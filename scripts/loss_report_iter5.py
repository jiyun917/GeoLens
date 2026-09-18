"""Iteration-5 dev bench report (context assembly v4; Gemini x2 only — Claude cut off by Gemini credit depletion, GPT not started) (user items 1–3, 2026-09-18) over the four bench JSONs
(Gemini r0/r1, Claude r0, GPT r0):
  A. goal-state early firings (attribute s5/s6): full_system response, whether it is the
     completion sentinel, and the step match — every bench;
  B. steps routed correctly but full_system wrong: [Current Step] / [Possible Next Steps]
     text as given to the generator, the scenario's expected action, the response, and
     whether the expected action is the current node's or the next node's action
     (keyword overlap of the expected keywords with the current node description vs the
     outgoing edge instruction);
  C. loss classification over all benches (routing / context / generation / wording) and
     full vs the two vanillas step accuracy per model.
Run from the worktree.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

SCEN_WF = {"opendtect__survey_setup__01": "survey_setup", "opendtect__3d_visualization__01": "d3_visualization",
           "opendtect__attribute_computation__01": "seismic_attribute"}
TARGET = {"opendtect__survey_setup__01": ["1.2.2a"], "opendtect__3d_visualization__01": ["1.3.1a", "1.3.1 "], "opendtect__attribute_computation__01": ["1.5.1a"]}
SENT = re.compile(r"^\s*(완료|Done)\.?\s*$", re.I)
WORDING = re.compile(r"더하기|플러스|\+|아이콘", re.I)


def sections(block):
    return [m.strip() for m in re.findall(r"Section: ([^\],\n]+)", block or "")]


def main():
    from api.services.workflow_graph import get_workflow_graph
    graph = get_workflow_graph()
    files = sorted(glob.glob("data/eval/results/dev_iter5_v3_*_r*.json"))
    scen_json = {sid: json.load(open(f"data/eval/scenarios/{sid}.json", encoding="utf-8")) for sid in SCEN_WF}
    out = ["# Iteration-5 dev bench report (context assembly v4; Gemini x2 only — Claude cut off by Gemini credit depletion, GPT not started)", "", f"Benches: {', '.join(os.path.basename(f) for f in files)}", ""]
    # ── C1: step accuracy per model ──
    acc = defaultdict(lambda: defaultdict(list))   # model -> backend -> [scenario acc per rep]
    A_rows, B_rows = [], []
    losses = defaultdict(int)
    loss_rows = []
    for f in files:
        run = json.load(open(f, encoding="utf-8"))
        name = os.path.basename(f)
        model = next(m for m in ("gemini", "claude", "gpt") if m in name)
        rep = re.search(r"_r(\d+)\.json", name).group(1)
        for sc in run["scenarios"]:
            sid = sc["scenario_id"]
            for b, m in sc["backends"].items():
                acc[model][b].append(float(m.get("step_accuracy") or 0.0))
            fs = sc["backends"]["full_system"]["per_step"]
            vv = sc["backends"]["vanilla_vector"]["per_step"]
            vb = sc["backends"]["vanilla_budget"]["per_step"]
            for ps in fs:
                si = ps["step_index"]
                st = scen_json[sid]["steps"][si]
                exp_node = st.get("expected_workflow_node")
                picked = ps.get("picked_node_id")
                node = graph.get_node(picked) if picked else None
                route_ok = (picked == exp_node) if exp_node else (bool(node) and node.get("workflow_id") == SCEN_WF[sid])
                resp = ps.get("response") or ""
                # A: early goal-state firings
                if ps.get("goal_state_node") and sid == "opendtect__attribute_computation__01" and si in (5, 6):
                    A_rows.append((model, rep, si, ps["goal_state_node"], bool(SENT.match(resp)), ps["matched"], resp[:100].replace("\n", " ")))
                if not ps["matched"]:
                    if not route_ok or ps.get("fallback_activated"):
                        cls = "routing"
                    elif not any(s.startswith(t) for s in sections(ps.get("context_block")) for t in TARGET[sid]):
                        cls = "context"
                    elif WORDING.search(resp) and any(k.lower() in ("survey", "add", "new", "create") for k in st.get("expected_action_keywords", [])):
                        cls = "wording"
                    else:
                        cls = "generation"
                    losses[(model, cls)] += 1
                    loss_rows.append((model, rep, sid.replace("opendtect__", ""), si, cls, picked, resp[:80].replace("\n", " "), vv[si]["matched"], vb[si]["matched"]))
                    if route_ok and not ps.get("fallback_activated"):
                        ctx = ps.get("context_block") or ""
                        cur = re.search(r"\[Current Step\][^\n]*\n(?:Description: [^\n]*)?", ctx)
                        nxt = re.search(r"\[Possible Next Steps\]\n((?:  - [^\n]*\n?)+)", ctx)
                        kws = [k.lower() for k in st.get("expected_action_keywords", [])]
                        cur_desc = (node.get("description") or "").lower() if node else ""
                        edges = " ".join((e.get("edge_instruction") or "") for e in graph.get_next_steps(picked)).lower() if picked else ""
                        cur_hit = sum(1 for k in kws if k in cur_desc); nxt_hit = sum(1 for k in kws if k in edges)
                        which = "next node's action" if nxt_hit > cur_hit else ("current node's action" if cur_hit > nxt_hit else "ambiguous")
                        B_rows.append((model, rep, sid.replace("opendtect__", ""), si, picked, cur.group(0)[:260] if cur else "—", (nxt.group(1)[:300] if nxt else "—"),
                                       st.get("expected_action_text_pattern", ""), st.get("expected_action_keywords", []), resp[:120].replace("\n", " "), which, cur_hit, nxt_hit))
    out += ["## C. step accuracy per model (scenario-avg, mean over reps)", "", "| model | reps | full_system | vanilla_vector | vanilla_budget | no_rag | full > vv | full > vb |", "|---|---|---|---|---|---|---|---|"]
    for model in ("gemini", "claude", "gpt"):
        if model not in acc:
            continue
        a = {b: (sum(v) / len(v) if v else float("nan")) for b, v in acc[model].items()}
        n = len(acc[model].get("full_system", [])) // 3
        out.append(f"| {model} | {n} | {a.get('full_system', float('nan')):.3f} | {a.get('vanilla_vector', float('nan')):.3f} | {a.get('vanilla_budget', float('nan')):.3f} | {a.get('no_rag', float('nan')):.3f} | "
                   f"{'✓' if a.get('full_system', 0) > a.get('vanilla_vector', 0) else ('=' if a.get('full_system', 0) == a.get('vanilla_vector', 0) else '✗')} | "
                   f"{'✓' if a.get('full_system', 0) > a.get('vanilla_budget', 0) else ('=' if a.get('full_system', 0) == a.get('vanilla_budget', 0) else '✗')} |")
    out += ["", "## C. full_system losses classified (routing / context / generation / wording)", "", "| model | routing | context | generation | wording |", "|---|---|---|---|---|"]
    for model in ("gemini", "claude", "gpt"):
        out.append(f"| {model} | {losses[(model, 'routing')]} | {losses[(model, 'context')]} | {losses[(model, 'generation')]} | {losses[(model, 'wording')]} |")
    out += ["", "| model | rep | scenario | step | class | routed to | response | vv | vb |", "|---|---|---|---|---|---|---|---|---|"]
    for r in loss_rows:
        out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5] or '—'} | `{r[6]}` | {'✓' if r[7] else '✗'} | {'✓' if r[8] else '✗'} |")
    out += ["", "## A. goal-state block fired early (attribute s5/s6): full_system response", "", "| model | rep | step | fired node | answered 완료? | step match | response |", "|---|---|---|---|---|---|---|"]
    for r in A_rows:
        out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {'YES' if r[4] else 'no'} | {'✓' if r[5] else '✗'} | `{r[6]}` |")
    out.append("")
    out.append(f"Early-completion answers: **{sum(1 for r in A_rows if r[4])}** of {len(A_rows)} early firings.")
    out += ["", "## B. routed correctly but full_system wrong — context vs expected action", ""]
    for r in B_rows:
        out += [f"### {r[0]} rep {r[1]} · {r[2]} step {r[3]} · routed {r[4]}", "",
                "[Current Step] as given:", "```", r[5], "```", "[Possible Next Steps] as given:", "```", r[6], "```",
                f"- expected pattern: `{r[7]}` ; keywords: {r[8]}", f"- response: `{r[9]}`",
                f"- expected action is the **{r[10]}** (keyword hits: current-node description {r[11]}, outgoing edge instruction {r[12]})", ""]
    Path("data/eval/results/dev_iter5_report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:60]))
    print("written: data/eval/results/dev_iter5_report.md")


if __name__ == "__main__":
    main()
