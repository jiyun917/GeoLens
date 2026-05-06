"""
Graph builder: Extract entities and relationships from text chunks using Gemini.
Supports two graph types:
  - geoscience: geological entities and relationships (for research papers, geological data)
  - software: UI workflows, menu paths, prerequisites (for software manuals)
Auto-detects content type from the first few chunks.
"""

import json
import os
import re
import concurrent.futures
from typing import List, Tuple, Optional

from . import graphstore


# ═══════════════════════════════════════════════════════════
# Extraction Prompts
# ═══════════════════════════════════════════════════════════

GEOSCIENCE_PROMPT = """You are a geoscience knowledge graph builder. Extract entities and relationships from the given text thoroughly and accurately.

# Entity Types to Extract
- Geological: formations, groups, members, basins, structures (faults, folds), unconformities, stratigraphic units
- Geophysical: seismic horizons, velocity zones, anomaly types, survey parameters
- Spatial: locations, regions, wells, lines, coordinates, depth/time ranges
- Temporal: geological ages, periods, events, deposition timing
- Properties: lithology, porosity, permeability, thickness, fluid content
- Methods: interpretation techniques, processing steps, software tools, workflows
- Concepts: depositional environments, tectonic regimes, petroleum system elements (source, reservoir, seal, trap)

# Relationship Types
- Hierarchy: type_of, part_of, member_of, belongs_to
- Spatial: located_in, overlies, underlies, adjacent_to, contains
- Causal: formed_by, caused_by, results_in, controls
- Property: has_lithology, has_age, has_thickness, has_porosity
- Association: associated_with, correlates_with, indicates, equivalent_to
- Function: used_for, measured_by, detected_by, interpreted_as

# Rules
- Extract 10-25 triplets per chunk
- ONLY extract relationships explicitly stated or directly implied in the text
- Normalize entity names: lowercase, consistent spelling
- Avoid vague relationships like "related_to"
- Include multi-hop chains when present (A→B, B→C)

# Output
JSON array only:
[["viking graben", "type_of", "extensional rift basin"], ["brent group", "located_in", "viking graben"]]

Text to analyze:
{text}

JSON array of triplets:"""


SOFTWARE_PROMPT = """You are a software workflow knowledge graph builder. Extract UI elements, actions, workflows, and their relationships from the given software manual text.

# Entity Types to Extract
- UI Elements: menus, buttons, icons, toolbars, panels, dialogs, wizards, tabs, trees, fields
- Actions: click, select, import, export, display, configure, create, delete, add, remove
- Data Types: files, formats (SEG-Y, LAS, DLIS), volumes, surfaces, wells, horizons, attributes
- Workflows: procedures, steps, processes, pipelines, sequences
- Concepts: projects, surveys, scenes, views (2D, 3D), displays, settings, preferences
- Conditions: prerequisites, requirements, states, modes

# Relationship Types
- Navigation: menu_path (parent menu → child item), located_in (element → panel/toolbar), contains
- Workflow: next_step, requires, prerequisite_for, results_in, part_of_workflow
- Action: action_on (action → target), opens (click → dialog), triggers, enables
- Data: input_for, output_of, format_of, displays, loads, imports, exports
- State: requires_state, enables_when, disabled_when, depends_on

# Rules
- Extract 10-25 triplets per chunk
- Capture menu navigation paths: "File menu" → contains → "Import submenu" → contains → "SEG-Y option"
- Capture workflow sequences: "step 1" → next_step → "step 2"
- Capture prerequisites: "inline display" → requires → "loaded 3D volume"
- Normalize names: lowercase, use exact UI labels when available
- Include keyboard shortcuts if mentioned

# Output
JSON array only:
[["survey menu", "contains", "import submenu"], ["seg-y import", "requires", "survey setup"], ["inline display", "requires", "loaded 3d volume"], ["add default data", "action_on", "seismic display"]]

Text to analyze:
{text}

JSON array of triplets:"""


# ═══════════════════════════════════════════════════════════
# Content Type Detection
# ═══════════════════════════════════════════════════════════

SOFTWARE_KEYWORDS = [
    "click", "menu", "button", "dialog", "toolbar", "icon", "tab", "panel",
    "wizard", "dropdown", "checkbox", "select", "window", "interface",
    "screenshot", "cursor", "right-click", "double-click", "drag",
    "file menu", "settings", "preferences", "install", "setup",
    "user guide", "manual", "tutorial", "how to", "step by step",
]

GEOSCIENCE_KEYWORDS = [
    "fault", "horizon", "seismic", "well", "formation", "basin",
    "stratigraphy", "lithology", "reservoir", "porosity", "permeability",
    "graben", "anticline", "syncline", "unconformity", "deposit",
    "tectonic", "sediment", "geophysical", "velocity", "amplitude",
    "reflection", "refraction", "gravity", "magnetic", "resistivity",
]


