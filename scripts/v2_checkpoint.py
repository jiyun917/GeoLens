"""V2 pipeline health checkpoint. Run this after Gemini finishes (Phase 1)
to verify:
  (1) Every replicate has 0 empty responses across all backends.
  (2) The new goal_completion 3-gate is firing — the Claude-style hallucinated
      completions on 3d_visualization would score 0 under the new rule.
  (3) Fallback rate is sane (0.7 threshold isn't tripping on every step, and
      isn't tripping never on the low-confidence step 2).
  (4) No 429 / RESOURCE_EXHAUSTED / [BENCH] EMPTY in the log.

Exit code 0 = safe to proceed with Phase 2 (other models).
Exit code 1 = stop, inspect, fix before proceeding.

Usage:
    .venv/Scripts/python.exe scripts/v2_checkpoint.py \\
        --tag unified2 --model gemini --log data/eval/results/unified2_gemini.log
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="Run tag (e.g. unified2)")
    ap.add_argument("--model", required=True, help="Model to check (e.g. gemini)")
    ap.add_argument("--log", default=None, help="Optional log file to scan")
    ap.add_argument("--expected-reps", type=int, default=5)
    args = ap.parse_args()

    problems = []
    pattern = f"data/eval/results/run_{args.model}_{args.tag}_r*_*.json"
    files = sorted(glob.glob(str(ROOT / pattern)))
    print(f"\n=== V2 CHECKPOINT: model={args.model} tag={args.tag} ===\n")
    print(f"Found {len(files)} replicate files")
    if len(files) != args.expected_reps:
        problems.append(
            f"expected {args.expected_reps} replicates, got {len(files)}"
        )

    # (1) empty response scan + goal check + fallback scan
    total_steps = 0
    empty_steps = 0
    r3dviz_hall_examples = []
    fallback_activations = 0
    fallback_eligible = 0
    for f in files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        rep = re.search(r"_r(\d+)_", Path(f).name).group(1)
        for scen in d.get("scenarios", []) or []:
            sid = scen.get("scenario_id")
            for bname, b in (scen.get("backends") or {}).items():
                if not b or "error" in b:
                    continue
                per_step = b.get("per_step") or []
                for ps in per_step:
                    total_steps += 1
                    if not (ps.get("response") or "").strip():
                        empty_steps += 1
                    if ps.get("route_method"):
                        fallback_eligible += 1
                        if ps.get("fallback_activated"):
                            fallback_activations += 1
                # For 3d_visualization, spot-check the completion gate.
                if sid == "opendtect__3d_visualization__01":
                    goal = b.get("goal_completion_rate")
                    final_step = per_step[-1] if per_step else {}
                    final_resp = (final_step.get("response") or "")[:80]
                    r3dviz_hall_examples.append(
                        (bname, rep, goal, final_resp)
                    )

    print(f"\n(1) Empty responses: {empty_steps}/{total_steps} "
          f"({100*empty_steps/max(total_steps,1):.1f}%)")
    if empty_steps > 0:
        problems.append(f"{empty_steps} empty responses detected")

    print(f"\n(2) 3d_visualization completion gate — goal_completion_rate "
          "per (backend, rep) (should be 0 unless the final response is "
          "grounded AND visual_state confirms goal, which it doesn't for "
          "this scenario):\n")
    for bname, rep, goal, resp in r3dviz_hall_examples:
        flag = "✓" if goal == 0.0 else "⚠ NONZERO"
        print(f"  {bname:<16} r{rep} goal={goal} {flag}  final={resp!r}")
    nonzero = [x for x in r3dviz_hall_examples if x[2] != 0.0]
    if nonzero:
        problems.append(
            f"{len(nonzero)} 3d_viz goal_completion nonzero (should all be 0)"
        )

    print(f"\n(3) Fallback activation rate: {fallback_activations}/"
          f"{fallback_eligible} routed steps "
          f"({100*fallback_activations/max(fallback_eligible,1):.1f}%)")
    if fallback_eligible == 0:
        problems.append("no routed steps recorded — telemetry not flowing")
    elif fallback_activations / max(fallback_eligible, 1) > 0.5:
        problems.append(
            f"fallback triggered on {100*fallback_activations/fallback_eligible:.0f}% "
            "of routed steps (>50% → suspect rerank tuning)"
        )

    # (4) log scan — pipeline errors
    if args.log and Path(args.log).exists():
        text = Path(args.log).read_text(encoding="utf-8", errors="replace")
        bad_patterns = [
            (r"\[BENCH\] EMPTY", "bench harness recorded empty response"),
            (r"\b429\b", "HTTP 429 rate limiting"),
            (r"RESOURCE_EXHAUSTED", "Gemini credit exhaustion"),
        ]
        print(f"\n(4) Log scan: {args.log}")
        for pat, label in bad_patterns:
            hits = re.findall(pat, text)
            print(f"  '{label}': {len(hits)} hits")
            if hits:
                problems.append(f"log has {len(hits)} × {label}")

        # (5) Flash auxiliary-call health — Phase 2 introduces a new path
        # (generator != Flash) for the first time. We verify Flash calls
        # (visual_state extraction + rerank) worked without silent failure.
        print(f"\n(5) Flash aux-call health (visual_state + rerank):")
        flash_patterns = [
            (r"Visual state recognition failed", "visual_state extraction hard failure"),
            (r"LLM rerank failed", "workflow rerank hard failure"),
            (r"visual_state transient", "visual_state transient (retried)"),
            (r"rerank transient", "rerank transient (retried)"),
            (r"CLIP match failed", "CLIP matcher failure"),
            (r"\[GUIDE\] visual_state: ''", "empty visual_state emitted"),
        ]
        for pat, label in flash_patterns:
            hits = re.findall(pat, text)
            print(f"  '{label}': {len(hits)} hits")
            # Transients are logged but recovered — informational, not fatal.
            if "transient" not in label and hits:
                problems.append(f"log has {len(hits)} × {label}")
        # visual_state emission count — should roughly equal (routed steps)
        vs_emissions = len(re.findall(r"\[GUIDE\] visual_state:", text))
        print(f"  visual_state emissions total: {vs_emissions}")
        if vs_emissions == 0 and any(m in args.log for m in ("phase2", "claude", "gpt", "qwen")):
            problems.append("no visual_state emissions — routed backends may have degraded to no_rag")

    print("\n" + "=" * 60)
    if problems:
        print("STATUS: FAIL — do NOT proceed to Phase 2")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    else:
        print("STATUS: PASS — safe to proceed with Phase 2")
        sys.exit(0)


if __name__ == "__main__":
    main()
