# -*- coding: utf-8 -*-
"""Scorer v4 sensitivity on the archived v3 confirmatory results (no API calls).

Re-scores every run_<model>_{v3,v3_qgis}_r*_*.json response with the v3 scorer and with the v4
scorer (ellipsis normalisation + numeric goal values never hallucinated) and reports, per
(set, model, backend): step_acc and hall under v3 → v4 with the delta, plus the primary
comparisons (full_system vs vanilla_budget / vanilla_vector) under v4. The signed v3 verdict is
NOT changed by this file; it documents how much of the QGIS result was scorer notation.

Usage: .venv/Scripts/python.exe scripts/rescore_scorer_v4_sensitivity.py
"""
from __future__ import annotations
import glob, json, os, re, statistics as st, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from api.services import evaluation as ev  # noqa: E402

MODELS = ["gemini", "claude", "gpt"]
BACKENDS = ["no_rag", "vanilla_vector", "vanilla_budget", "graph_only", "vision_only", "state_path", "full_system"]


def load_scenarios():
    scen = {}
    for f in glob.glob(str(ROOT / "data/eval/scenarios/*.json")):
        d = json.load(open(f, encoding="utf-8"))
        if d.get("scenario_id") and d["scenario_id"] != "EXAMPLE_PLACEHOLDER":
            scen[d["scenario_id"]] = d
    return scen


def score(d, scen, version):
    ev.SCORER_VERSION = version
    out = defaultdict(lambda: defaultdict(list))
    for sc in d["scenarios"]:
        steps = scen[sc["scenario_id"]]["steps"]; goal = scen[sc["scenario_id"]].get("goal", "")
        for b, bb in sc["backends"].items():
            if not bb or "per_step" not in bb:
                continue
            m = h = 0; n = len(bb["per_step"])
            for ps in bb["per_step"]:
                stp = steps[ps["step_index"]]; vis = (stp.get("visual_state_gt") or {}).get("visible_elements", [])
                m += ev.step_match(ps["response"], stp)
                h += bool(ev.hallucinated_elements(ps["response"], vis, step_gt=stp, goal=goal))
            out[b]["step_acc"].append(m / n); out[b]["hall"].append(h / n)
    return {b: {k: st.fmean(v) for k, v in mm.items()} for b, mm in out.items()}


def main():
    scen = load_scenarios()
    L = ["# Scorer v4 sensitivity on the v3 confirmatory results (re-score only; the signed verdict is unchanged)", "",
         "v4 = v3 + '…'→'...' before step matching + numeric goal values never counted as hallucinated elements. Values = mean over 10 replicates of the replicate-level (scenario-mean) metric.", ""]
    for tag, label in (("v3_qgis", "QGIS test set"), ("v3", "OpendTect dev set")):
        L += [f"## {label} (tag {tag})", "", "| model | backend | step_acc v3 | step_acc v4 | Δ | hall v3 | hall v4 | Δ |", "|---|---|---|---|---|---|---|---|"]
        per = {}
        for model in MODELS:
            files = sorted(glob.glob(str(ROOT / f"data/eval/results/run_{model}_{tag}_r*_*.json")))
            acc3 = defaultdict(list); acc4 = defaultdict(list); h3 = defaultdict(list); h4 = defaultdict(list)
            for f in files:
                d = json.load(open(f, encoding="utf-8"))
                r3 = score(d, scen, "v3"); r4 = score(d, scen, "v4")
                for b in BACKENDS:
                    if b in r3:
                        acc3[b].append(r3[b]["step_acc"]); acc4[b].append(r4[b]["step_acc"]); h3[b].append(r3[b]["hall"]); h4[b].append(r4[b]["hall"])
            for b in BACKENDS:
                if acc3[b]:
                    a3, a4, hh3, hh4 = st.fmean(acc3[b]), st.fmean(acc4[b]), st.fmean(h3[b]), st.fmean(h4[b])
                    per[(model, b)] = (a4, hh4)
                    L.append(f"| {model} | {b} | {a3:.3f} | {a4:.3f} | {a4 - a3:+.3f} | {hh3:.3f} | {hh4:.3f} | {hh4 - hh3:+.3f} |")
        L += ["", f"Primary comparisons under v4 ({label}): " + "; ".join(
            f"{m}: full−vb step {per[(m, 'full_system')][0] - per[(m, 'vanilla_budget')][0]:+.3f} / hall {per[(m, 'full_system')][1] - per[(m, 'vanilla_budget')][1]:+.3f}, full−vv step {per[(m, 'full_system')][0] - per[(m, 'vanilla_vector')][0]:+.3f} / hall {per[(m, 'full_system')][1] - per[(m, 'vanilla_vector')][1]:+.3f}"
            for m in MODELS if (m, "full_system") in per), ""]
    ev.SCORER_VERSION = os.environ.get("GEOLENS_SCORER", "v3").lower()
    md = "\n".join(L) + "\n"
    out = ROOT / "data/eval/results/rescore_scorer_v4_sensitivity.md"
    out.write_text(md, encoding="utf-8"); print(md); print("saved:", out)


if __name__ == "__main__":
    main()
