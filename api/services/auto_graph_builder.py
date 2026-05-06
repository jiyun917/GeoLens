"""
Automatic Workflow Graph builder.

Consumes classified chunks from `chunk_classifier.py` and emits workflow JSON
files in the same format as hand-authored workflows under `data/workflows/`.

Strategy:
  1. Group chunks by section.
  2. Sections with < 3 procedural_step chunks are ignored (too thin for a
     workflow — probably narrative or reference material).
  3. Each qualifying section becomes one workflow:
       nodes = procedural_step chunks, ordered by step_order_hint (fallback
               to chunk_index).
       edges = sequential between consecutive steps. A transition_cue chunk
               between two steps with conditional language ("if", "만약",
               "경우", "or") is promoted to a conditional edge.
  4. Each node absorbs nearby supporting chunks (|chunk_index diff| ≤ 3):
       linked_chunks = self + parameter_desc + concept_explanation + ui_description
       parameters    = extracted from parameter_desc.parameters_mentioned
       visual_signature = aggregated ui_elements / nearby_text

Files are saved as:
    data/workflows/auto_{manual_id}__{section_slug}.json

Naming lets deletion glob `auto_{manual_id}*.json` to purge a manual.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple

WORKFLOW_DIR = os.environ.get(
    "WORKFLOW_DATA_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "workflows"),
)

TITLE_MODEL = "gemini-2.5-pro"
TITLE_MAX_RETRIES = 4
TITLE_BASE_BACKOFF = 2.0


def _is_transient_error(err: Exception) -> bool:
    msg = str(err)
    for marker in ("503", "429", "500", "504", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
                   "DEADLINE_EXCEEDED", "timeout", "Timeout", "temporarily"):
        if marker in msg:
            return True
    return False


CONDITIONAL_MARKERS = (
    "if ", "if,", "만약", "경우", " or ", " 또는 ",
    "때에만", "when ", "otherwise",
)

ACTION_VERBS = {
    "click", "select", "open", "choose", "press", "double-click",
    "클릭", "선택", "열기", "누르", "실행",
}
SETUP_VERBS = {
    "set", "configure", "adjust", "enter", "specify", "define", "enable", "disable",
    "설정", "구성", "조정", "입력", "지정", "정의",
}
VERIFY_VERBS = {
    "check", "verify", "review", "confirm", "inspect", "validate",
    "확인", "검증", "검토", "점검",
}

LINK_RADIUS = 3  # chunk_index distance for linked_chunks

MIN_PROCEDURAL_STEPS = 3

_gemini_client = None


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        from google.genai import types as _t
        _gemini_client = genai.Client(
            api_key=api_key,
            http_options=_t.HttpOptions(timeout=60_000),
        )
        return _gemini_client
    except Exception as e:
        print(f"[AUTO_GRAPH] Gemini client init failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# Slug + step_type helpers
# ═══════════════════════════════════════════════════════════

def _slugify(value: str) -> str:
    if not value:
        return "section"
    # Collapse non-alphanumeric to underscores, normalize
    slug = re.sub(r"[^\w\-]+", "_", value, flags=re.UNICODE).strip("_").lower()
    slug = re.sub(r"_+", "_", slug)
    return slug[:40] or "section"


def _step_type_from_verb(verb: str) -> str:
    v = (verb or "").lower().strip()
    if not v:
        return "action"
    if v in ACTION_VERBS:
        return "action"
    if v in SETUP_VERBS:
        return "setup"
    if v in VERIFY_VERBS:
        return "verification"
    # substring fallback
    for s in SETUP_VERBS:
        if s in v:
            return "setup"
    for s in VERIFY_VERBS:
        if s in v:
            return "verification"
    return "action"


def _sentence_head(text: str, max_chars: int = 80) -> str:
    text = (text or "").strip()
    # split on sentence boundaries (., !, ?, 。, 다.)
    m = re.search(r"[.!?。]|다\.", text)
    first = text[:m.end()] if m else text
    first = re.sub(r"\s+", " ", first).strip()
    if len(first) > max_chars:
        first = first[:max_chars].rstrip() + "…"
    return first or "Step"


def _is_conditional_transition(text: str) -> bool:
    low = (text or "").lower()
    return any(marker in low for marker in CONDITIONAL_MARKERS)


# Stopwords we don't want in screenshot_keywords — generic verbs/filler.
_KW_STOPWORDS = frozenset([
    "click", "clicks", "select", "selects", "press", "choose", "open", "opens",
    "close", "closes", "set", "sets", "enter", "enters", "input", "inputs",
    "check", "confirm", "then", "next", "this", "that", "with", "from", "into",
    "have", "been", "will", "would", "could", "should", "must", "also", "same",
    "each", "them", "they", "some", "any", "other", "than", "when", "where",
    "what", "which", "while", "there", "their", "these", "those", "about",
    "above", "after", "before", "below", "between", "during", "under", "just",
    "only", "over", "such", "more", "most", "step", "steps", "default", "data",
    "file", "files", "using", "used", "use", "value", "values", "line", "lines",
    "item", "items", "pair", "button", "field", "menu",
    "클릭", "선택", "누르", "입력", "그리고", "다음", "확인", "버튼", "메뉴",
])


def _keywords_from_step_text(title: str, body: str, max_n: int = 12) -> List[str]:
    """Extract likely UI/noun tokens from a step's title + body.
    - Prefer PascalCase / TitleCase tokens (usually UI labels in manuals)
    - Also include 4+ char lowercase words (filtered by stopwords)
    - Preserve Korean 3+ char nouns as-is
    """
    text = f"{title}  {body}"
    seen = set()
    out: List[str] = []

    # Capitalized / TitleCase tokens (likely UI names)
    for m in re.findall(r"\b[A-Z][a-zA-Z0-9_\-]{1,}\b", text):
        key = m.lower()
        if key in _KW_STOPWORDS or key in seen:
            continue
        seen.add(key)
        out.append(m)
        if len(out) >= max_n:
            return out

    # Lowercase long words (4+ chars)
    for m in re.findall(r"\b[a-z][a-z0-9]{3,}\b", text):
        if m in _KW_STOPWORDS or m in seen:
            continue
        seen.add(m)
        out.append(m)
        if len(out) >= max_n:
            return out

    # Korean nouns (3+ Hangul chars)
    for m in re.findall(r"[가-힣]{3,}", text):
        if m in _KW_STOPWORDS or m in seen:
            continue
        seen.add(m)
        out.append(m)
        if len(out) >= max_n:
            break

    return out


def _json_list_field(metadata: dict, key: str) -> List[str]:
    raw = metadata.get(key)
    if isinstance(raw, list):
        return [str(x) for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(x) for x in parsed if str(x).strip()]
        except Exception:
            # not JSON, treat as single value
            return [raw.strip()]
    return []


# ═══════════════════════════════════════════════════════════
# Main builder
# ═══════════════════════════════════════════════════════════

class AutoGraphBuilder:
    """Generate workflow JSON files from classified chunks."""

    def build_workflow_from_chunks(
        self,
        manual_id: str,
        classified_chunks: List[Tuple[str, dict]],
    ) -> List[Dict]:
        """
        Expects each chunk's metadata to contain:
          - section (str)
          - chunk_index (int, per-section ordering)
          - chunk_role (str, added by chunk_classifier)
          - chunk_id (str, ChromaDB doc id — caller must inject this)
          - page (int, optional)
          - step_order_hint, action_verb, ui_elements (JSON str),
            parameters_mentioned (JSON str), next_step_hint (optional)

        Returns the list of workflow dicts produced (one per qualifying section).
        """
        if not classified_chunks:
            return []

        # 1. group by section
        sections: Dict[str, List[Tuple[str, dict]]] = {}
        for text, meta in classified_chunks:
            section = str(meta.get("section") or "unknown")
            sections.setdefault(section, []).append((text, meta))

        workflows = []
        for section, chunks in sections.items():
            chunks_sorted = sorted(chunks, key=lambda p: p[1].get("chunk_index", 0))
            procedural = [c for c in chunks_sorted if c[1].get("chunk_role") == "procedural_step"]
            if len(procedural) < MIN_PROCEDURAL_STEPS:
                continue

            workflow = self._build_one_workflow(manual_id, section, chunks_sorted, procedural)
            if workflow and workflow.get("nodes"):
                workflows.append(workflow)

        return workflows

    # ────────────────────────────────────────────────────────

    def _build_one_workflow(
        self,
        manual_id: str,
        section: str,
        all_chunks: List[Tuple[str, dict]],
        procedural: List[Tuple[str, dict]],
    ) -> Dict:
        section_slug = _slugify(section)
        workflow_id = f"auto_{manual_id}__{section_slug}"

        # Order procedural steps: step_order_hint if present, else chunk_index
        def _step_key(p: Tuple[str, dict]):
            meta = p[1]
            hint = meta.get("step_order_hint")
            return (hint if isinstance(hint, int) else 10_000, meta.get("chunk_index", 0))

        procedural_sorted = sorted(procedural, key=_step_key)

        # Pre-compute titles in a single Gemini batch (falls back to sentence head)
        titles = self._summarize_titles([text for text, _ in procedural_sorted])

        # Build nodes
        nodes = []
        step_chunk_indices: List[int] = []
        for step_number, (text, meta) in enumerate(procedural_sorted, start=1):
            chunk_index = int(meta.get("chunk_index", 0))
            step_chunk_indices.append(chunk_index)

            linked, parameters = self._collect_linked_chunks(chunk_index, all_chunks, meta)
            visual_sig = self._extract_visual_signature(
                chunk_index, all_chunks,
                step_text=text,
                step_title=titles[step_number - 1] if step_number - 1 < len(titles) else _sentence_head(text),
                action_verb=meta.get("action_verb", ""),
            )

            node_id = f"{workflow_id}_{step_number:02d}"
            title = titles[step_number - 1] if step_number - 1 < len(titles) else _sentence_head(text)
            nodes.append({
                "id": node_id,
                "workflow_id": workflow_id,
                "step_number": step_number,
                "title": title,
                "description": _sentence_head(text, max_chars=200),
                "step_type": _step_type_from_verb(meta.get("action_verb", "")),
                "visual_signature": visual_sig,
                "linked_chunks": linked,
                "parameters": parameters,
                "page": meta.get("page"),
            })

        # Build edges
        edges = self._build_edges(nodes, procedural_sorted, all_chunks)

        return {
            "workflow_id": workflow_id,
            "name": section,
            "description": f"Auto-generated from {manual_id}: {section}",
            "auto_generated": True,
            "source_manual_id": manual_id,
            "nodes": nodes,
            "edges": edges,
        }

    # ────────────────────────────────────────────────────────

    def _collect_linked_chunks(
        self,
        step_chunk_index: int,
        all_chunks: List[Tuple[str, dict]],
        step_meta: dict,
    ) -> Tuple[List[str], List[Dict]]:
        """Find supporting chunks within LINK_RADIUS of step_chunk_index."""
        linked_ids: List[str] = []
        parameters: List[Dict] = []

        self_id = step_meta.get("chunk_id")
        if self_id:
            linked_ids.append(self_id)

        for _, meta in all_chunks:
            role = meta.get("chunk_role")
            if role not in ("parameter_desc", "concept_explanation", "ui_description"):
                continue
            idx = int(meta.get("chunk_index", -9999))
            if abs(idx - step_chunk_index) > LINK_RADIUS:
                continue
            cid = meta.get("chunk_id")
            if cid and cid not in linked_ids:
                linked_ids.append(cid)
            if role == "parameter_desc":
                for param_name in _json_list_field(meta, "parameters_mentioned"):
                    if not any(p.get("name") == param_name for p in parameters):
                        parameters.append({"name": param_name, "default": None, "description": ""})

        return linked_ids, parameters

    # ────────────────────────────────────────────────────────

    def _extract_visual_signature(
        self,
        step_chunk_index: int,
        all_chunks: List[Tuple[str, dict]],
        step_text: str = "",
        step_title: str = "",
        action_verb: str = "",
    ) -> Dict:
        """Build screenshot_keywords by combining:
          - ui_elements from nearby ui_description chunks
          - action verb + noun tokens from the step's own title/description
          - Capitalized terms in the step text (likely UI labels)
        """
        ui_elements: List[str] = []
        keywords: List[str] = []
        expected_dialog = ""

        for _, meta in all_chunks:
            if meta.get("chunk_role") != "ui_description":
                continue
            idx = int(meta.get("chunk_index", -9999))
            if abs(idx - step_chunk_index) > LINK_RADIUS:
                continue
            for el in _json_list_field(meta, "ui_elements"):
                if el not in ui_elements:
                    ui_elements.append(el)
                keywords.append(el)
                if not expected_dialog and any(k in el.lower() for k in ("window", "dialog", "panel", "창")):
                    expected_dialog = el

        # Pull title + text tokens as fallback signal (always present)
        for kw in _keywords_from_step_text(step_title, step_text):
            if kw not in keywords:
                keywords.append(kw)
        if action_verb:
            av = action_verb.strip().lower()
            if av and av not in keywords:
                keywords.append(av)

        return {
            "expected_dialog": expected_dialog,
            "expected_ui_elements": ui_elements[:10],
            "screenshot_keywords": list(dict.fromkeys(keywords))[:15],
        }

    # ────────────────────────────────────────────────────────

    def _build_edges(
        self,
        nodes: List[Dict],
        procedural_sorted: List[Tuple[str, dict]],
        all_chunks: List[Tuple[str, dict]],
    ) -> List[Dict]:
        """Sequential edges between consecutive steps, upgraded to conditional when a
        transition_cue chunk between them carries branching language."""
        edges = []
        for i in range(len(nodes) - 1):
            src_node = nodes[i]
            tgt_node = nodes[i + 1]
            src_idx = procedural_sorted[i][1].get("chunk_index", 0)
            tgt_idx = procedural_sorted[i + 1][1].get("chunk_index", 0)

            # find transition_cue between the two step chunks
            between = [
                (text, meta) for text, meta in all_chunks
                if meta.get("chunk_role") == "transition_cue"
                and src_idx < int(meta.get("chunk_index", -1)) < tgt_idx
            ]
            edge_type = "sequential"
            instruction = ""
            condition = None
            if between:
                cue_text, cue_meta = between[0]
                instruction = cue_meta.get("next_step_hint") or _sentence_head(cue_text, max_chars=120)
                if _is_conditional_transition(cue_text):
                    edge_type = "conditional"
                    condition = "conditional_transition"

            edges.append({
                "source": src_node["id"],
                "target": tgt_node["id"],
                "edge_type": edge_type,
                "condition": condition,
                "instruction": instruction,
            })
        return edges

    # ────────────────────────────────────────────────────────

    def _summarize_titles(self, step_texts: List[str]) -> List[str]:
        """Optionally use Gemini to generate short titles; fallback to first sentence."""
        fallback = [_sentence_head(t, max_chars=60) for t in step_texts]
        client = _get_gemini_client()
        if not client or not step_texts:
            return fallback

        blocks = []
        for i, t in enumerate(step_texts, start=1):
            trimmed = t.strip()
            if len(trimmed) > 500:
                trimmed = trimmed[:500] + "…"
            blocks.append(f'Step {i}:\n"""\n{trimmed}\n"""')
        prompt = (
            "For each procedural step below, write a concise title (max 10 words) "
            "capturing the user's action. Respond as a JSON array of strings in the "
            "same order as input. No extra prose.\n\n"
            + "\n\n".join(blocks)
            + "\n\nTitles JSON:"
        )

        from google.genai import types
        import time as _time, random as _random

        cfg = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0,
        )

        raw = ""
        last_err: Exception = RuntimeError("never attempted")
        for attempt in range(TITLE_MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=TITLE_MODEL,
                    contents=prompt,
                    config=cfg,
                )
                raw = (response.text or "").strip()
                if attempt > 0:
                    print(f"[AUTO_GRAPH] title summarization recovered on retry {attempt}")
                break
            except Exception as e:
                last_err = e
                if attempt >= TITLE_MAX_RETRIES or not _is_transient_error(e):
                    break
                delay = TITLE_BASE_BACKOFF * (2 ** attempt) + _random.uniform(0, 1.0)
                print(f"[AUTO_GRAPH] title transient error ({e.__class__.__name__}); "
                      f"retry {attempt + 1}/{TITLE_MAX_RETRIES} after {delay:.1f}s")
                _time.sleep(delay)

        if not raw:
            print(f"[AUTO_GRAPH] title summarization failed after {TITLE_MAX_RETRIES + 1} attempts: {last_err}")
            return fallback

        try:
            parsed = json.loads(raw)
        except Exception:
            return fallback
        if isinstance(parsed, list) and len(parsed) == len(step_texts):
            cleaned = []
            for i, v in enumerate(parsed):
                s = str(v).strip()
                cleaned.append(s if s else fallback[i])
            return cleaned
        return fallback


# ═══════════════════════════════════════════════════════════
# Disk IO helpers
# ═══════════════════════════════════════════════════════════

def save_workflows(workflows: List[Dict]) -> List[str]:
    """Write each workflow dict to `data/workflows/{workflow_id}.json` and return the paths."""
    os.makedirs(WORKFLOW_DIR, exist_ok=True)
    paths = []
    for wf in workflows:
        wid = wf.get("workflow_id")
        if not wid:
            continue
        path = os.path.join(WORKFLOW_DIR, f"{wid}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(wf, f, ensure_ascii=False, indent=2)
        paths.append(path)
    return paths


def delete_auto_workflows(manual_id: str) -> int:
    """Remove every auto-generated workflow JSON belonging to a manual. Returns count deleted."""
    import glob
    pattern = os.path.join(WORKFLOW_DIR, f"auto_{manual_id}__*.json")
    removed = 0
    for path in glob.glob(pattern):
        try:
            os.remove(path)
            removed += 1
        except Exception as e:
            print(f"[AUTO_GRAPH] failed to delete {path}: {e}")
    return removed
