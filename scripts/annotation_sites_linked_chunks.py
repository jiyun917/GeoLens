"""List every place that cites unified2–4 full_system results and therefore
needs the V3-9 annotation: "full_system was measured without linked_chunks
text (all linked_chunks ids dangling since the 2026-07-27 re-ingest;
graph_context = per-node title/description vector search only)".

Scans (a) live Markdown under data/eval/results (archives, stale and
discarded folders excluded), qualitative INDEX/README, and (b) the Word
files in ~/Downloads that carry the paper / supplement text. For each hit
it reports the nearest preceding heading (Markdown '#' line, or a Word
paragraph with a Heading style) so the note can be placed at the right
table or section. Output: data/eval/results/v3_linked_chunks_annotation_sites.md
"""
from __future__ import annotations

import glob
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "eval" / "results" / "v3_linked_chunks_annotation_sites.md"
DOWNLOADS = Path.home() / "Downloads"

PAT = re.compile(r"full_system|full system|Full system|Full System|full‑system|풀 시스템|전체 시스템|GeoLens \(full\)", re.I)
RUN_PAT = re.compile(r"unified[234]|unified_?[234]|Table ?1|표 ?1|step[ _]acc", re.I)
SKIP_DIRS = (".archive_unified2", "_stale_gemini_429", "_stale_pre_completion_fix", "discarded", "dev_iter", "v3_", "rescore_v3",
             "routing_dryrun", "retrieval_replay", "relink_chunks", "gt_", "reindex_v4")


def scan_md(path: Path):
    hits = []
    heading = "(top)"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return hits
    for i, ln in enumerate(lines, 1):
        if ln.startswith("#"):
            heading = ln.strip("# ").strip()[:90]
        if PAT.search(ln):
            hits.append((i, heading, ln.strip()[:110]))
    return hits


def scan_docx(path: Path):
    try:
        import docx
    except ImportError:
        return None
    try:
        d = docx.Document(str(path))
    except Exception as e:
        return [("?", f"(cannot open: {e})", "")]
    hits = []
    heading = "(top)"
    for i, p in enumerate(d.paragraphs, 1):
        style = (p.style.name or "") if p.style is not None else ""
        if style.lower().startswith("heading") or style.lower().startswith("제목"):
            heading = p.text.strip()[:90] or heading
        if PAT.search(p.text):
            hits.append((f"p{i}", heading, p.text.strip()[:110]))
    for ti, t in enumerate(d.tables, 1):
        txt = " ".join(c.text for r in t.rows for c in r.cells)
        if PAT.search(txt):
            first = " | ".join(c.text.strip()[:18] for c in t.rows[0].cells)[:110]
            hits.append((f"table{ti}", "(table)", first))
    return hits


def main():
    out = ["# V3-9 annotation sites — documents citing unified2–4 full_system results", "",
           "Note to attach at each site: **\"unified2–4 full_system was measured without linked_chunks text: every linked_chunks id had been dangling since the 2026-07-27 re-ingest, so graph_context contained only the per-node title/description vector search (audit trail V3-9).\"**",
           "", "## Markdown (data/eval/results, live files only)", ""]
    md_files = sorted(glob.glob(str(ROOT / "data/eval/results/*.md"))) + \
        sorted(glob.glob(str(ROOT / "data/eval/qualitative/**/*.md"), recursive=True))
    n_md = 0
    for f in md_files:
        name = os.path.basename(f)
        if any(s in f for s in SKIP_DIRS) or any(name.startswith(s) for s in SKIP_DIRS):
            continue
        hits = scan_md(Path(f))
        if not hits:
            continue
        # keep only files that also mention a run/table (so pure code docs are skipped)
        body = Path(f).read_text(encoding="utf-8", errors="ignore")
        if not RUN_PAT.search(body):
            continue
        n_md += 1
        rel = os.path.relpath(f, ROOT).replace("\\", "/")
        headings = []
        for ln, h, txt in hits:
            if h not in headings:
                headings.append(h)
        out.append(f"### {rel}  ({len(hits)} mentions)")
        for h in headings[:12]:
            first = next(x for x in hits if x[1] == h)
            out.append(f"- section **{h}** — first at line {first[0]}: `{first[2]}`")
        out.append("")
    out += ["## Word documents (~/Downloads)", ""]
    for f in sorted(DOWNLOADS.glob("*.docx")):
        if f.name.startswith("~$"):
            continue
        hits = scan_docx(f)
        if hits is None:
            out.append("- python-docx not available"); break
        if not hits:
            continue
        out.append(f"### {f.name}  ({len(hits)} mentions)")
        seen = []
        for loc, h, txt in hits:
            key = (h if h != "(table)" else loc)
            if key in seen:
                continue
            seen.append(key)
            out.append(f"- {loc} · **{h}** — `{txt}`")
            if len(seen) >= 15:
                out.append("- …"); break
        out.append("")
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    print(f"\nwritten: {OUT} (markdown files with sites: {n_md})")


if __name__ == "__main__":
    main()
