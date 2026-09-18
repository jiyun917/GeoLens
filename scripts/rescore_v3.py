"""Re-score archived bench logs with the v2 and v3 scorers (no API calls).

Produces the per-cell table the v3 pre-registration needs: how much of
the step-accuracy / hallucination change is attributable to (a) the
ASCII-boundary fix, (b) the quote-independent hallucination extractor,
(c) dropping unclosed <think> blocks — before any new run is made.

Usage:
    .venv/Scripts/python.exe scripts/rescore_v3.py --tag unified4 [--out data/eval/results/rescore_v3_unified4.md]
    .venv/Scripts/python.exe scripts/rescore_v3.py --glob "run_gemini_longctx_r*_20260807T18*.json" --label longctx
    .venv/Scripts/python.exe scripts/rescore_v3.py --glob "run_gemini_qgis_pilot_r*_20260813T*.json" --label qgis_pilot
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from api.services.evaluation import (  # noqa: E402
    step_match_v2, step_match_v3, hallucinated_elements_v2, hallucinated_elements_v3,
    _normalize_instruction,
)
from api.services.bench_backends import _strip_thinking  # noqa: E402

MODELS = [m.strip() for m in os.environ.get("BENCH_MODELS", "gemini,claude,gpt").split(",") if m.strip()]  # v3: Qwen excluded (VL serving unavailable); set BENCH_MODELS=gemini,claude,gpt,qwen for unified2/3/4 tags


def load_scenarios():
    scen = {}
    for f in glob.glob(str(ROOT / "data/eval/scenarios/*.json")):
        d = json.load(open(f, encoding="utf-8"))
        if d.get("scenario_id") and d["scenario_id"] != "EXAMPLE_PLACEHOLDER":
            scen[d["scenario_id"]] = d
    return scen


def score_run(d, scen, variant):
    """variant: v2 | v3 | v3_think (v3 + unclosed <think> dropped).
    Returns {backend: {metric: replicate-level value (mean over scenarios)}}."""
    out = defaultdict(lambda: defaultdict(list))
    for sc in d["scenarios"]:
        steps = scen[sc["scenario_id"]]["steps"]
        for b, bb in sc["backends"].items():
            if not bb or "per_step" not in bb:
                continue
            resp = [ps["response"] for ps in bb["per_step"]]
            if variant == "v3_think":
                resp = [_strip_thinking(r) for r in resp]
            m = h = l = 0
            n = len(resp)
            for i, ps in enumerate(bb["per_step"]):
                stp = steps[ps["step_index"]]
                vis = (stp.get("visual_state_gt") or {}).get("visible_elements", [])
                if variant == "v2":
                    mt = step_match_v2(resp[i], stp); hl = bool(hallucinated_elements_v2(resp[i], vis))
                else:
                    mt = step_match_v3(resp[i], stp)
                    hl = bool(hallucinated_elements_v3(resp[i], vis, step_gt=stp, goal=scen[sc["scenario_id"]].get("goal", "")))
                lp = bool(i > 0 and resp[i] and _normalize_instruction(resp[i]) == _normalize_instruction(resp[i - 1]))
                m += mt; h += hl; l += lp
            out[b]["step_acc"].append(m / n); out[b]["hall"].append(h / n); out[b]["loop"].append(l / n)
    return {b: {k: st.fmean(v) for k, v in mm.items()} for b, mm in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default=None, help="e.g. unified4 → run_<model>_<tag>_r*_*.json")
    ap.add_argument("--glob", default=None, help="explicit glob under data/eval/results")
    ap.add_argument("--label", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    scen = load_scenarios()
    if args.tag:
        files = sorted(glob.glob(str(ROOT / f"data/eval/results/run_*_{args.tag}_r*_*.json")))
        label = args.label or args.tag
    else:
        files = sorted(glob.glob(str(ROOT / "data/eval/results" / args.glob)))
        label = args.label or "custom"
    cells = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # (model,backend) -> variant -> metric -> reps
    stored = defaultdict(lambda: defaultdict(list))
    mism = 0; total = 0
    for f in files:
        m = re.match(r"run_([a-z]+)_", os.path.basename(f)); model = m.group(1) if m else "?"
        d = json.load(open(f, encoding="utf-8"))
        # v2 reproduction check against stored matched/hallucinated
        for sc in d["scenarios"]:
            steps = scen[sc["scenario_id"]]["steps"]
            for b, bb in sc["backends"].items():
                if not bb or "per_step" not in bb:
                    continue
                for ps in bb["per_step"]:
                    stp = steps[ps["step_index"]]
                    vis = (stp.get("visual_state_gt") or {}).get("visible_elements", [])
                    total += 1
                    if step_match_v2(ps["response"], stp) != bool(ps["matched"]) or \
                       bool(hallucinated_elements_v2(ps["response"], vis)) != bool(ps["hallucinated"]):
                        mism += 1
        for variant in ("v2", "v3", "v3_think"):
            r = score_run(d, scen, variant)
            for b, mm in r.items():
                for k, v in mm.items():
                    cells[(model, b)][variant][k].append(v)
    lines = [f"# Re-score of archived logs with scorer v2 / v3 — {label}", "",
             f"Files: {len(files)}. v2 re-implementation vs stored matched/hallucinated: {mism} mismatches / {total} steps.",
             "", "v3 = ASCII word boundary in step patterns + quote-independent hallucination extractor. "
             "v3_think = v3 + unclosed <think> blocks dropped (affects Qwen only). "
             "Values are macro means over replicates (%), Δ = variant − v2.", "",
             "| model | backend | n | StepAcc v2 | v3 | Δ | v3_think | Δ | Hall v2 | v3 | Δ | v3_think | Δ | Loop v2 | v3_think |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for (model, b), vv in sorted(cells.items(), key=lambda t: (MODELS.index(t[0][0]) if t[0][0] in MODELS else 9, t[0][1])):
        def M(var, k):
            v = vv[var][k]; return 100 * st.fmean(v) if v else float("nan")
        n = len(vv["v2"]["step_acc"])
        lines.append(f"| {model} | {b} | {n} | {M('v2','step_acc'):.1f} | {M('v3','step_acc'):.1f} | {M('v3','step_acc')-M('v2','step_acc'):+.1f} | "
                     f"{M('v3_think','step_acc'):.1f} | {M('v3_think','step_acc')-M('v2','step_acc'):+.1f} | "
                     f"{M('v2','hall'):.1f} | {M('v3','hall'):.1f} | {M('v3','hall')-M('v2','hall'):+.1f} | {M('v3_think','hall'):.1f} | {M('v3_think','hall')-M('v2','hall'):+.1f} | "
                     f"{M('v2','loop'):.1f} | {M('v3_think','loop'):.1f} |")
    # direction full vs vanilla per variant
    lines += ["", "## full_system vs vanilla_vector direction (step_acc / hall)", "",
              "| model | v2 | v3 | v3_think |", "|---|---|---|---|"]
    for model in MODELS:
        if (model, "full_system") not in cells:
            continue
        row = []
        for var in ("v2", "v3", "v3_think"):
            fs = 100 * st.fmean(cells[(model, "full_system")][var]["step_acc"]); va = 100 * st.fmean(cells[(model, "vanilla_vector")][var]["step_acc"])
            fh = 100 * st.fmean(cells[(model, "full_system")][var]["hall"]); vh = 100 * st.fmean(cells[(model, "vanilla_vector")][var]["hall"])
            row.append(f"acc {fs:.1f} vs {va:.1f} ({'full' if fs > va else 'tie' if fs == va else 'vanilla'}); hall {fh:.1f} vs {vh:.1f} ({'full' if fh < vh else 'tie' if fh == vh else 'vanilla'})")
        lines.append(f"| {model} | " + " | ".join(row) + " |")
    md = "\n".join(lines) + "\n"
    out = args.out or str(ROOT / f"data/eval/results/rescore_v3_{label}.md")
    Path(out).write_text(md, encoding="utf-8")
    print(md)
    print("saved:", out)


if __name__ == "__main__":
    main()
