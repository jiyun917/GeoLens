# -*- coding: utf-8 -*-
"""Exploratory sensitivity analysis (offline, no API; designed 2026-10-14 after the study-5 results were seen):
re-score every test-set response with a STRICT criterion — a step is correct only if all expected_action_keywords
occur in the response (case-insensitive; the two version aliases decided before the run, 'Input layer' for
'Reference layer' and 'User-defined' for 'User Defined', are allowed) or the response is the bare completion
sentinel at a goal-reached step. The pre-registered scorer additionally accepts the alternatives listed in
expected_action_text_pattern / allowed_alternatives; this analysis removes them to bound how much that leniency
contributes. Writes data/eval/results/rescore_strict_study5.md.
Usage: .venv/Scripts/python.exe scripts/rescore_strict_study5.py
"""
from __future__ import annotations
import glob, json, os, re, statistics, sys, collections
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_stratified import stratified_perm, perm_p  # noqa: E402
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "data" / "eval" / "results"
MODELS = ["gemini", "claude", "gpt"]
ALIAS = {"Reference layer": ["Reference layer", "Input layer"], "User Defined": ["User Defined", "User-defined"]}
SENT = re.compile(r"(?i)^\s*(완료|done)\.?\s*$")
GOAL_MARKERS = ("goal reached", "목표 도달", "완료", "달성", "goal state", "completed", "terminal state")


def load_gt():
    gts = {}
    for f in glob.glob(str(ROOT / "data/eval/scenarios/.study5_test_*/*.json")):
        sc = json.load(open(f, encoding="utf-8")); gts[sc["scenario_id"]] = sc
    return gts


def goal_reached(st):
    vs = st.get("visual_state_gt") or {}
    hay = (str(vs.get("data_state", "")) + " " + str(vs.get("current_action", ""))).lower()
    return any(m in hay for m in GOAL_MARKERS)


def strict(resp, st):
    t = (resp or "").strip()
    if SENT.match(t):
        return goal_reached(st)
    low = t.lower()
    for k in st["expected_action_keywords"]:
        if not any(a.lower() in low for a in ALIAS.get(k, [k])):
            return False
    return True


def load(pattern, backends, gts):
    d = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
    loose = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
    for f in sorted(glob.glob(pattern)):
        m = re.match(r"run_([a-z]+)_study5x?_(opendtect|qgis)_r(\d+)_", os.path.basename(f))
        if not m or m.group(1) not in MODELS:
            continue
        run = json.load(open(f, encoding="utf-8"))
        for sc in run["scenarios"]:
            for b, bd in sc["backends"].items():
                if b not in backends:
                    continue
                acc = [strict(s["response"], gts[sc["scenario_id"]]["steps"][s["step_index"]]) for s in bd["per_step"]]
                d[m.group(1)][int(m.group(3))][b].append(sum(acc) / len(acc))
                loose[m.group(1)][int(m.group(3))][b].append(bd["step_accuracy"])
    return d, loose


def reps(d, m, b):
    return [statistics.mean(d[m][r][b]) for r in sorted(d[m])]


def main():
    gts = load_gt()
    d5, l5 = load(str(RES / "run_*_study5_*_r*_*.json"), {"no_rag", "vanilla_budget", "vanilla_vector", "full_system"}, gts)
    dx, lx = load(str(RES / "run_*_study5x_*_r*_*.json"), {"linked_chunks"}, gts)
    L = ["# Strict re-score of the study-5 test set (exploratory sensitivity analysis, outside the pre-registration)\n",
         "Criterion: all expected_action_keywords present (version aliases 'Input layer'/'User-defined' allowed) or bare completion sentinel at a goal-reached step; "
         "pattern alternatives and allowed_alternatives NOT used. Replicate = mean over the 3 scenarios, n = 10.\n",
         "## Step accuracy, strict (pre-registered scorer in parentheses)\n",
         "| model | no_rag | vanilla_budget | vanilla_vector | linked_chunks (5x) | full_system |", "|---|---|---|---|---|---|"]
    for m in MODELS:
        cells = []
        for b, dd, ll in (("no_rag", d5, l5), ("vanilla_budget", d5, l5), ("vanilla_vector", d5, l5), ("linked_chunks", dx, lx), ("full_system", d5, l5)):
            s, lo = reps(dd, m, b), reps(ll, m, b)
            cells.append(f"{statistics.mean(s):.3f} ± {statistics.pstdev(s):.3f} ({statistics.mean(lo):.3f})")
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("\n## Comparisons under the strict criterion (stratified permutation, 10,000, seed 42)\n")
    for A, dA, B, dB in (("full_system", d5, "vanilla_budget", d5), ("full_system", d5, "vanilla_vector", d5), ("full_system", d5, "linked_chunks", dx), ("linked_chunks", dx, "vanilla_budget", d5)):
        groups, rows = {}, []
        for m in MODELS:
            a, b = reps(dA, m, A), reps(dB, m, B); groups[m] = (a, b); _, pm = perm_p(a, b); rows.append((m, statistics.mean(a) - statistics.mean(b), pm))
        obs, p = stratified_perm(groups)
        L.append(f"- {A} vs {B}: " + "; ".join(f"{r[0]} Δ {r[1]:+.3f} (p {r[2]:.4f})" for r in rows) + f" → direction {sum(r[1] > 0 for r in rows)}/3, stratified Δ {obs:+.4f}, p {p:.4f}")
    # where the two criteria disagree (full_system and vanilla_budget)
    L.append("\n## Steps scored correct by the pre-registered scorer but not by the strict criterion (count / 30 responses)\n")
    L.append("| backend | scenario | step | keyword | loose-only |"); L.append("|---|---|---|---|---|")
    for b in ("full_system", "vanilla_budget", "vanilla_vector", "no_rag"):
        drop = collections.Counter()
        for f in sorted(glob.glob(str(RES / "run_*_study5_*_r*_*.json"))):
            run = json.load(open(f, encoding="utf-8"))
            for sc in run["scenarios"]:
                for s in sc["backends"][b]["per_step"]:
                    st = gts[sc["scenario_id"]]["steps"][s["step_index"]]
                    if s["matched"] and not strict(s["response"], st):
                        drop[(sc["scenario_id"], s["step_index"], st["expected_action_keywords"][0])] += 1
        for k in sorted(drop):
            L.append(f"| {b} | {k[0]} | s{k[1]} | {k[2]} | {drop[k]} |")
    md = "\n".join(L) + "\n"
    (RES / "rescore_strict_study5.md").write_text(md, encoding="utf-8"); print(md); print("saved:", RES / "rescore_strict_study5.md")


if __name__ == "__main__":
    main()
