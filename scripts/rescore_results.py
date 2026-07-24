"""Re-score every existing run_*_r*_*.json using the CURRENT step_match /
scoring logic, without hitting the LLM again.

For each per_step row we already stored:
  - response, matched, hallucinated, looped, ... etc.

We recompute `matched` and `hallucinated` under the current rules and
overwrite the file's per_step + aggregate fields in place. The raw
response text is unchanged, so if the scoring logic changes again in
the future we can re-run this and re-score exactly the same responses.

The idea: no_rag / RAG variants alike suffered from over-permissive
allowed_alternatives that accepted premature '완료' regardless of the
screen state. With the tightened step_match rule the numbers change,
and this is where those new numbers come from — no bench rerun needed.

Usage:
    .venv/Scripts/python.exe scripts/rescore_results.py [--dry-run]
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _load_scenario(scenario_id: str) -> dict | None:
    for sub in ("", "excluded/"):
        p = ROOT / "data" / "eval" / "scenarios" / sub / f"{scenario_id}.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return None
    return None


def rescore_file(path: Path, dry_run: bool = False) -> dict:
    from api.services.evaluation import (
        step_match, hallucinated_elements, has_done_sentinel,
        _normalize_instruction, completion_visually_grounded,
        _visual_state_indicates_goal_reached,
    )

    d = json.loads(path.read_text(encoding="utf-8"))
    changes = {"file": path.name, "scenarios": []}

    scenarios = d.get("scenarios") or []
    for scen_row in scenarios:
        sid = scen_row.get("scenario_id")
        scen_def = _load_scenario(sid)
        if not scen_def:
            continue
        step_gts = {s["step_index"]: s for s in scen_def.get("steps", [])}

        for bname, bmetrics in (scen_row.get("backends") or {}).items():
            if not isinstance(bmetrics, dict) or "per_step" not in bmetrics:
                continue
            per = bmetrics["per_step"]
            # Recompute per-step matched + hallucinated
            prior_norms: list[str] = []
            hall_changes = matched_changes = 0
            for i, ps in enumerate(per):
                step_gt = step_gts.get(ps.get("step_index"))
                if not step_gt:
                    continue
                resp = ps.get("response", "") or ""
                new_matched = step_match(resp, step_gt)
                new_hall = bool(hallucinated_elements(
                    resp, (step_gt.get("visual_state_gt") or {}).get("visible_elements", [])
                ))
                new_looped = bool(
                    prior_norms and
                    _normalize_instruction(resp) == prior_norms[-1]
                )
                prior_norms.append(_normalize_instruction(resp))

                if ps.get("matched") != new_matched:
                    matched_changes += 1
                # Compare truthiness — archived files store hallucinated
                # as a list ([]) while the new schema uses bool. Casting
                # both to bool avoids a spurious "change" that's really
                # just a type migration.
                if bool(ps.get("hallucinated")) != bool(new_hall):
                    hall_changes += 1

                ps["matched"] = new_matched
                ps["hallucinated"] = new_hall
                ps["looped"] = new_looped

            n = max(1, len(per))
            trap_steps = [s for s in per if s.get("is_trap")]
            recovery_steps = [s for s in per if s.get("is_recovery")]
            hall_rate = sum(1 for s in per if s.get("hallucinated")) / n
            loop_rate = sum(1 for s in per if s.get("looped")) / n
            step_acc = sum(1 for s in per if s.get("matched")) / n

            # Goal completion — apply the three-gate check matching the
            # updated ScenarioEvaluator.evaluate_backend logic:
            #   (i)   response has a done sentinel
            #   (ii)  every UI element the response claims is grounded in
            #         the final step's visual_state (blocks the r2/r4/r5
            #         "In-line/Cross-line/Z-slice 모두 로드됨" hallucination)
            #   (iii) the final visual_state actively indicates goal-reached
            #         (blocks the r1 bare-sentinel with no screen evidence)
            completion = scen_def.get("completion") or {}
            done_ok = 0.0
            old_done_ok = float(bmetrics.get("goal_completion_rate") or 0.0)
            completion_diag = None
            if completion.get("expected_done_sentinel") and per:
                final_step = per[-1]
                final_response = final_step.get("response", "") or ""
                final_gt = scen_def.get("steps", [])[-1] if scen_def.get("steps") else None
                sentinel_ok = has_done_sentinel(final_response)
                grounded, halls = (
                    completion_visually_grounded(final_response, final_gt)
                    if final_gt else (True, [])
                )
                visual_ok = (
                    _visual_state_indicates_goal_reached(final_gt)
                    if final_gt else False
                )
                if sentinel_ok and grounded and visual_ok:
                    done_ok = 1.0
                completion_diag = {
                    "sentinel": sentinel_ok,
                    "grounded": grounded,
                    "visual_confirms_goal": visual_ok,
                    "hallucinations": halls,
                    "response_preview": final_response[:120],
                }

            new_metrics = {
                "step_accuracy": step_acc,
                "hallucination_rate": hall_rate,
                "faithfulness": round(1.0 - hall_rate, 4),
                "dwell_loop_rate": loop_rate,
                "loop_rate": loop_rate,
                "trap_pass_rate": (sum(1 for s in trap_steps if s.get("matched")) / len(trap_steps)) if trap_steps else None,
                "recovery_rate": (sum(1 for s in recovery_steps if s.get("matched")) / len(recovery_steps)) if recovery_steps else None,
                "goal_completion_rate": done_ok,
            }
            for k, v in new_metrics.items():
                bmetrics[k] = v

            changes["scenarios"].append({
                "scenario_id": sid,
                "backend": bname,
                "matched_changed": matched_changes,
                "hallucinated_changed": hall_changes,
                "new_step_acc": step_acc,
                "old_goal_comp": old_done_ok,
                "new_goal_comp": done_ok,
                "goal_comp_delta": done_ok - old_done_ok,
                "completion_diag": completion_diag,
            })

    # Recompute aggregate at the run level too
    for bname in {b for scen in scenarios for b in (scen.get("backends") or {}).keys()}:
        rows = [
            scen["backends"][bname]
            for scen in scenarios
            if bname in (scen.get("backends") or {})
            and "error" not in (scen["backends"][bname] or {})
        ]
        if not rows:
            continue
        agg_keys = ["step_accuracy", "hallucination_rate", "faithfulness",
                    "dwell_loop_rate", "loop_rate", "trap_pass_rate",
                    "recovery_rate", "goal_completion_rate",
                    "mean_latency_sec", "mean_cost_usd", "total_cost_usd",
                    "total_input_tokens", "total_output_tokens"]
        agg = d.setdefault("aggregate", {}).setdefault(bname, {})
        agg["n_scenarios"] = len(rows)
        for k in agg_keys:
            vals = [r[k] for r in rows if r.get(k) is not None]
            agg[k] = (sum(vals) / len(vals)) if vals else None

    if not dry_run:
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return changes


def _print_goal_completion_comparison(all_changes: list[dict]) -> None:
    """Old vs new goal_completion, aggregated per (model, backend) with n
    replicate observations. Prints a markdown table for the paper Methods
    section.

    We derive model from the filename tag between 'run_' and '_r'."""
    from collections import defaultdict
    import re as _re

    # (model, backend, scenario) -> list of (old, new)
    bucket: dict = defaultdict(list)
    for entry in all_changes:
        fn = entry["file"]
        m = _re.match(r"run_([^_]+(?:_[^_]+)*?)_r\d+_", fn)
        model = m.group(1) if m else fn.replace("run_", "").split("_")[0]
        for sc in entry["scenarios"]:
            bucket[(model, sc["backend"], sc["scenario_id"])].append(
                (sc["old_goal_comp"], sc["new_goal_comp"])
            )

    # (model, backend) → mean_old, mean_new, delta, n
    per_mb: dict = defaultdict(lambda: {"old_sum": 0.0, "new_sum": 0.0, "n": 0})
    for (model, backend, scen), pairs in bucket.items():
        for old, new in pairs:
            per_mb[(model, backend)]["old_sum"] += old
            per_mb[(model, backend)]["new_sum"] += new
            per_mb[(model, backend)]["n"] += 1

    print("\n" + "=" * 70)
    print("Goal-completion under OLD scoring (sentinel only) vs NEW three-gate")
    print("=" * 70)
    print()
    print("| model | backend | n | old_goal | new_goal | Δ |")
    print("|---|---|---|---|---|---|")
    for (model, backend), agg in sorted(per_mb.items()):
        if agg["n"] == 0:
            continue
        old_m = agg["old_sum"] / agg["n"]
        new_m = agg["new_sum"] / agg["n"]
        d = new_m - old_m
        print(f"| {model} | {backend} | {agg['n']} | "
              f"{old_m:.3f} | {new_m:.3f} | {d:+.3f} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Report changes without writing files")
    args = ap.parse_args()

    files = sorted((ROOT / "data" / "eval" / "results").glob("run_*_r*_*.json"))
    print(f"Rescoring {len(files)} files{' (dry-run)' if args.dry_run else ''}")
    total_matched = total_hall = total_goal_flips = 0
    all_changes: list = []
    for f in files:
        c = rescore_file(f, dry_run=args.dry_run)
        all_changes.append(c)
        for sc in c["scenarios"]:
            goal_flipped = abs(sc.get("goal_comp_delta", 0.0)) > 1e-9
            if sc["matched_changed"] or sc["hallucinated_changed"] or goal_flipped:
                print(f"  {f.name} :: {sc['scenario_id']} :: {sc['backend']}  "
                      f"matched_Δ={sc['matched_changed']}  hall_Δ={sc['hallucinated_changed']}  "
                      f"goal {sc['old_goal_comp']:.2f}→{sc['new_goal_comp']:.2f}"
                      f"  (Δ={sc.get('goal_comp_delta', 0.0):+.2f})")
                total_matched += sc["matched_changed"]
                total_hall += sc["hallucinated_changed"]
                if goal_flipped:
                    total_goal_flips += 1
    print(f"\nTotal matched flips: {total_matched}, hallucinated flips: {total_hall}, "
          f"goal_completion flips: {total_goal_flips}")

    _print_goal_completion_comparison(all_changes)


if __name__ == "__main__":
    main()
