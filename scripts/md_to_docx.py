"""Convert the v2 final report from Markdown to Word.

Handles:
  - # / ## / ### headings
  - Bold **text** inline
  - Markdown tables (| col | col |)
  - Bullet lists (- item)
  - Horizontal rules (---) as page separators
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


import sys as _sys
if len(_sys.argv) >= 3:
    SRC = Path(_sys.argv[1])
    OUT = Path(_sys.argv[2])
else:
    SRC = Path(r"C:\Users\user\Downloads\GeoLens_v2_최종보고서.md")
    OUT = Path(r"C:\Users\user\Downloads\GeoLens_v2_최종보고서.docx")


def add_inline_runs(paragraph, text: str) -> None:
    """Handle **bold** inline within a paragraph."""
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            paragraph.add_run(part)


def add_table(doc: Document, header: list[str], rows: list[list[str]]) -> None:
    tbl = doc.add_table(rows=1 + len(rows), cols=len(header))
    tbl.style = "Light Grid Accent 1"
    # Header row
    hdr = tbl.rows[0].cells
    for i, cell in enumerate(header):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        run = p.add_run(cell.strip())
        run.bold = True
        run.font.size = Pt(9)
    # Data rows
    for r_idx, row in enumerate(rows, start=1):
        cells = tbl.rows[r_idx].cells
        for c_idx, cell in enumerate(row):
            if c_idx >= len(cells):
                continue
            cells[c_idx].text = ""
            p = cells[c_idx].paragraphs[0]
            add_inline_runs(p, cell.strip())
            for run in p.runs:
                run.font.size = Pt(9)


def parse_table_lines(lines: list[str], start: int) -> tuple[list[str], list[list[str]], int]:
    """Parse a markdown table starting at `start`. Returns (header, rows, next_idx)."""
    def _cells(line: str) -> list[str]:
        # Strip leading/trailing pipe and split
        s = line.strip()
        if s.startswith("|"):
            s = s[1:]
        if s.endswith("|"):
            s = s[:-1]
        return [c for c in s.split("|")]

    header = _cells(lines[start])
    # Next line is the separator (|---|---|)
    sep_idx = start + 1
    if sep_idx >= len(lines) or not re.match(r"^\s*\|[\s\-:|]+\|?\s*$", lines[sep_idx]):
        # Not actually a table
        return header, [], start + 1
    rows = []
    idx = sep_idx + 1
    while idx < len(lines):
        line = lines[idx]
        if not line.strip() or not line.strip().startswith("|"):
            break
        rows.append(_cells(line))
        idx += 1
    return header, rows, idx


def convert(src_path: Path, out_path: Path) -> None:
    doc = Document()

    # Set default font to something that supports Korean well
    style = doc.styles["Normal"]
    style.font.name = "맑은 고딕"
    style.font.size = Pt(10)

    # Set margins
    for section in doc.sections:
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.2)

    lines = src_path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip blank
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run("─" * 40)
            run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
            i += 1
            continue

        # Headings
        if stripped.startswith("# "):
            h = doc.add_heading(stripped[2:], level=0)
            for run in h.runs:
                run.font.name = "맑은 고딕"
            i += 1
            continue
        if stripped.startswith("## "):
            h = doc.add_heading(stripped[3:], level=1)
            for run in h.runs:
                run.font.name = "맑은 고딕"
            i += 1
            continue
        if stripped.startswith("### "):
            h = doc.add_heading(stripped[4:], level=2)
            for run in h.runs:
                run.font.name = "맑은 고딕"
            i += 1
            continue

        # Table
        if stripped.startswith("|") and stripped.endswith("|"):
            header, rows, next_i = parse_table_lines(lines, i)
            if rows:
                add_table(doc, header, rows)
                doc.add_paragraph()
                i = next_i
                continue

        # Bullet list
        if stripped.startswith("- ") or stripped.startswith("* "):
            item_text = stripped[2:]
            p = doc.add_paragraph(style="List Bullet")
            add_inline_runs(p, item_text)
            for run in p.runs:
                run.font.name = "맑은 고딕"
            i += 1
            continue

        # Numbered list
        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            p = doc.add_paragraph(style="List Number")
            add_inline_runs(p, m.group(2))
            for run in p.runs:
                run.font.name = "맑은 고딕"
            i += 1
            continue

        # Plain paragraph
        p = doc.add_paragraph()
        add_inline_runs(p, stripped)
        for run in p.runs:
            run.font.name = "맑은 고딕"
        i += 1

    doc.save(str(out_path))
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    convert(SRC, OUT)
