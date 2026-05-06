import io
import os
import time
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import fitz  # PyMuPDF

# Minimum text length to consider a page as text-based (not image-based)
MIN_TEXT_LENGTH = 50


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
        "Extract ALL text from this document page exactly as written.\n"
        "Include: headings, body text, bullet points, numbered lists, "
        "table content, UI element names, menu paths, button labels, "
        "step-by-step instructions.\n"
        "Output plain text preserving structure. "
        "Do NOT describe images — only extract readable text."
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ],
        )
    ]

    config = types.GenerateContentConfig(temperature=0)

    last_err: Exception = RuntimeError("never attempted")
    for attempt in range(OCR_MAX_RETRIES + 1):
        try:
            result = client.models.generate_content(
                model=OCR_MODEL,
                contents=contents,
                config=config,
            )
            if attempt > 0:
                print(f"[OCR] Page {page_num + 1} recovered on retry {attempt}")
            return result.text or ""
        except Exception as e:
            last_err = e
            if attempt >= OCR_MAX_RETRIES or not _is_transient_error(e):
                break
            # exponential backoff with jitter
            delay = OCR_BASE_BACKOFF * (2 ** attempt) + random.uniform(0, 1.0)
            print(f"[OCR] Page {page_num + 1} transient error ({e.__class__.__name__}); "
                  f"retry {attempt + 1}/{OCR_MAX_RETRIES} after {delay:.1f}s")
            time.sleep(delay)

    print(f"[OCR] Page {page_num + 1} failed after {OCR_MAX_RETRIES + 1} attempts: {last_err}")
    return ""


def _render_page_to_png(page) -> bytes:
    """Render a PDF page to PNG bytes."""
    pix = page.get_pixmap(dpi=200)
    return pix.tobytes("png")


def parse_pdf(file_path: str) -> List[Tuple[str, dict]]:
    """
    Extract text from a PDF file.
    For image-based pages (scanned/embedded images), uses Gemini Vision OCR.
    """
    doc = fitz.open(file_path)
    toc = doc.get_toc()

    # Build page-to-section mapping from TOC
    page_sections = {}
    for level, title, page_num in toc:
        page_sections[page_num - 1] = title

    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    # First pass: collect text and identify image-based pages
    pages_data = []
    current_section = "Introduction"

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()

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
            page = doc[p["page_num"]]
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

    doc.close()

    # Build results
    results = []
    for p in pages_data:
        if p["text"].strip():
            results.append((p["text"], p["metadata"]))

    return results
