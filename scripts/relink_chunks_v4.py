"""Re-link OpendTect workflow nodes to the v4 knowledge base (Task A, v3).

Finding (2026-09-18): every linked_chunks id in data/workflows/*.json (98
ids across 6 files) resolves in NEITHER data/chromadb (the index used by
unified2-4) NOR data/chromadb_v3. The ids were produced by chunk_mapper.py
against the April-2026 ingestion; the July-2026 re-ingestion (pdfplumber +
pypdf migration) regenerated every chunk uuid, so from then on
retrieve_by_graph() fetched nothing for linked_chunks and full_system's
graph_context consisted only of the per-node title/description vector
searches. There is therefore no old chunk text to map from; the links are
regenerated with the ORIGINAL mechanism (chunk_mapper.map_node_to_chunks:
query = workflow label + title + description + screenshot keywords, top-3
by embedding similarity) against the v4 index under bge-m3.

Scope: the five hand-written OpendTect workflows only. The QGIS
auto-workflow (auto_bf2804…) is left untouched — QGIS-side artefacts are
frozen for the test set; its links stay dangling exactly as in v2 and the
runtime falls back to the per-node vector search for it.

Usage:
    CHROMADB_PATH=./data/chromadb_v4 EMBED_MODEL=BAAI/bge-m3 \
        .venv/Scripts/python.exe scripts/relink_chunks_v4.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

OPENDTECT_MANUAL = "645b7cdf2690408da843b9ce63c52d5b"
QGIS_MANUAL = "bf2804feea57434bb79b749134ed1df0"
MANUALS = {
    # manual key -> (manual_id, workflow files)
    "opendtect": (OPENDTECT_MANUAL, ["survey_setup.json", "d3_visualization.json", "seismic_attribute.json",
                                     "fault_interpretation.json", "horizon_tracking.json"]),
    # QGIS (user decision 2026-09-18): same section-provenance rule, applied after the
    # QGIS re-ingest and before the freeze commit, without executing the QGIS scenario.
    # Only linked_chunks / manual_sections / provenance are written; signatures, titles,
    # descriptions and the scenario file are not touched.
    "qgis": (QGIS_MANUAL, ["qgis_vector_buffer.json"]),
    # study 2 (2026-09-21, V3-32): the two test-set workflows authored from the manual were
    # committed WITHOUT linked_chunks (authoring omission); same mechanism and section rule.
    "study2": (OPENDTECT_MANUAL, ["horizon_autotrack_142a.json", "fault_sticks_143b.json"]),
}
FILES = MANUALS["opendtect"][1]

# Section provenance (v3): the manual exercise section(s) each hand-authored
# node was written from. Prefix match on the chunk's section label ("1.3.1 "
# with a trailing space = the parent section only; "1.4.3" = 1.4.3, 1.4.3a,
# 1.4.3b). chunk_mapper ranks the chunks of these sections first (by the same
# embedding distance) and fills remaining slots from the global top-k.
# The QGIS workflow files are not touched.
SECTIONS = {
    "survey_setup": {
        "survey_setup_01_open_selection": ["1.2.2a", "1.2 "],
        "survey_setup_02_open_new_survey_dialog": ["1.2.2a"],
        "survey_setup_03_choose_initial_setup": ["1.2.2a"],
        "survey_setup_04_scan_segy": ["1.2.2a", "1.2.2b"],
        "survey_setup_05_select_survey": ["1.2.2a"],
    },
    "d3_visualization": {
        "d3_visualization_01_main_window_ready": ["1.3.1 ", "1.3.1a"],
        "d3_visualization_02_add_inline": ["1.3.1a", "1.3.1 "],
        "d3_visualization_03_add_crossline": ["1.3.1a", "1.3.1 "],
        "d3_visualization_04_add_zslice": ["1.3.1a", "1.3.1 "],
        "d3_visualization_05_all_slices_displayed": ["1.3.1a", "1.3.1 "],
    },
    "seismic_attribute": {
        "seismic_attribute_01_ready_to_start": ["1.5.1a", "1.5.1 ", "1.5 "],
        "seismic_attribute_02_open_attribute_tool": ["1.5.1a"],
        "seismic_attribute_03_select_type": ["1.5.1a"],
        "seismic_attribute_04_configure": ["1.5.1a"],
        "seismic_attribute_05_compute": ["1.5.1a"],
        "seismic_attribute_06_display": ["1.5.1a"],
        "seismic_attribute_07_qc_analyze": ["1.5.1a"],
    },
    "fault_interpretation": {"*": ["1.4.3"]},
    "horizon_tracking": {"*": ["1.4.2"]},
    "horizon_autotrack_142a": {"*": ["1.4.2a"]},
    "fault_sticks_143b": {"*": ["1.4.3b"]},
    # QGIS Training Manual 3.44 §6.2.6 "Follow Along: Analyzing the Problem: Distances
    # From Schools and Roads" (pp. 212-218) — the workflow file's own manual_reference.
    # The QGIS parser keeps section TITLES (with the manual's difficulty stars),
    # not numbers: §6.2.6 is stored as "★☆☆ Follow Along: Analyzing the Problem:
    # Distances From Schools and Roads" (7 chunks, pp. 212-218, unique label).
    "qgis_vector_buffer": {"*": ["★☆☆ Follow Along: Analyzing the Problem"]},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--report", default=None)
    ap.add_argument("--manual", default="opendtect", choices=sorted(MANUALS))
    args = ap.parse_args()
    import time as _time
    t_start = _time.time()
    manual_id, files = MANUALS[args.manual]
    report = args.report or (f"data/eval/results/relink_chunks_v4{'' if args.manual == 'opendtect' else '_' + args.manual}.md")

    from api.services import vectorstore
    from api.services.chunk_mapper import map_node_to_chunks
    from api.services.embedder import EMBED_MODEL

    OPENDTECT_MANUAL_ = manual_id  # noqa (kept for readability below)
    col = vectorstore.get_collection(manual_id)
    print(f"[relink] chroma={vectorstore.CHROMA_DIR} embed={EMBED_MODEL} "
          f"collection count={col.count() if col else None}")
    if not col or col.count() == 0:
        print("[relink] empty collection — abort"); sys.exit(1)

    lines = [f"# linked_chunks re-link — {args.manual} — v4 index ({vectorstore.CHROMA_DIR}, {EMBED_MODEL}), {date.today().isoformat()}", "",
             "Mechanism: chunk_mapper.map_node_to_chunks (unchanged): query = workflow label + title + description + screenshot keywords; top-3 by embedding distance.",
             "Section provenance (v3): node.manual_sections restricts candidates to the node's source section(s) first (see SECTIONS in this script).",
             "", "| workflow | node | manual_sections | old ids resolve? | new chunk (section, p.) | distance |", "|---|---|---|---|---|---|"]
    for fn in files:
        path = ROOT / "data" / "workflows" / fn
        data = json.load(open(path, encoding="utf-8"))
        wf_secs = SECTIONS.get(data.get("workflow_id"), {})
        for node in data.get("nodes", []):
            node["manual_sections"] = list(wf_secs.get(node["id"], wf_secs.get("*", [])))
            old = list(node.get("linked_chunks") or [])
            old_found = 0
            if old:
                got = vectorstore.get_chunks_by_ids(manual_id, old)
                old_found = sum(1 for d in got.get("documents", []) if d)
            new_ids = map_node_to_chunks(node, [manual_id], top_k=args.top_k)
            got_new = vectorstore.get_chunks_by_ids(manual_id, new_ids)
            metas = got_new.get("metadatas", [])
            # distances for the report
            from api.services.embedder import get_embeddings
            q = f"{(node.get('workflow_id') or '').replace('_', ' ')} {node.get('title') or ''} {node.get('description') or ''} " \
                f"{' '.join((node.get('visual_signature') or {}).get('screenshot_keywords') or [])}".strip()
            res = vectorstore.search(manual_id, get_embeddings([q])[0], top_k=args.top_k)
            dist = {cid: d for cid, d in zip(res["ids"][0], res["distances"][0])} if res and res.get("ids") else {}
            desc = "; ".join(f"{(m or {}).get('section', '?')[:40]} p.{(m or {}).get('page', '?')}" for m in metas)
            dists = ", ".join(f"{dist.get(c, float('nan')):.3f}" for c in new_ids)
            lines.append(f"| {data['workflow_id']} | {node['id']} | {', '.join(node['manual_sections']) or '—'} | {old_found}/{len(old)} | {desc} | {dists} |")
            node["linked_chunks"] = new_ids
            node["linked_chunks_provenance"] = {
                "index": os.path.basename(str(vectorstore.CHROMA_DIR)), "embed_model": EMBED_MODEL,
                "mapped_on": date.today().isoformat(), "mechanism": "chunk_mapper.map_node_to_chunks top-3 (section provenance first)",
                "previous_ids": old, "previous_ids_resolved": old_found,
            }
        if not args.dry_run:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print(f"[relink] wrote {fn}")
    elapsed = _time.time() - t_start
    lines += ["", f"Wall-clock for this relink run (model load + {sum(len(json.load(open(ROOT / 'data' / 'workflows' / f, encoding='utf-8'))['nodes']) for f in files)} nodes): {elapsed:.1f} s."]
    Path(report).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"[relink] report: {report}  elapsed={elapsed:.1f}s")


if __name__ == "__main__":
    main()
