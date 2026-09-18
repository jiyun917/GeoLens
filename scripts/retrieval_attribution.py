"""Retrieval attribution — evidence for the pre-registered attribute-scenario prediction.

Per unified3 pre-registration (v2_pre_registration.md § attribute prediction):
  "attribute 시나리오에서 vanilla_vector의 retrieval hit가 이론 페이지
   (§1.5.1)로 쏠려 step acc·faithfulness가 저조할 것,
   full_system은 workflow 라우팅으로 절차 청크(p118~120)를 확보해
   격차가 기존 2개 시나리오보다 벌어질 것."

This script produces the retrieval-page distribution evidence needed to
either confirm or falsify that prediction:

- **vanilla_vector**: For each scenario, replay the deterministic retrieval
  (`get_manual_context(manual_id, scenario.goal, top_k=5)`) and extract
  the [Section, Page] metadata from each returned chunk. This is
  deterministic given the fixed corpus + fixed query (scenario.goal), so
  it exactly reproduces what the bench harness saw.

- **full_system**: Aggregate per_step routing telemetry (picked_node_id,
  picked_workflow_id) from unified3 result files. This is stored per step
  by the ScenarioEvaluator (evaluation.py:713-718). Report the workflow
  and node distribution per scenario.

Then side-by-side compare:
  vanilla top-5 pages/sections vs. full_system routed workflow nodes.

If prediction confirmed:
  - vanilla attribute → top-5 dominated by §1.5.1 (theory p117) or
    unrelated sections; §1.5.1a procedural pages (118-128) absent or low.
  - full_system attribute → picked_workflow_id = seismic_attribute (the
    workflow whose nodes link to p118-128).

Output: data/eval/results/retrieval_attribution_unified3.md

Usage:
    .venv/Scripts/python.exe scripts/retrieval_attribution.py
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if (ROOT / p).exists():
            load_dotenv(ROOT / p)
except ImportError:
    pass


SCENARIOS = [
    "opendtect__survey_setup__01",
    "opendtect__3d_visualization__01",
    "opendtect__attribute_computation__01",
]

# Chunk header prefix pattern from api/services/rag.py:_format_context
# "[Source: <src>, Section: <section>]" or "[Source: <src>]"
CHUNK_HEADER = re.compile(
    r"\[Source:\s*(?P<source>[^,\]]+?)(?:,\s*Section:\s*(?P<section>[^\]]+?))?\](?:\s*\(adjacent context\))?"
)


def load_scenario(sid: str) -> dict:
    return json.loads((ROOT / "data" / "eval" / "scenarios" / f"{sid}.json").read_text(encoding="utf-8"))


def vanilla_retrieval_attribution(sid: str, top_k: int = 5) -> dict:
    """Replay vanilla_vector's deterministic retrieval for a scenario. Returns
    parsed chunk metadata + raw context length."""
    from api.services.rag import get_manual_context
    scen = load_scenario(sid)
    manual_id = scen["manual_id"]
    query = scen.get("goal", "")
    context = get_manual_context(manual_ids=[manual_id], query=query, top_k=top_k) or ""

    chunks = []
    for m in CHUNK_HEADER.finditer(context):
        section = (m.group("section") or "").strip()
        chunks.append({
            "section": section,
            "position": m.start(),
        })

    return {
        "scenario_id": sid,
        "query_prefix": query[:100],
        "context_len_chars": len(context),
        "n_chunk_headers": len(chunks),
        "top_k": top_k,
        "chunks": chunks,
    }


def full_system_routing_attribution(sid: str, tag: str = "unified3") -> dict:
    """Aggregate full_system per_step routing telemetry across all replicates
    for a scenario. Returns picked_node / picked_workflow distribution."""
    node_ctr: Counter = Counter()
    wf_ctr: Counter = Counter()
    conf_by_node: dict[str, list[float]] = defaultdict(list)
    n_steps = 0

    for f in sorted(glob.glob(str(ROOT / "data" / "eval" / "results" / f"run_*_{tag}_r*_*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for scen in d.get("scenarios") or []:
            if scen.get("scenario_id") != sid:
                continue
            fs = (scen.get("backends") or {}).get("full_system") or {}
            for ps in fs.get("per_step") or []:
                nid = ps.get("picked_node_id")
                wid = ps.get("picked_workflow_id")
                conf = ps.get("route_confidence", 0.0)
                if nid:
                    node_ctr[nid] += 1
                    conf_by_node[nid].append(conf)
                if wid:
                    wf_ctr[wid] += 1
                n_steps += 1

    return {
        "scenario_id": sid,
        "tag": tag,
        "n_steps_scanned": n_steps,
        "workflow_distribution": dict(wf_ctr),
        "node_distribution": dict(node_ctr),
        "mean_confidence_by_node": {
            k: round(sum(v) / len(v), 3) for k, v in conf_by_node.items()
        },
    }


def render_report() -> str:
    lines = [
        "# Retrieval attribution — unified3 pre-registration evidence",
        "",
        "Evidence for or against the pre-registered attribute-scenario",
        "prediction (v2_pre_registration.md § attribute prediction).",
        "",
        "## Vanilla vector retrieval (deterministic, replayed)",
        "",
        "For each scenario, `backend_vanilla_vector` calls `get_manual_context("
        "manual_ids, scenario.goal, top_k=5)`. That is a pure function of the "
        "fixed corpus and the fixed query (scenario.goal), so the retrieval "
        "we replay here matches bench-time exactly.",
        "",
    ]

    for sid in SCENARIOS:
        try:
            va = vanilla_retrieval_attribution(sid)
        except Exception as e:
            lines.append(f"### {sid}\n\nError: {e!r}\n")
            continue
        lines.append(f"### {sid}")
        lines.append("")
        lines.append(f"- query prefix: `{va['query_prefix']}...`")
        lines.append(f"- context length: {va['context_len_chars']} chars, {va['n_chunk_headers']} chunk headers")
        lines.append("")
        lines.append("**Retrieved chunks (Section / order)**:")
        for i, c in enumerate(va["chunks"], 1):
            lines.append(f"  {i}. {c['section'] or '(no section)'}")
        lines.append("")

    lines.append("## Full_system routing distribution")
    lines.append("")
    lines.append("Aggregated across all replicates of `unified3` full_system runs. "
                 "Reads `picked_node_id` / `picked_workflow_id` from each `per_step` record.")
    lines.append("")

    for sid in SCENARIOS:
        try:
            fa = full_system_routing_attribution(sid)
        except Exception as e:
            lines.append(f"### {sid}\n\nError: {e!r}\n")
            continue
        lines.append(f"### {sid}")
        lines.append("")
        lines.append(f"- steps scanned across all replicates: {fa['n_steps_scanned']}")
        lines.append("")
        lines.append("**Workflow distribution**:")
        for wf, n in sorted(fa["workflow_distribution"].items(), key=lambda kv: -kv[1]):
            lines.append(f"  - `{wf}`: {n} steps")
        lines.append("")
        lines.append("**Node distribution (top 10)**:")
        for node, n in sorted(fa["node_distribution"].items(), key=lambda kv: -kv[1])[:10]:
            conf = fa["mean_confidence_by_node"].get(node, 0)
            lines.append(f"  - `{node}`: {n} steps (mean conf {conf})")
        lines.append("")

    lines.append("## Prediction judgment")
    lines.append("")
    lines.append("Fill after inspecting the two sections above:")
    lines.append("")
    lines.append("- **vanilla — attribute scenario**: retrieved chunks' Section field")
    lines.append("  - Expected (if prediction confirmed): §1.5.1 (theory p117) or")
    lines.append("    unrelated sections dominate; §1.5.1a procedural (p118-128) absent/low.")
    lines.append("  - Observed: <fill in from Section list above>")
    lines.append("")
    lines.append("- **full_system — attribute scenario**: workflow distribution")
    lines.append("  - Expected (if prediction confirmed): `seismic_attribute` workflow")
    lines.append("    dominates. Nodes linked to procedural chunks (`_04_configure`,")
    lines.append("    `_06_display`) hit consistently.")
    lines.append("  - Observed: <fill in from workflow/node distribution above>")
    lines.append("")
    lines.append("- **Comparison to existing 2 scenarios**: cross-scenario Δ (full − vanilla)")
    lines.append("  step_acc + faithfulness should be larger for attribute than for the two")
    lines.append("  original scenarios if the retrieval-structuring mechanism dominates.")
    lines.append("  See `stats_audit.py --tag unified3` output.")
    lines.append("")

    return "\n".join(lines) + "\n"


def main():
    text = render_report()
    out = ROOT / "data" / "eval" / "results" / "retrieval_attribution_unified3.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
