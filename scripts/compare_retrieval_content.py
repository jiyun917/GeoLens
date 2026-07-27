"""Verification (a′) — content-level retrieval overlap between two indexes.

For each evaluation query, retrieve top-K chunk *documents* (not IDs) from
both indexes, normalize the concatenated text (lowercase, whitespace
collapse), then compute a token-shingle Jaccard overlap.

Rationale for the newer approach: chunk UUIDs regenerate on each reindex
(so ID-based comparison always returns 0.0), and (page, section) signature
comparison undercounts because parser-induced chunk boundary shifts move
content across chunk boundaries even when the retrieved text is nearly
identical. Content-level shingle Jaccard directly measures "how much of
the retrieved context is the same," which is what the generator actually
consumes.

Pass threshold: mean shingle-Jaccard >= 0.80.

Usage:
    .venv/Scripts/python.exe scripts/compare_retrieval_content.py \\
        --index-a data/chromadb_pymupdf_reference \\
        --index-b data/chromadb \\
        --manual-id 645b7cdf2690408da843b9ce63c52d5b \\
        --top-k 5 --shingle-n 5
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _queries_from_scenarios() -> list[tuple[str, int, str]]:
    """Same query construction as scripts/compare_retrieval.py."""
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


def _normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip common metadata brackets."""
    if not text:
        return ""
    # Strip our contextual retrieval prefix like [Section: X, Page: Y, Source: Z]
    text = re.sub(r"\[Section:[^\]]*\]", " ", text)
    # Lowercase + collapse whitespace
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _shingles(text: str, n: int = 5) -> set[str]:
    """Return set of n-token shingles from normalized text."""
    tokens = text.split()
    if len(tokens) < n:
        return set([" ".join(tokens)]) if tokens else set()
    return set(" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-a", required=True)
    ap.add_argument("--index-b", required=True)
    ap.add_argument("--manual-id", required=True)
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--shingle-n", type=int, default=5, help="n-gram size for shingles")
    ap.add_argument("--out", default="data/eval/results/retrieval_overlap_content.json")
    args = ap.parse_args()

    import chromadb
    ca = chromadb.PersistentClient(path=args.index_a)
    cb = chromadb.PersistentClient(path=args.index_b)
    coll = f"manual_{args.manual_id}"
    col_a = ca.get_collection(coll)
    col_b = cb.get_collection(coll)
    print(f"Index A chunks: {col_a.count()}")
    print(f"Index B chunks: {col_b.count()}")

    queries = _queries_from_scenarios()
    print(f"Queries: {len(queries)}")
    print(f"Shingle n: {args.shingle_n}")
    print()

    rows = []
    overlaps = []
    for sid, idx, q in queries:
        ra = col_a.query(query_texts=[q], n_results=args.top_k)
        rb = col_b.query(query_texts=[q], n_results=args.top_k)
        docs_a = (ra.get("documents") or [[]])[0]
        docs_b = (rb.get("documents") or [[]])[0]
        text_a = _normalize(" \n ".join(docs_a))
        text_b = _normalize(" \n ".join(docs_b))
        sh_a = _shingles(text_a, args.shingle_n)
        sh_b = _shingles(text_b, args.shingle_n)
        inter = sh_a & sh_b
        union = sh_a | sh_b
        jaccard = len(inter) / len(union) if union else 0.0
        overlaps.append(jaccard)
        rows.append({
            "scenario": sid,
            "step": idx,
            "query_preview": q[:100],
            "shingles_a": len(sh_a),
            "shingles_b": len(sh_b),
            "shingles_intersection": len(inter),
            "jaccard_shingle": round(jaccard, 3),
            "text_a_len_chars": len(text_a),
            "text_b_len_chars": len(text_b),
        })

    mean_overlap = sum(overlaps) / len(overlaps) if overlaps else 0.0
    print(f"Per-query results:")
    for r in rows:
        print(f"  {r['scenario'].split('__')[1]} step {r['step']}: "
              f"jaccard_shingle={r['jaccard_shingle']}  "
              f"(|A|={r['shingles_a']}, |B|={r['shingles_b']}, "
              f"|∩|={r['shingles_intersection']})")

    print()
    print(f"Mean shingle-Jaccard overlap: {mean_overlap:.3f}")
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
        "shingle_n": args.shingle_n,
        "mean_shingle_jaccard": mean_overlap,
        "verdict": verdict,
        "n_queries": len(overlaps),
        "per_query": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
