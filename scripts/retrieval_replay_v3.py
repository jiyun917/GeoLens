"""Offline retrieval replay (no LLM calls): for each scenario goal, run the
deterministic vanilla_vector retrieval (get_manual_context(goal, top_k=5))
against an index and report which manual sections the top-5 (+neighbour)
chunks come from, whether the scenario's target section is hit, and how
much manual text survives the guide-mode 1,500-char vector budget.

Run once per index/embedder pair, e.g.
    CHROMADB_PATH=./data/chromadb    EMBED_MODEL=all-MiniLM-L6-v2 python scripts/retrieval_replay_v3.py --label minilm
    CHROMADB_PATH=./data/chromadb_v3 EMBED_MODEL=BAAI/bge-m3       python scripts/retrieval_replay_v3.py --label bgem3
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# scenario -> target manual section prefix(es) (from manual_reference)
TARGET = {
    "opendtect__survey_setup__01": ["1.2.2a"],
    "opendtect__3d_visualization__01": ["1.3.1a", "1.3.1"],
    "opendtect__attribute_computation__01": ["1.5.1a"],
    "qgis__vector_buffer__01": ["6.2.6", "6.2"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--budget", type=int, default=1500)
    ap.add_argument("--include-qgis", action="store_true",
                    help="v3 dev loop: the QGIS test scenario is skipped unless this flag is given "
                         "(no QGIS execution, dry-runs included, before the freeze commit)")
    args = ap.parse_args()
    from api.services.rag import get_manual_context
    from api.services.embedder import EMBED_MODEL
    import tiktoken
    enc = tiktoken.get_encoding("o200k_base")
    lines = [f"# Retrieval replay — {args.label} (EMBED_MODEL={EMBED_MODEL}, CHROMADB_PATH={os.environ.get('CHROMADB_PATH')}, KG position={os.environ.get('RAG_KG_POSITION', 'last')})", "",
             "| scenario | target section | chunks (top-5 + ±1) | target hits | sections (in order) | ctx chars | ctx tokens | first 1,500 chars = manual text? |",
             "|---|---|---|---|---|---|---|---|"]
    for f in sorted(glob.glob(str(ROOT / "data/eval/scenarios/*.json"))):
        scen = json.load(open(f, encoding="utf-8"))
        sid = scen.get("scenario_id")
        if not sid or sid == "EXAMPLE_PLACEHOLDER":
            continue
        if sid.startswith("qgis") and not args.include_qgis:
            print(f"[replay] skip {sid} (QGIS test set; --include-qgis to run)")
            continue
        ctx = get_manual_context([scen["manual_id"]], scen["goal"], top_k=5) or ""
        secs = re.findall(r"\[Source: [^\]]*?Section: ([^\]]+)\]", ctx)
        secs_short = [s.split(" ")[0] for s in secs]
        targets = TARGET.get(sid, [])
        hits = sum(1 for s in secs if any(s.startswith(t) for t in targets))
        head = ctx[:args.budget]
        head_is_manual = head.lstrip().startswith("[Source:")
        lines.append(f"| {sid} | {'/'.join(targets)} | {len(secs)} | {hits}/{len(secs)} | {', '.join(secs_short)} | {len(ctx)} | {len(enc.encode(ctx))} | {'yes' if head_is_manual else 'no (KG block first)'} |")
        print(lines[-1])
    out = ROOT / f"data/eval/results/retrieval_replay_{args.label}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("saved:", out)


if __name__ == "__main__":
    main()
