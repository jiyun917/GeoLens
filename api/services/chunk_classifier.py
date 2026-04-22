"""
Chunk role classifier.

Classifies each chunk into one of 6 procedural roles and extracts structural
metadata (action verbs, UI elements, parameter names, step ordering cues).
Results are attached to chunk metadata and persisted with ChromaDB so the
downstream workflow-graph builder and guide pipeline can reason over them.

Gemini 2.5 Flash is used for cost efficiency, with 5 chunks per API call.
Classification failures default to "general" so the embedding pipeline
never blocks.
"""

import json
import os
import re
from typing import List, Tuple

ROLES = (
    "procedural_step",
    "parameter_desc",
    "concept_explanation",
    "transition_cue",
    "ui_description",
    "general",
)

BATCH_SIZE = 5
MAX_CHUNK_CHARS = 2000  # trim very long chunks before sending to Gemini

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        _client = genai.Client(api_key=api_key)
        return _client
    except Exception as e:
        print(f"[CLASSIFIER] Gemini client init failed: {e}")
        return None


def _default_result() -> dict:
    return {
        "role": "general",
        "step_order_hint": None,
        "action_verb": "",
        "ui_elements": [],
        "parameters_mentioned": [],
        "next_step_hint": "",
        "confidence": 0.0,
    }


BATCH_PROMPT = """You are analyzing chunks of software-manual text and classifying each by procedural role.

Roles (choose exactly ONE per chunk):
- procedural_step: A concrete user action to perform (e.g. "Click OK", "Select Horizon from the Tracking menu").
- parameter_desc: Describes a parameter's meaning, default, or recommended range (e.g. "Correlation Threshold: 0.7~0.95 recommended").
- concept_explanation: Theory, method, algorithm, or principle explanation.
- transition_cue: Connective phrasing that marks progression to the next step (e.g. "Once configured, proceed to...", "이후 Auto-track을 실행합니다").
- ui_description: Describes UI elements, menus, dialogs, or their layout.
- general: None of the above.

For each chunk also extract:
- step_order_hint: integer parsed from ordering cues ("Step 3", "3.", "셋째", "First"=1, "다음으로"=null) or null.
- action_verb: the primary verb for procedural_step in lowercase, else "".
- ui_elements: list of UI element/menu/button/dialog names mentioned (strings).
- parameters_mentioned: list of parameter names mentioned (strings).
- next_step_hint: if transition_cue, short phrase describing the next step, else "".
- confidence: your classification confidence in [0, 1].

Return a JSON array with one object per chunk, in the same order as the input. No extra prose.

Input chunks:
{chunks_block}

Output JSON array:"""


def _call_gemini_batch(chunk_texts: List[str]) -> List[dict]:
    """Classify up to BATCH_SIZE chunks in one Gemini call. Returns one dict per input chunk."""
    client = _get_client()
    if not client:
        return [_default_result() for _ in chunk_texts]

    # Build the chunks block
    blocks = []
    for i, text in enumerate(chunk_texts, start=1):
        trimmed = text.strip()
        if len(trimmed) > MAX_CHUNK_CHARS:
            trimmed = trimmed[:MAX_CHUNK_CHARS] + "…"
        blocks.append(f'Chunk {i}:\n"""\n{trimmed}\n"""')
    chunks_block = "\n\n".join(blocks)
    prompt = BATCH_PROMPT.replace("{chunks_block}", chunks_block)

    try:
        from google.genai import types
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0,
            ),
        )
        raw_text = (response.text or "").strip()
    except Exception as e:
        print(f"[CLASSIFIER] Gemini call failed: {e}")
        return [_default_result() for _ in chunk_texts]

    # Parse JSON array (tolerate surrounding text)
    try:
        parsed = json.loads(raw_text)
    except Exception:
        match = re.search(r"\[.*\]", raw_text, re.DOTALL)
        if not match:
            return [_default_result() for _ in chunk_texts]
        try:
            parsed = json.loads(match.group())
        except Exception:
            return [_default_result() for _ in chunk_texts]

    if not isinstance(parsed, list):
        return [_default_result() for _ in chunk_texts]

    results = []
    for i in range(len(chunk_texts)):
        item = parsed[i] if i < len(parsed) and isinstance(parsed[i], dict) else {}
        results.append(_normalize_result(item))
    return results


def _normalize_result(item: dict) -> dict:
    role = item.get("role", "general")
    if role not in ROLES:
        role = "general"

    step_hint = item.get("step_order_hint")
    if isinstance(step_hint, (int, float)):
        step_hint = int(step_hint)
    elif isinstance(step_hint, str) and step_hint.strip().isdigit():
        step_hint = int(step_hint.strip())
    else:
        step_hint = None

    def _str_list(v) -> List[str]:
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str) and v.strip():
            return [v.strip()]
        return []

    confidence = item.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except Exception:
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    return {
        "role": role,
        "step_order_hint": step_hint,
        "action_verb": str(item.get("action_verb", "") or "").strip().lower(),
        "ui_elements": _str_list(item.get("ui_elements")),
        "parameters_mentioned": _str_list(item.get("parameters_mentioned")),
        "next_step_hint": str(item.get("next_step_hint", "") or "").strip(),
        "confidence": confidence,
    }


def _apply_to_metadata(metadata: dict, result: dict) -> dict:
    """Merge classification result into chunk metadata.

    ChromaDB metadata must be flat scalars, so list fields are JSON-serialized.
    Callers that need the list form should json.loads() on read.
    """
    new_meta = {**metadata, "chunk_role": result["role"]}
    if result["step_order_hint"] is not None:
        new_meta["step_order_hint"] = result["step_order_hint"]
    if result["action_verb"]:
        new_meta["action_verb"] = result["action_verb"]
    if result["ui_elements"]:
        new_meta["ui_elements"] = json.dumps(result["ui_elements"], ensure_ascii=False)
    if result["parameters_mentioned"]:
        new_meta["parameters_mentioned"] = json.dumps(result["parameters_mentioned"], ensure_ascii=False)
    if result["next_step_hint"]:
        new_meta["next_step_hint"] = result["next_step_hint"]
    if result["confidence"]:
        new_meta["classification_confidence"] = result["confidence"]
    return new_meta


class ChunkClassifier:
    """Classify chunks individually or in batches."""

    def classify_chunk(self, chunk_text: str, metadata: dict) -> Tuple[str, dict]:
        results = _call_gemini_batch([chunk_text])
        return chunk_text, _apply_to_metadata(metadata, results[0])

    def classify_batch(self, chunks: List[Tuple[str, dict]]) -> List[Tuple[str, dict]]:
        """Classify many (text, metadata) pairs. Groups into BATCH_SIZE-sized API calls."""
        if not chunks:
            return []

        out: List[Tuple[str, dict]] = []
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            texts = [c[0] for c in batch]
            try:
                results = _call_gemini_batch(texts)
            except Exception as e:
                print(f"[CLASSIFIER] batch {i // BATCH_SIZE} failed: {e}")
                results = [_default_result() for _ in texts]
            if len(results) != len(batch):
                # pad/truncate for safety
                results = (results + [_default_result()] * len(batch))[:len(batch)]
            for (text, metadata), result in zip(batch, results):
                out.append((text, _apply_to_metadata(metadata, result)))

        try:
            counts = {}
            for _, m in out:
                r = m.get("chunk_role", "general")
                counts[r] = counts.get(r, 0) + 1
            print(f"[CLASSIFIER] classified {len(out)} chunks: {counts}")
        except Exception:
            pass

        return out
