"""
Visual matcher for manual screenshots.

Uses open-clip (ViT-B/32) to embed both manual images and live screenshots into
a shared vector space. At query time we compute cosine similarity against the
cached per-manual image index and return the top matches.

Graceful degradation: if open_clip / torch / PIL are not installed the matcher
returns empty results rather than raising, so the rest of the pipeline keeps
working.

Manual-image metadata (page_number, section, nearby_text) is preserved alongside
embeddings, which lets `match_to_workflow_node()` map a screenshot to a specific
workflow node via its linked_chunks / `page` attribute.
"""

import base64
import io
import os
from typing import Dict, List, Optional, Tuple

CLIP_MODEL_NAME = "ViT-B-32"
CLIP_PRETRAINED = "openai"

_matcher_singleton: Optional["VisualMatcher"] = None


class VisualMatcher:
    def __init__(self):
        self._model = None
        self._preprocess = None
        self._tokenizer = None
        self._torch = None
        self._device = "cpu"
        # manual_id → list of {"path", "page_number", "section", "embedding" (tensor), "nearby_text"}
        self._index: Dict[str, List[Dict]] = {}
        self._available = self._lazy_init()

    # ─────────────────────────────────────────────────────
    # Bootstrap
    # ─────────────────────────────────────────────────────

    def _lazy_init(self) -> bool:
        try:
            import torch
            import open_clip
            from PIL import Image  # noqa: F401
        except Exception as e:
            print(f"[VISUAL_MATCH] CLIP libs unavailable ({e}); matching disabled")
            return False

        try:
            self._torch = torch
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model, _, self._preprocess = open_clip.create_model_and_transforms(
                CLIP_MODEL_NAME, pretrained=CLIP_PRETRAINED
            )
            self._model.eval().to(self._device)
            self._tokenizer = open_clip.get_tokenizer(CLIP_MODEL_NAME)
            print(f"[VISUAL_MATCH] CLIP {CLIP_MODEL_NAME}/{CLIP_PRETRAINED} loaded on {self._device}")
            return True
        except Exception as e:
            print(f"[VISUAL_MATCH] CLIP init failed: {e}")
            return False

    def available(self) -> bool:
        return self._available

    # ─────────────────────────────────────────────────────
    # Indexing
    # ─────────────────────────────────────────────────────

    def index_manual_images(self, manual_id: str, image_entries: List[Dict]) -> int:
        """Embed each manual image and cache per manual_id.

        image_entries may be either a list of absolute file paths (str) or a list
        of dicts with at least {"path", "page_number", "section", "nearby_text"}.

        Returns the number of successfully indexed images.
        """
        if not self._available or not image_entries:
            return 0

        from PIL import Image

        entries: List[Dict] = []
        for item in image_entries:
            if isinstance(item, str):
                entries.append({"path": item})
            elif isinstance(item, dict) and item.get("path"):
                entries.append(item)

        if not entries:
            return 0

        indexed: List[Dict] = []
        batch_tensors = []
        batch_entries = []
        batch_size = 16

        def _flush():
            if not batch_tensors:
                return
            tensor = self._torch.stack(batch_tensors).to(self._device)
            with self._torch.no_grad():
                feats = self._model.encode_image(tensor)
                feats = feats / feats.norm(dim=-1, keepdim=True)
            feats = feats.cpu()
            for i, entry in enumerate(batch_entries):
                indexed.append({
                    **entry,
                    "embedding": feats[i],
                })
            batch_tensors.clear()
            batch_entries.clear()

        for entry in entries:
            path = entry["path"]
            try:
                img = Image.open(path).convert("RGB")
                tensor = self._preprocess(img)
            except Exception as e:
                print(f"[VISUAL_MATCH] skip {path}: {e}")
                continue
            batch_tensors.append(tensor)
            batch_entries.append(entry)
            if len(batch_tensors) >= batch_size:
                _flush()
        _flush()

        self._index[manual_id] = indexed
        print(f"[VISUAL_MATCH] indexed {len(indexed)} images for manual={manual_id}")
        return len(indexed)

    def clear_manual(self, manual_id: str) -> bool:
        return self._index.pop(manual_id, None) is not None

    # ─────────────────────────────────────────────────────
    # Matching
    # ─────────────────────────────────────────────────────

    def _embed_screenshot(self, screenshot_b64: str):
        from PIL import Image
        try:
            # Strip data URL prefix if present ("data:image/jpeg;base64,....")
            b64_payload = screenshot_b64
            if b64_payload.startswith("data:"):
                _, _, b64_payload = b64_payload.partition(",")
            raw = base64.b64decode(b64_payload)
            img = Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception as e:
            print(f"[VISUAL_MATCH] screenshot decode failed: {e}")
            return None
        tensor = self._preprocess(img).unsqueeze(0).to(self._device)
        with self._torch.no_grad():
            feats = self._model.encode_image(tensor)
            feats = feats / feats.norm(dim=-1, keepdim=True)
        return feats[0].cpu()

    def _ensure_indexed(self, manual_id: str) -> int:
        """If manual_id isn't in the in-memory index (e.g. after server restart),
        try to re-index from data/manual_images/{manual_id}/ on disk."""
        if manual_id in self._index:
            return len(self._index[manual_id])
        import glob, re as _re
        img_dir = os.path.join(
            os.environ.get(
                "MANUAL_IMAGE_DIR",
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "data", "manual_images",
                ),
            ),
            manual_id,
        )
        if not os.path.isdir(img_dir):
            return 0
        entries = []
        for path in sorted(glob.glob(os.path.join(img_dir, "*"))):
            fname = os.path.basename(path)
            m = _re.match(r"p(\d+)_i(\d+)\.", fname)
            if not m:
                continue
            entries.append({
                "path": path,
                "page_number": int(m.group(1)),
                "section": "",
                "nearby_text": "",
            })
        if not entries:
            return 0
        print(f"[VISUAL_MATCH] rehydrating {len(entries)} images for manual={manual_id} from disk")
        return self.index_manual_images(manual_id, entries)

    def match_screenshot(
        self,
        screenshot_b64: str,
        manual_id: str,
        top_k: int = 3,
    ) -> List[Dict]:
        """Return the top_k most similar manual images for the given screenshot."""
        if not self._available:
            return []
        self._ensure_indexed(manual_id)
        indexed = self._index.get(manual_id, [])
        if not indexed:
            return []

        query = self._embed_screenshot(screenshot_b64)
        if query is None:
            return []

        torch = self._torch
        stacked = torch.stack([e["embedding"] for e in indexed])
        sims = (stacked @ query).tolist()
        ranked = sorted(
            zip(sims, indexed), key=lambda p: p[0], reverse=True
        )[:top_k]
        return [
            {
                "manual_image_path": e.get("path"),
                "similarity": float(s),
                "page_number": e.get("page_number"),
                "section": e.get("section"),
                "nearby_text": e.get("nearby_text", ""),
            }
            for s, e in ranked
        ]

    # ─────────────────────────────────────────────────────
    # Node-level matching
    # ─────────────────────────────────────────────────────

    def match_to_workflow_nodes_top_k(
        self,
        screenshot_b64: str,
        manual_id: str,
        workflow_graph,
        k: int = 3,
    ) -> List[Tuple[Dict, float]]:
        """Return top-k (node, confidence) tuples by combining top CLIP image
        matches with their page-based node lookup. Useful for LLM reranking."""
        if not self._available:
            return []
        img_matches = self.match_screenshot(screenshot_b64, manual_id, top_k=k * 2)
        if not img_matches:
            return []

        candidates = []
        for node in workflow_graph.get_all_nodes():
            wf_id = node.get("workflow_id", "")
            if manual_id and manual_id not in wf_id:
                continue
            candidates.append(node)
        if not candidates:
            candidates = workflow_graph.get_all_nodes()
        if not candidates:
            return []

        seen_ids: set = set()
        result: List[Tuple[Dict, float]] = []
        for img in img_matches:
            target_page = img.get("page_number")
            target_section = (img.get("section") or "").strip().lower()

            def score(node: Dict):
                page_diff = abs(int(node.get("page") or 0) - int(target_page or 0))
                section_match = 0
                wf_name = (node.get("workflow_id") or "").lower()
                if target_section and target_section.replace(" ", "_") in wf_name:
                    section_match = 1
                return (-section_match, page_diff)

            best = min(candidates, key=score)
            if best["id"] in seen_ids:
                continue
            seen_ids.add(best["id"])
            result.append((best, float(img["similarity"])))
            if len(result) >= k:
                break
        return result

    def match_to_workflow_node(
        self,
        screenshot_b64: str,
        manual_id: str,
        workflow_graph,  # WorkflowGraph instance
    ) -> Tuple[Optional[Dict], float]:
        """Map a screenshot to the best-matching workflow node.

        Strategy: find the top manual image → use (page, section) to locate the
        procedural_step node with the closest page number in the matching workflow.

        Returns (node_dict, confidence). confidence is the CLIP cosine similarity.
        """
        matches = self.match_screenshot(screenshot_b64, manual_id, top_k=1)
        if not matches:
            return None, 0.0
        top = matches[0]
        target_page = top.get("page_number")
        target_section = (top.get("section") or "").strip().lower()

        candidates = []
        for node in workflow_graph.get_all_nodes():
            wf_id = node.get("workflow_id", "")
            # prefer auto-generated workflows bound to this manual
            if manual_id and manual_id not in wf_id:
                continue
            candidates.append(node)

        if not candidates:
            # fall back to all nodes if no manual-bound workflow exists
            candidates = workflow_graph.get_all_nodes()
        if not candidates:
            return None, 0.0

        # Rank by (section match, |page diff|)
        def score(node: Dict):
            page_diff = abs(int(node.get("page") or 0) - int(target_page or 0))
            section_match = 0
            wf_name = (node.get("workflow_id") or "").lower()
            if target_section and target_section.replace(" ", "_") in wf_name:
                section_match = 1
            return (-section_match, page_diff)

        best = min(candidates, key=score)
        return best, float(top["similarity"])


# ─────────────────────────────────────────────────────
# Module-level accessor
# ─────────────────────────────────────────────────────

def get_visual_matcher() -> VisualMatcher:
    global _matcher_singleton
    if _matcher_singleton is None:
        _matcher_singleton = VisualMatcher()
    return _matcher_singleton
