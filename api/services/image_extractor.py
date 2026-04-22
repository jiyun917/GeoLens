"""
Manual image extractor.

Pulls embedded images from a PDF manual, filters out icons, captures nearby
caption text, and persists them under data/manual_images/{manual_id}/. The
surviving images + metadata feed into the visual matcher so live screenshots
can be matched to specific manual pages / workflow steps.
"""

import os
from typing import List, Dict, Optional

import fitz  # PyMuPDF

MIN_WIDTH = 100
MIN_HEIGHT = 100
NEARBY_TEXT_MARGIN = 40  # pixels above/below image to scan for caption

IMAGE_DIR = os.environ.get(
    "MANUAL_IMAGE_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "manual_images"),
)


class ManualImageExtractor:
    def extract_images(self, pdf_path: str) -> List[Dict]:
        """Return list of dicts describing each surviving image embedded in the PDF.

        Each dict contains:
          image_bytes (bytes), ext (str), page_number (1-based int),
          section (str), image_index (int), width, height, nearby_text (str).
        """
        if not os.path.exists(pdf_path):
            print(f"[IMG_EXTRACT] PDF not found: {pdf_path}")
            return []

        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        page_sections = {page_num - 1: title for _, title, page_num in toc}

        results: List[Dict] = []
        current_section = "Introduction"

        for page_num in range(len(doc)):
            page = doc[page_num]
            if page_num in page_sections:
                current_section = page_sections[page_num]

            images = page.get_images(full=True)
            for idx, img in enumerate(images):
                xref = img[0]
                try:
                    info = doc.extract_image(xref)
                except Exception as e:
                    print(f"[IMG_EXTRACT] extract failed xref={xref}: {e}")
                    continue

                w = int(info.get("width", 0) or 0)
                h = int(info.get("height", 0) or 0)
                if w < MIN_WIDTH or h < MIN_HEIGHT:
                    continue

                nearby = self._nearby_text(page, xref)
                results.append({
                    "image_bytes": info.get("image"),
                    "ext": info.get("ext", "png"),
                    "page_number": page_num + 1,
                    "section": current_section,
                    "image_index": idx,
                    "width": w,
                    "height": h,
                    "nearby_text": nearby,
                })

        doc.close()
        print(f"[IMG_EXTRACT] {os.path.basename(pdf_path)}: {len(results)} images (≥{MIN_WIDTH}×{MIN_HEIGHT})")
        return results

    def save_images(self, manual_id: str, images: List[Dict]) -> List[str]:
        """Persist images to data/manual_images/{manual_id}/ and return their absolute paths.

        Also mutates each dict in `images` to add `path` (absolute file path).
        """
        if not images:
            return []

        out_dir = os.path.join(IMAGE_DIR, manual_id)
        os.makedirs(out_dir, exist_ok=True)

        saved_paths: List[str] = []
        for i, meta in enumerate(images):
            ext = meta.get("ext", "png") or "png"
            filename = f"p{meta['page_number']:03d}_i{meta['image_index']:02d}.{ext}"
            path = os.path.join(out_dir, filename)
            try:
                with open(path, "wb") as f:
                    f.write(meta["image_bytes"])
                meta["path"] = path
                saved_paths.append(path)
            except Exception as e:
                print(f"[IMG_EXTRACT] save failed {path}: {e}")
        return saved_paths

    def _nearby_text(self, page, xref: int) -> str:
        """Approximate caption: text blocks whose bbox is near the image bbox."""
        try:
            rects = page.get_image_rects(xref) or []
        except Exception:
            return ""
        if not rects:
            return ""
        img_rect = rects[0]

        texts: List[str] = []
        try:
            blocks = page.get_text("blocks") or []
        except Exception:
            return ""

        for block in blocks:
            # block = (x0, y0, x1, y1, text, block_no, block_type, ...)
            if len(block) < 5:
                continue
            x0, y0, x1, y1, text = block[:5]
            if not text or not isinstance(text, str):
                continue
            # overlap check along X + proximity on Y axis
            x_overlap = min(x1, img_rect.x1) - max(x0, img_rect.x0)
            if x_overlap <= 0:
                continue
            above_gap = img_rect.y0 - y1
            below_gap = y0 - img_rect.y1
            if 0 <= above_gap <= NEARBY_TEXT_MARGIN or 0 <= below_gap <= NEARBY_TEXT_MARGIN:
                texts.append(text.strip())

        snippet = " ".join(t for t in texts if t)
        return snippet[:300]


def delete_manual_images(manual_id: str) -> bool:
    """Remove data/manual_images/{manual_id}/ and its contents. Returns True if removed."""
    import shutil
    target = os.path.join(IMAGE_DIR, manual_id)
    if not os.path.isdir(target):
        return False
    try:
        shutil.rmtree(target)
        return True
    except Exception as e:
        print(f"[IMG_EXTRACT] delete failed {target}: {e}")
        return False
