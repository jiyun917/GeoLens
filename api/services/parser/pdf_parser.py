"""PDF parser using pdfplumber (text extraction + image rendering for OCR)
and pypdf (outline / table of contents).

Migrated from PyMuPDF (AGPL-3.0) to pdfplumber (MIT) + pypdf (BSD-3-Clause)
for MIT-license compatibility of the overall project. See
`data/eval/results/pypdf_migration_audit.md` for equivalence verification
between the two indexes.

Note on text quality: pdfplumber preserves most whitespace correctly for
paragraph text; a small fraction of tokens lose inter-word spaces (e.g.
`Requiredlicenses:OpendTect`), which is why we validate retrieval
equivalence against the PyMuPDF-based index rather than assuming identity.
"""

import io
import os
import time
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import pdfplumber
import pypdf

# Minimum text length to consider a page as text-based (not image-based)
MIN_TEXT_LENGTH = 50

# pdfplumber x_tolerance controls how close (in points) two characters must
# be along the x-axis to be considered part of the same word. The default
# of 3 is too loose for this manual's font metrics and collapses inter-word
# spaces (e.g. "Requiredlicenses:OpendTect"). 1.5 restores paragraph-level
# spacing to parity with PyMuPDF on sampled pages. Documented in
# data/eval/results/pypdf_migration_audit.md §F1.
PDFPLUMBER_X_TOLERANCE = 1.5


OCR_MODEL = "gemini-2.5-flash"
OCR_MAX_RETRIES = 4
OCR_BASE_BACKOFF = 2.0  # seconds; doubles each retry with jitter


def _is_transient_error(err: Exception) -> bool:
    """Classify errors worth retrying: 503/429/500/504 + network timeouts."""
    msg = str(err)
    for marker in ("503", "429", "500", "504", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
                   "DEADLINE_EXCEEDED", "timeout", "Timeout", "temporarily"):
        if marker in msg:
            return True
    return False


def _ocr_page_gemini(image_bytes: bytes, page_num: int, api_key: str) -> str:
    """Extract text from a PDF page image using Gemini Vision, with retry on transient errors."""
    from google import genai
    from google.genai import types
    import random

    client = genai.Client(api_key=api_key)

    prompt = (
        "Extract all readable text from this PDF page. "
        "Preserve the reading order (top-to-bottom, left-to-right within columns). "
        "Do NOT describe images — only extract readable text."
    )

    last_err = None
    for attempt in range(OCR_MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=OCR_MODEL,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                    prompt,
                ],
            )
            return (response.text or "").strip()
        except Exception as e:
            last_err = e
            if not _is_transient_error(e) or attempt >= OCR_MAX_RETRIES:
                break
            delay = OCR_BASE_BACKOFF * (2 ** attempt) + random.uniform(0, 0.5)
            print(f"[OCR] Page {page_num + 1} transient error ({type(e).__name__}); "
                  f"retry {attempt + 1}/{OCR_MAX_RETRIES} after {delay:.1f}s")
            time.sleep(delay)

    print(f"[OCR] Page {page_num + 1} failed after {OCR_MAX_RETRIES + 1} attempts: {last_err}")
    return ""


def _render_page_to_png(page, resolution: int = 200) -> bytes:
    """Render a pdfplumber page to PNG bytes."""
    img = page.to_image(resolution=resolution)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _extract_page_sections(file_path: str) -> dict:
    """Build page-to-section mapping from PDF outline via pypdf.

    Returns {page_index_0based: section_title}. Empty dict if outline
    missing or malformed — caller falls back to "Introduction" default.
    """
    page_sections = {}
    try:
        reader = pypdf.PdfReader(file_path)
        outline = reader.outline
        if not outline:
            return {}

        def _walk(items):
            """pypdf.outline is a nested list: Destination objects at leaves,
            lists for subsections."""
            for item in items:
                if isinstance(item, list):
                    _walk(item)
                else:
                    # item is a Destination
                    try:
                        title = str(item.title) if hasattr(item, "title") else ""
                        page_num = reader.get_destination_page_number(item)
                        if page_num is not None and title:
                            page_sections[page_num] = title
                    except Exception:
                        continue

        _walk(outline)
    except Exception as e:
        print(f"[parser] Outline extraction failed ({e}); sections will be empty.")
    return page_sections


def parse_pdf(file_path: str) -> List[Tuple[str, dict]]:
    """
    Extract text from a PDF file.
    For image-based pages (scanned/embedded images), uses Gemini Vision OCR.
    """
    page_sections = _extract_page_sections(file_path)
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    with pdfplumber.open(file_path) as doc:
        # First pass: collect text and identify image-based pages
        pages_data = []
        current_section = "Introduction"

        for page_num in range(len(doc.pages)):
            page = doc.pages[page_num]
            text = (page.extract_text(x_tolerance=PDFPLUMBER_X_TOLERANCE) or "").strip()

            if page_num in page_sections:
                current_section = page_sections[page_num]

            metadata = {
                "source": file_path,
                "page": page_num + 1,
                "section": current_section,
                "type": "pdf",
            }

            needs_ocr = len(text) < MIN_TEXT_LENGTH and gemini_api_key
            pages_data.append({
                "page_num": page_num,
                "text": text,
                "metadata": metadata,
                "needs_ocr": needs_ocr,
            })

        # OCR pass: process image-based pages with Gemini Vision
        ocr_pages = [p for p in pages_data if p["needs_ocr"]]
        if ocr_pages:
            total = len(ocr_pages)
            print(f"[OCR] {total} image-based pages detected. Starting Gemini Vision OCR...")

            # Render pages to images
            for p in ocr_pages:
                page = doc.pages[p["page_num"]]
                p["image_bytes"] = _render_page_to_png(page)

            # Process in parallel (5 concurrent, respect rate limits)
            completed = 0

            def process_page(p):
                return p["page_num"], _ocr_page_gemini(
                    p["image_bytes"], p["page_num"], gemini_api_key
                )

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(process_page, p): p for p in ocr_pages}
                for future in as_completed(futures):
                    page_num, ocr_text = future.result()
                    completed += 1
                    if ocr_text:
                        # Find and update the page data
                        for p in pages_data:
                            if p["page_num"] == page_num:
                                p["text"] = ocr_text
                                break
                    if completed % 20 == 0:
                        print(f"[OCR] Progress: {completed}/{total} pages")

            print(f"[OCR] Complete: {completed}/{total} pages processed")

    # Build results
    results = []
    for p in pages_data:
        if p["text"].strip():
            results.append((p["text"], p["metadata"]))

    return results