def detect_content_type(chunks: List[Tuple[str, dict]], sample_size: int = 10) -> str:
    """
    Auto-detect whether content is software manual or geoscience document.
    Returns 'software' or 'geoscience'.
    """
    sample_text = " ".join(
        chunk[:500] for chunk, _ in chunks[:sample_size]
    ).lower()

    sw_score = sum(1 for kw in SOFTWARE_KEYWORDS if kw in sample_text)
    geo_score = sum(1 for kw in GEOSCIENCE_KEYWORDS if kw in sample_text)

    detected = "software" if sw_score > geo_score else "geoscience"
    print(f"[GRAPH] Content type detection: software={sw_score}, geoscience={geo_score} → {detected}")
    return detected


# ═══════════════════════════════════════════════════════════
# Extraction
# ═══════════════════════════════════════════════════════════

_gemini_client = None

TRIPLET_MAX_RETRIES = 4
TRIPLET_BASE_BACKOFF = 2.0


def _is_transient_error(err: Exception) -> bool:
    msg = str(err)
    for marker in ("503", "429", "500", "504", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
                   "DEADLINE_EXCEEDED", "timeout", "Timeout", "temporarily"):
        if marker in msg:
            return True
    return False


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            return None
        from google import genai
        from google.genai import types as _t
        _gemini_client = genai.Client(
            api_key=gemini_api_key,
            http_options=_t.HttpOptions(timeout=60_000),
        )
    return _gemini_client


def _extract_triplets(text: str, prompt_template: str) -> List[Tuple[str, str, str]]:
    """Extract triplets using the given prompt template, with retry on transient errors."""
    client = _get_gemini_client()
    if not client:
        return []

    import time as _time, random as _random
    prompt = prompt_template.replace("{text}", text[:3000])
    response_text = ""
    last_err: Exception = RuntimeError("never attempted")
    for attempt in range(TRIPLET_MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
            )
            response_text = (response.text or "").strip()
            if attempt > 0:
                print(f"[GRAPH] Triplet extraction recovered on retry {attempt}")
            break
        except Exception as e:
            last_err = e
            if attempt >= TRIPLET_MAX_RETRIES or not _is_transient_error(e):
                break
            delay = TRIPLET_BASE_BACKOFF * (2 ** attempt) + _random.uniform(0, 1.0)
            print(f"[GRAPH] Triplet transient error ({e.__class__.__name__}); "
                  f"retry {attempt + 1}/{TRIPLET_MAX_RETRIES} after {delay:.1f}s")
            _time.sleep(delay)

    if not response_text:
        print(f"[GRAPH] Triplet extraction failed after {TRIPLET_MAX_RETRIES + 1} attempts: {last_err}")
        return []

    try:
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            raw = json.loads(json_match.group())
            triplets = []
            for item in raw:
                if isinstance(item, list) and len(item) == 3:
                    triplets.append((str(item[0]), str(item[1]), str(item[2])))
            return triplets
    except Exception as e:
        print(f"[GRAPH] Triplet parse failed: {e}")

    return []


def _process_chunk_with_prompt(args):
    """Process a single chunk with the specified prompt."""
    text, metadata, prompt_template = args
    source = metadata.get("source", "unknown")
    triplets = _extract_triplets(text, prompt_template)
    return triplets, source


# ═══════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════

def build_graph_from_chunks(
    manual_id: str,
    chunks: List[Tuple[str, dict]],
    content_type: Optional[str] = None,
):
    """
    Process text chunks and build a knowledge graph for a manual.
    Auto-detects content type if not specified.
    """
    if not chunks:
        return {"nodes": 0, "edges": 0}

    # Auto-detect content type
    if content_type is None:
        content_type = detect_content_type(chunks)

    prompt_template = SOFTWARE_PROMPT if content_type == "software" else GEOSCIENCE_PROMPT
    print(f"[GRAPH] Building {content_type} graph for {manual_id}: {len(chunks)} chunks")

    total_triplets = 0
    max_workers = min(5, len(chunks))

    # Prepare args with prompt template
    chunk_args = [(text, meta, prompt_template) for text, meta in chunks]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(_process_chunk_with_prompt, chunk_args)

        for triplets, source in results:
            if triplets:
                graphstore.add_triplets(manual_id, triplets, chunk_source=source)
                total_triplets += len(triplets)

    stats = graphstore.get_graph_stats(manual_id)
    print(f"[GRAPH] Manual {manual_id} ({content_type}): {total_triplets} triplets, "
          f"{stats['nodes']} nodes, {stats['edges']} edges")
    return stats
