"""Convert GeoLens_종합결과보고서_final.md → docx with table rendering."""

import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

sys.stdout.reconfigure(encoding="utf-8")

MD = Path(r"GeoLens_종합결과보고서_final.md")
OUT = Path(r"out/GeoLens_종합결과보고서_final.docx")


def set_cell_shading(cell, color_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def add_table_from_md(doc, header, rows):
    n_cols = len(header)
    t = doc.add_table(rows=1 + len(rows), cols=n_cols)
    t.style = "Light Grid Accent 1"
    hdr = t.rows[0].cells
    for i, h in enumerate(header):
        hdr[i].text = h
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(8)
        set_cell_shading(hdr[i], "D9E2F3")
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row[:n_cols]):
            t.rows[ri + 1].cells[ci].text = str(val)
            for p in t.rows[ri + 1].cells[ci].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8)


def parse_md_table(lines, start_idx):
    """Return (header, rows, next_idx) starting at pipe table."""
    header_line = lines[start_idx]
    if start_idx + 1 >= len(lines) or "|---" not in lines[start_idx + 1] and "|-" not in lines[start_idx + 1]:
        return None, None, start_idx
    header = [c.strip() for c in header_line.strip().strip("|").split("|")]
    rows = []
    i = start_idx + 2
    while i < len(lines) and lines[i].strip().startswith("|") and "---" not in lines[i]:
        row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        rows.append(row)
        i += 1
    return header, rows, i


def add_code_block(doc, code_text):
    para = doc.add_paragraph()
    para.paragraph_format.left_indent = Cm(0.5)
    run = para.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)


def process_inline(paragraph, text):
    """Handle **bold**, `code`, plain."""
    parts = re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = paragraph.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("`") and part.endswith("`"):
            r = paragraph.add_run(part[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9)
        else:
            paragraph.add_run(part)


def main():
    doc = Document()
    # font defaults
    style = doc.styles["Normal"]
    style.font.name = "맑은 고딕"
    style.font.size = Pt(10)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "맑은 고딕")
    for h in ["Heading 1", "Heading 2", "Heading 3"]:
        s = doc.styles[h]
        s.font.name = "맑은 고딕"
        s._element.rPr.rFonts.set(qn("w:eastAsia"), "맑은 고딕")

    lines = MD.read_text(encoding="utf-8").splitlines()
    i = 0
    in_code = False
    code_buf = []
    while i < len(lines):
        line = lines[i]

        # code block toggle
        if line.strip().startswith("```"):
            if in_code:
                add_code_block(doc, "\n".join(code_buf))
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # table
        if line.strip().startswith("|") and i + 1 < len(lines) and ("|---" in lines[i + 1] or "|-" in lines[i + 1]):
            header, rows, i = parse_md_table(lines, i)
            if header and rows:
                add_table_from_md(doc, header, rows)
                doc.add_paragraph()
                continue

        # headings
        if line.startswith("# "):
            h = doc.add_heading(line[2:].strip(), level=0)
            h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=1)
        elif line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=2)
        elif line.startswith("#### "):
            doc.add_heading(line[5:].strip(), level=3)
        # horizontal rule
        elif line.strip() == "---":
            p = doc.add_paragraph("─" * 60)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # bullet list
        elif line.strip().startswith("- "):
            para = doc.add_paragraph(style="List Bullet")
            process_inline(para, line.strip()[2:])
        # numbered list
        elif re.match(r"^\d+\. ", line.strip()):
            para = doc.add_paragraph(style="List Number")
            process_inline(para, re.sub(r"^\d+\. ", "", line.strip()))
        # blank line
        elif not line.strip():
            doc.add_paragraph()
        # regular paragraph
        else:
            para = doc.add_paragraph()
            process_inline(para, line)
        i += 1

    doc.save(str(OUT))
    print(f"[SAVED] {OUT}")
    print(f"[SIZE] {OUT.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
