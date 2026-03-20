"""
Graph builder: Extract entities and relationships from text chunks using Gemini.
Builds knowledge graph triplets (subject, relation, object) for Graph RAG.
"""

import json
import os
import re
import concurrent.futures
from typing import List, Tuple

from . import graphstore


EXTRACTION_PROMPT = """You are a geoscience knowledge graph builder. Extract entities and relationships from the given text thoroughly and accurately.

# Entity Types to Extract
- Geological: formations, groups, members, basins, structures (faults, folds), unconformities, stratigraphic units
- Geophysical: seismic horizons, velocity zones, anomaly types, survey parameters
- Spatial: locations, regions, wells, lines, coordinates, depth/time ranges
- Temporal: geological ages, periods, events, deposition timing
- Properties: lithology, porosity, permeability, thickness, fluid content
- Methods: interpretation techniques, processing steps, software tools, workflows
- Concepts: depositional environments, tectonic regimes, petroleum system elements (source, reservoir, seal, trap)

# Relationship Types
Use specific, directional relationships:
- Hierarchy: type_of, part_of, member_of, belongs_to
- Spatial: located_in, overlies, underlies, adjacent_to, contains
- Causal: formed_by, caused_by, results_in, controls
- Property: has_lithology, has_age, has_thickness, has_porosity
- Association: associated_with, correlates_with, indicates, equivalent_to
- Function: used_for, measured_by, detected_by, interpreted_as

# Rules
- Extract 10-25 triplets per chunk — be thorough, capture all meaningful relationships
- ONLY extract relationships that are explicitly stated or directly implied in the text
- Do NOT invent or guess relationships — if unsure, skip it
- Normalize entity names: lowercase, consistent spelling (e.g., always "viking graben" not "Viking graben" sometimes)
- Avoid vague relationships like "related_to" — be specific
- Do NOT create contradictory triplets (e.g., same entity being both "normal fault" and "reverse fault")
- Include multi-hop chains when present (A→B, B→C enables A→C reasoning)

# Output
JSON array only, no explanation:
[
  ["viking graben", "type_of", "extensional rift basin"],
  ["viking graben", "has_age", "jurassic to present"],
  ["brent group", "located_in", "viking graben"],
  ["brent group", "has_lithology", "sandstone"],
  ["brent group", "interpreted_as", "reservoir"],
  ["kimmeridge clay", "overlies", "brent group"],
  ["kimmeridge clay", "interpreted_as", "source rock"]
]

Text to analyze:
{text}

JSON array of triplets:"""


_gemini_client = None


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            return None
        from google import genai
        _gemini_client = genai.Client(api_key=gemini_api_key)
    return _gemini_client


def _extract_triplets_with_gemini(text: str) -> List[Tuple[str, str, str]]:
    """Use Gemini to extract knowledge graph triplets from text."""
    client = _get_gemini_client()
    if not client:
        return []

    try:
        prompt = EXTRACTION_PROMPT.replace("{text}", text[:3000])

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        response_text = response.text.strip()

        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            raw = json.loads(json_match.group())
            triplets = []
            for item in raw:
                if isinstance(item, list) and len(item) == 3:
                    triplets.append((str(item[0]), str(item[1]), str(item[2])))
            return triplets
    except Exception as e:
        print(f"[GRAPH] Triplet extraction failed: {e}")

    return []


def _process_chunk(args: Tuple[str, dict]) -> Tuple[List[Tuple[str, str, str]], str]:
    """Process a single chunk and return triplets + source."""
    text, metadata = args
    source = metadata.get("source", "unknown")
    triplets = _extract_triplets_with_gemini(text)
    return triplets, source


def build_graph_from_chunks(manual_id: str, chunks: List[Tuple[str, dict]]):
    """
    Process text chunks and build a knowledge graph for a manual.
    Uses parallel processing for faster Gemini API calls.
    """
    total_triplets = 0
    max_workers = min(5, len(chunks))  # Up to 5 parallel API calls

    print(f"[GRAPH] Building graph for {manual_id}: {len(chunks)} chunks (parallel={max_workers})")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(_process_chunk, chunks)

        for triplets, source in results:
            if triplets:
                graphstore.add_triplets(manual_id, triplets, chunk_source=source)
                total_triplets += len(triplets)

    stats = graphstore.get_graph_stats(manual_id)
    print(f"[GRAPH] Manual {manual_id}: {total_triplets} triplets extracted, "
          f"{stats['nodes']} nodes, {stats['edges']} edges")
    return stats
