"""Compare retrieval-top-K between two ChromaDB indexes for equivalence audit.

For each (scenario, step) query, runs vanilla_vector top-K on both indexes
and computes the Jaccard overlap of returned chunk IDs.

Passes when average Jaccard overlap >= 0.80.

Usage:
    .venv/Scripts/python.exe scripts/compare_retrieval.py \\
        --index-a data/chromadb_pymupdf_reference \\
        --index-b data/chromadb \\
        --manual-id 645b7cdf2690408da843b9ce63c52d5b \\
        --top-k 5
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


def _queries_from_scenarios() -> list[tuple[str, int, str]]:
    """Return (scenario_id, step_index, query_text) triples from active scenarios."""
    triples = []
    for p in sorted((ROOT / "data" / "eval" / "scenarios").glob("opendtect__*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        sid = d.get("scenario_id")
        for step in d.get("steps", []) or []:
            idx = step.get("step_index")
            vs = step.get("visual_state_gt") or {}
            # Build a query similar to what vanilla_vector backend uses
            parts = []
            for k in ("current_dialog", "active_menu", "current_action"):
                v = vs.get(k)
                if isinstance(v, str) and v.strip():
                    parts.append(v)
            for e in (vs.get("visible_elements") or [])[:3]:
                if isinstance(e, str):
                    parts.append(e)
            query = " ".join(parts).strip()
            if not query:
                continue
            triples.append((sid, idx, query))
    return triples


def _load_client(path: str):
    import chromadb
    return chromadb.PersistentClient(path=path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-a", required=True, help="Reference index (PyMuPDF)")
    ap.add_argument("--index-b", required=True, help="New index (pdfplumber)")
    ap.add_argument("--manual-id", required=True)
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--out", default="data/eval/results/retrieval_overlap.json")
    args = ap.parse_args()

    ca = _load_client(args.index_a)
    cb = _load_client(args.index_b)
    coll = f"manual_{args.manual_id}"
    col_a = ca.get_collection(coll)
    col_b = cb.get_collection(coll)
    print(f"Index A chunks: {col_a.count()}")
    print(f"Index B chunks: {col_b.count()}")

    queries = _queries_from_scenarios()
    print(f"Queries: {len(queries)}")

    def _sig(meta: dict) -> tuple:
        """Content-addressable signature for a retrieved chunk.

        Chunk IDs are UUIDs regenerated on each reindex so ID-based
        matching is impossible. We use (page, section) metadata which
        is stable across parser changes as long as the same source
        content is present. Two chunks with the same signature came
        from the same page under the same section — a meaningful
        equivalence for retrieval purposes.
        """
        return (meta.get("page"), meta.get("section"))

    rows = []
    overlaps = []
    for sid, idx, q in queries:
        ra = col_a.query(query_texts=[q], n_results=args.top_k)
        rb = col_b.query(query_texts=[q], n_results=args.top_k)
        metas_a = (ra.get("metadatas") or [[]])[0]
        metas_b = (rb.get("metadatas") or [[]])[0]
        sigs_a = set(_sig(m) for m in metas_a)
        sigs_b = set(_sig(m) for m in metas_b)
        inter = sigs_a & sigs_b
        union = sigs_a | sigs_b
        jaccard = len(inter) / len(union) if union else 0.0
        overlaps.append(jaccard)
        rows.append({
            "scenario": sid,
            "step": idx,
            "query_preview": q[:100],
            "top_k_a_pages": sorted([s[0] for s in sigs_a if s[0] is not None]),
            "top_k_b_pages": sorted([s[0] for s in sigs_b if s[0] is not None]),
            "intersection_signatures": sorted([str(s) for s in inter]),
            "jaccard": round(jaccard, 3),
        })

    mean_overlap = sum(overlaps) / len(overlaps) if overlaps else 0.0
    print(f"\nMean Jaccard overlap: {mean_overlap:.3f} across {len(overlaps)} queries")
    print(f"Pass threshold: 0.80")
    verdict = "PASS" if mean_overlap >= 0.80 else "FAIL"
    print(f"STATUS: {verdict}")

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "index_a": args.index_a,
        "index_b": args.index_b,
        "manual_id": args.manual_id,
        "top_k": args.top_k,
        "mean_jaccard": mean_overlap,
        "verdict": verdict,
        "n_queries": len(overlaps),
        "per_query": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
