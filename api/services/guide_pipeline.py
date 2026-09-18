"""
Guide Mode State-Aware RAG Pipeline.
Combines:
  - Screenshot visual analysis (Gemini)
  - Workflow graph localization (current node matching)
  - Next-step retrieval (graph + vector)
  - Correction logic (handle skipped steps, wrong workflow)
"""

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple

from .workflow_graph import WorkflowGraph, get_workflow_graph
from .graph_retriever import GraphRetriever, get_graph_retriever
from . import stage_timer


def _timed_call(stage: str, fn, *args, **kwargs):
    with stage_timer.timed(stage):
        return fn(*args, **kwargs)


# Rerank confidence gate. When the LLM rerank picks a node with confidence
# below this threshold, we treat the match as unreliable and fall back to
# vector-only retrieval (no graph_context, no next_nodes, no post-completion
# override). This exists because a low-confidence graph pick actively poisons
# the context with the wrong workflow's chunks — worse than pure vector RAG.
# v3: calibrated on the OpendTect development set (env override for the
# calibration sweep; the frozen value is written into run_v3.sh).
CONFIDENCE_THRESHOLD = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.7"))
# v3: goal-query vector retrieval runs in a worker thread while the vision
# call and localization run (it does not depend on the screenshot).
PARALLEL_RETRIEVAL = os.environ.get("PARALLEL_RETRIEVAL", "1") != "0"


# Module-level scratch space, populated by process_guide_request() on each
# call so downstream benchmarking code can read what routing did without
# threading extra return values through every backend signature. Mirrors
# the _LAST_USAGE pattern in bench_backends.py.
_LAST_LOCALIZE_META: Dict[str, Any] = {
    "confidence": 0.0,
    "picked_node_id": None,
    "picked_workflow_id": None,
    "match_method": "",
    "fallback_activated": False,
    "threshold": CONFIDENCE_THRESHOLD,
}


def get_last_localize_meta() -> Dict[str, Any]:
    return dict(_LAST_LOCALIZE_META)


def reset_last_localize_meta() -> None:
    _LAST_LOCALIZE_META.update({
        "confidence": 0.0,
        "picked_node_id": None,
        "picked_workflow_id": None,
        "match_method": "",
        "fallback_activated": False,
        "threshold": CONFIDENCE_THRESHOLD,
    })


def _set_localize_meta(node: Optional[Dict], confidence: float, method: str) -> None:
    """Record the localization outcome. Called from localize_to_graph() itself
    (v3) so every backend that localizes — full_system AND state_path — leaves
    routing telemetry; process_guide_request() then overlays the fallback
    flag. In v2 only process_guide_request() wrote this, so state_path's
    240 unified4 steps carry no routing telemetry."""
    node = node or {}
    _LAST_LOCALIZE_META.update({
        "confidence": float(confidence or 0.0),
        "picked_node_id": node.get("id"),
        "picked_workflow_id": node.get("workflow_id"),
        "match_method": method,
        "fallback_activated": False,
        "threshold": CONFIDENCE_THRESHOLD,
    })


# ─── Auxiliary-call usage accounting (v3) ──────────────────────────────
# Every Gemini Flash call the pipeline makes on behalf of a request (vision
# state extraction, LLM rerank) is appended here. The bench evaluator resets
# it before each step and reads it afterwards, so auxiliary cost is reported
# next to generator cost. The unified2/3/4 logs did not record these calls.
# Pricing mirrors bench_backends.MODEL_PRICING (2026-07 base rates); thinking
# tokens are billed at the output rate.
_AUX_PRICING: Dict[str, Dict[str, float]] = {
    "gemini-2.5-flash": {"in_per_m": 0.30, "out_per_m": 2.50},
}
_AUX_USAGE: Dict[str, Any] = {"calls": []}

# Thinking budget for the two auxiliary Flash calls. v2 left thinking_config
# unset (model default = dynamic thinking, ~650 / ~1,600 thinking tokens per
# vision / rerank call in a 2026-09-17 probe). v3 default 0 = thinking off;
# AUX_THINKING_BUDGET=-1 restores the model default for A/B checks.
def _aux_thinking_config(types_mod):
    raw = os.environ.get("AUX_THINKING_BUDGET", "0").strip()
    try:
        budget = int(raw)
    except ValueError:
        return None
    if budget < 0:
        return None
    try:
        return types_mod.ThinkingConfig(thinking_budget=budget)
    except Exception:
        return None


def record_aux_usage(kind: str, model: str, usage_metadata: Any,
                     latency_sec: float = 0.0) -> None:
    if usage_metadata is None:
        return
    pt = int(getattr(usage_metadata, "prompt_token_count", 0) or 0)
    ct = int(getattr(usage_metadata, "candidates_token_count", 0) or 0)
    tt = getattr(usage_metadata, "thoughts_token_count", None)
    if tt is None:
        total = int(getattr(usage_metadata, "total_token_count", 0) or 0)
        tt = max(0, total - pt - ct)
    tt = int(tt or 0)
    price = _AUX_PRICING.get(model, {"in_per_m": 0.0, "out_per_m": 0.0})
    cost = (pt / 1_000_000) * price["in_per_m"] + ((ct + tt) / 1_000_000) * price["out_per_m"]
    _AUX_USAGE["calls"].append({
        "kind": kind, "model": model,
        "input_tokens": pt, "output_tokens": ct, "thoughts_tokens": tt,
        "cost_usd": round(cost, 6),
        "latency_sec": round(float(latency_sec or 0.0), 3),
    })


# usage_metadata of the vision call that produced each cached visual_state,
# replayed on cache hits so every request is charged for its own vision call.
_VISUAL_STATE_USAGE: Dict[str, Dict[str, int]] = {}


def _usage_snapshot(usage_metadata: Any) -> Dict[str, int]:
    if usage_metadata is None:
        return {}
    pt = int(getattr(usage_metadata, "prompt_token_count", 0) or 0)
    ct = int(getattr(usage_metadata, "candidates_token_count", 0) or 0)
    tt = getattr(usage_metadata, "thoughts_token_count", None)
    if tt is None:
        total = int(getattr(usage_metadata, "total_token_count", 0) or 0)
        tt = max(0, total - pt - ct)
    return {"prompt_token_count": pt, "candidates_token_count": ct, "thoughts_token_count": int(tt or 0)}


class _UsageLike:
    def __init__(self, d: Dict[str, int]):
        self.prompt_token_count = d.get("prompt_token_count", 0)
        self.candidates_token_count = d.get("candidates_token_count", 0)
        self.thoughts_token_count = d.get("thoughts_token_count", 0)
        self.total_token_count = self.prompt_token_count + self.candidates_token_count + self.thoughts_token_count


def _replay_cached_usage(cache_key: str) -> None:
    snap = _VISUAL_STATE_USAGE.get(cache_key)
    if snap:
        # Tokens AND wall-clock of the original vision call are replayed so
        # a backend served from the in-process cache is charged the same
        # latency it would pay in production (evaluator adds
        # replayed_latency_sec to the measured wall-clock).
        record_aux_usage("vision_cached", "gemini-2.5-flash", _UsageLike(snap),
                         latency_sec=float(snap.get("latency_sec", 0.0) or 0.0))
        stage_timer.record("vision_replayed", float(snap.get("latency_sec", 0.0) or 0.0))


def get_aux_usage() -> Dict[str, Any]:
    calls = list(_AUX_USAGE["calls"])
    by_kind: Dict[str, int] = {}
    for c in calls:
        by_kind[c["kind"]] = by_kind.get(c["kind"], 0) + 1
    return {
        "calls": len(calls),
        "input_tokens": sum(c["input_tokens"] for c in calls),
        "output_tokens": sum(c["output_tokens"] for c in calls),
        "thoughts_tokens": sum(c["thoughts_tokens"] for c in calls),
        "cost_usd": round(sum(c["cost_usd"] for c in calls), 6),
        "by_kind": by_kind,
        "latency_sec": round(sum(c.get("latency_sec", 0.0) for c in calls), 3),
        "replayed_latency_sec": round(sum(c.get("latency_sec", 0.0) for c in calls
                                        if c["kind"] == "vision_cached"), 3),
    }


def reset_aux_usage() -> None:
    _AUX_USAGE["calls"] = []


# Screenshot-content-addressed cache for recognize_visual_state results.
# Keyed by SHA-256 of raw decoded image bytes so identical screenshots hit
# the cache regardless of base64 padding or data-URL prefix. Bounded via
# _CACHE_MAX_ENTRIES to guard against long-running processes leaking memory.
_VISUAL_STATE_CACHE: Dict[str, Dict] = {}
_VISUAL_STATE_CACHE_STATS: Dict[str, int] = {"hits": 0, "misses": 0}
_CACHE_MAX_ENTRIES = 512


def get_visual_state_cache_stats() -> Dict[str, int]:
    total = _VISUAL_STATE_CACHE_STATS["hits"] + _VISUAL_STATE_CACHE_STATS["misses"]
    return {
        "hits": _VISUAL_STATE_CACHE_STATS["hits"],
        "misses": _VISUAL_STATE_CACHE_STATS["misses"],
        "size": len(_VISUAL_STATE_CACHE),
        "hit_rate": (_VISUAL_STATE_CACHE_STATS["hits"] / total) if total else 0.0,
    }


def reset_visual_state_cache() -> None:
    _VISUAL_STATE_CACHE.clear()
    _VISUAL_STATE_CACHE_STATS["hits"] = 0
    _VISUAL_STATE_CACHE_STATS["misses"] = 0


SOFTWARE_PROFILES = {
    "opendtect": {
        "display_name": "OpendTect geophysics software",
        "data_state_example": "3D seismic loaded",
    },
    "qgis": {
        "display_name": "QGIS geographic information system",
        "data_state_example": "vector layers loaded",
    },
}

_ACTIVE_SOFTWARE_ID = os.environ.get("GEOLENS_SOFTWARE_ID", "opendtect").lower()

# v3 development-loop knobs (all applied identically to every backend)
VISION_PROMPT_VERSION = os.environ.get("VISION_PROMPT_VERSION", "v3").lower()   # v2 | v3 (verbatim strings)
ROUTER_POOL_K = int(os.environ.get("ROUTER_POOL_K", "5"))                          # candidates per scorer
# v3: successors of the last confirmed node join the pool and are flagged
# to the rerank as expected-next (ROUTER_GRAPH_PRIOR=0 disables).
ROUTER_GRAPH_PRIOR = os.environ.get("ROUTER_GRAPH_PRIOR", "1") != "0"
# v3: how a re-matched node is rendered in the context (override = v2 dismiss
# override at the top of the context; soft = continue-with-next-action note; off).
POST_COMPLETION_MODE = os.environ.get("POST_COMPLETION_MODE", "soft").strip().lower()
# v3 rerank prompt (calibrated confidence bands, session context); v2 = the
# unified4 prompt with the 'bias toward picking' decision rule.
RERANK_PROMPT_VERSION = os.environ.get("RERANK_PROMPT_VERSION", "v3").strip().lower()

_RERANK_RULE_V2 = """DECISION RULE — bias toward PICKING a candidate:
- If ANY candidate's title/description shares the dialog name, screen name, or topic with the visual_state, PICK that candidate. Confidence in [0.5, 0.9] is fine for partial matches; use higher only when title essentially names what's on screen.
- Returning "none" is ONLY for cases where NO candidate is even loosely related (different application, different module, totally unrelated topic).
- Picking a slightly-imperfect candidate is better than "none", because downstream logic uses the picked node for state tracking (post-completion detection, next-step hints). Returning "none" disables those."""

_RERANK_WIZARD_V2 = """IMPORTANT — wizard dialogs stay on screen after their action completes:
- If the screenshot still looks like a candidate the user ALREADY completed (see "Already-completed" list above), they are NOT re-doing it. The wizard just hasn't been dismissed yet.
- In that case, prefer a NEXT candidate in the same workflow, OR (if no next exists) STILL pick the visited candidate — downstream code will detect post-completion from that match."""

_RERANK_WIZARD_V3 = """NOTE — multi-action steps and dialogs that stay open:
- A step may cover several actions. If the screen still shows that step's dialog and the instructions already given do not cover all of its actions, pick that step AGAIN (do not skip ahead).
- If the instructions already given complete the step and the screen is unchanged, prefer the NEXT step of the same workflow; if none fits, still pick the current step."""

_RERANK_RULE_V3 = """DECISION RULE:
- Compare the EXACT on-screen strings in visual_state (window/dialog titles, button and field labels, tree entries) with each candidate's dialog/elements/keywords. A candidate whose expected dialog or elements literally appear on screen is a strong match.
- Prefer a candidate from the same workflow as the session's previous steps and the graph prior, unless the screen clearly shows a different application module.
- Return "none" when NO candidate is even loosely related (different application, different module, totally unrelated topic), or when every related candidate is already completed and no successor fits.

CONFIDENCE CALIBRATION (used as a gate: below {thr} the pick is discarded):
- 0.9–1.0: the candidate's expected dialog title or its specific elements are literally on screen AND it fits the goal/session.
- 0.7–0.85: same workflow and topic, screen consistent, but no literal dialog/element evidence.
- 0.5–0.65: plausible topic only — the screen could belong to another workflow. Use this when unsure; do NOT inflate."""
FALLBACK_CTX_CHARS = int(os.environ.get("FALLBACK_CTX_CHARS", "3900"))            # vector-only context when not routed (= vanilla_budget)
VECTOR_CTX_CHARS = int(os.environ.get("VECTOR_CTX_CHARS", "1500"))                # auxiliary vector context when routed
GRAPH_CTX_CHARS = int(os.environ.get("GRAPH_CTX_CHARS", "800"))                   # per linked-chunk block when routed
GRAPH_CTX_ITEMS = int(os.environ.get("GRAPH_CTX_ITEMS", "3"))


def get_active_software_id() -> str:
    return os.environ.get("GEOLENS_SOFTWARE_ID", "opendtect").lower()


def _build_visual_state_prompt(software_id: str) -> str:
    profile = SOFTWARE_PROFILES.get(software_id, SOFTWARE_PROFILES["opendtect"])
    name = profile["display_name"]
    ex = profile["data_state_example"]
    if VISION_PROMPT_VERSION == "v2":
        return f"""You are analyzing a screenshot of the {name}.
Extract the current UI state into JSON:

{{
  "current_dialog": "name of the currently visible dialog/window",
  "active_menu": "currently active menu or tab, if visible",
  "visible_elements": ["key UI elements visible on screen"],
  "data_state": "state of data loaded (e.g., '{ex}', 'none')",
  "current_action": "what action appears to be in progress"
}}

Respond with JSON only, no markdown fences, no explanation."""
    # v3: on-screen strings are copied VERBATIM (title-bar text, button
    # labels, field labels, list/tree entries) so that workflow-node
    # signatures and the candidate matcher can rely on exact strings.
    return f"""You are analyzing a screenshot of the {name}.
Extract the current UI state into JSON. Copy every on-screen string VERBATIM (same capitalisation, hyphens, brackets, numbers) — do not paraphrase or translate labels. Ignore any GeoLens chat window.

{{
  "current_dialog": "exact title-bar text of the front-most dialog/window (or the main window title)",
  "window_titles": ["exact title-bar text of every visible window/dialog, front-most first"],
  "active_menu": "currently open menu / active tab, if visible",
  "menu_items": ["exact text of visible menu-bar entries and any open context-menu / submenu items"],
  "buttons": ["exact labels of visible buttons (OK, Cancel, Next, Add as new, ...)"],
  "labels": ["exact labels of fields, dropdowns, checkboxes, radio buttons, with the current value in parentheses if readable"],
  "visible_elements": ["other key UI elements visible on screen: panels, trees, list/tree entries, toolbars"],
  "data_state": "state of data loaded (e.g., '{ex}', 'none')",
  "current_action": "what action appears to be in progress"
}}

Respond with JSON only, no markdown fences, no explanation."""


# Kept as module-level for backward-compatibility with any external import.
# Runtime code uses _build_visual_state_prompt(get_active_software_id()).
VISUAL_STATE_PROMPT = _build_visual_state_prompt("opendtect")


def _extract_json(text: str) -> Optional[Dict]:
    """Extract JSON object from model response."""
    if not text:
        return None
    match = re.search(r'\{[\s\S]*\}', text)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None


class GuideRAGPipeline:
    """
    Guide mode pipeline:
      1. Recognize visual state from screenshot (via Gemini)
      2. Match to workflow graph node (localization)
      3. Retrieve next-step context (graph + vector)
      4. Check correction need vs expected position
      5. Build enriched context for guide response
    """

    def __init__(
        self,
        workflow_graph: Optional[WorkflowGraph] = None,
        retriever: Optional[GraphRetriever] = None,
    ):
        self.graph = workflow_graph or get_workflow_graph()
        self.retriever = retriever or get_graph_retriever()

    # ═══════════════════════════════════════════════════════════
    # Step 1: Visual State Recognition
    # ═══════════════════════════════════════════════════════════

    def recognize_visual_state(self, screenshot_b64: str) -> Dict:
        """
        Use Gemini to extract structured UI state from a screenshot.
        screenshot_b64: raw base64 or data URL

        Results are cached in-process by SHA-256 of the raw image bytes so
        the bench harness (which re-analyzes every prior step's screenshot
        on each new step to reconstruct visited_node_ids) pays the Gemini
        vision call once per unique screenshot instead of O(N^2). In
        production this also helps when the same on-screen state persists
        across successive 200 ms captures.
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {}

        from google import genai
        from google.genai import types
        import base64 as b64module
        import hashlib as _hashlib
        import time as _time, random as _random

        try:
            # Extract base64 payload up-front so we can hash the raw image
            # bytes (data-URL prefix must not affect cache identity).
            b64_data = screenshot_b64
            mime = "image/jpeg"
            if screenshot_b64.startswith("data:image/"):
                header, b64_data = screenshot_b64.split(",", 1)
                try:
                    mime = header.split(";")[0].split(":")[1]
                except Exception:
                    mime = "image/jpeg"

            image_bytes = b64module.b64decode(b64_data)
            cache_key = _hashlib.sha256(image_bytes).hexdigest()
            cached = _VISUAL_STATE_CACHE.get(cache_key)
            if cached is not None:
                _VISUAL_STATE_CACHE_STATS["hits"] += 1
                # v3 accounting: a cache hit still counts as this request's
                # vision call. In the bench several backends analyse the same
                # screenshot inside one process; without this the vision cost
                # lands on whichever backend ran first (graph_only) and
                # full_system/state_path look artificially cheap.
                _replay_cached_usage(cache_key)
                return dict(cached)  # defensive copy — callers may mutate
            _VISUAL_STATE_CACHE_STATS["misses"] += 1

            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=30_000),
            )

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=_build_visual_state_prompt(get_active_software_id())),
                        types.Part.from_bytes(data=image_bytes, mime_type=mime),
                    ],
                )
            ]
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0,
                thinking_config=_aux_thinking_config(types),
            )

            MAX_RETRY = 3
            for attempt in range(MAX_RETRY + 1):
                try:
                    _t_vis = _time.perf_counter()
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", contents=contents, config=config
                    )
                    _dt_vis = _time.perf_counter() - _t_vis
                    stage_timer.record("vision", _dt_vis)
                    um = getattr(response, "usage_metadata", None)
                    record_aux_usage("vision", "gemini-2.5-flash", um, latency_sec=_dt_vis)
                    _VISUAL_STATE_USAGE[cache_key] = dict(_usage_snapshot(um), latency_sec=round(_dt_vis, 3))
                    result = _extract_json(response.text) or {}
                    # Only cache non-empty results — an empty dict typically
                    # means Gemini returned something we couldn't parse, and
                    # caching that would poison every future call on the
                    # same screenshot.
                    if result:
                        if len(_VISUAL_STATE_CACHE) >= _CACHE_MAX_ENTRIES:
                            # Simple FIFO eviction — the harness never
                            # revisits an old screenshot after 500+ new
                            # ones, so LRU adds complexity for no gain.
                            _VISUAL_STATE_CACHE.pop(next(iter(_VISUAL_STATE_CACHE)))
                        _VISUAL_STATE_CACHE[cache_key] = dict(result)
                    return result
                except Exception as e:
                    msg = str(e)
                    transient = any(m in msg for m in (
                        "503", "429", "500", "504", "UNAVAILABLE",
                        "RESOURCE_EXHAUSTED", "DEADLINE_EXCEEDED", "timed out", "Timeout"
                    ))
                    if not transient or attempt >= MAX_RETRY:
                        print(f"[GuidePipeline] Visual state recognition failed: {e}")
                        return {}
                    delay = 1.5 * (2 ** attempt) + _random.uniform(0, 0.5)
                    print(f"[GuidePipeline] visual_state transient; retry {attempt + 1}/{MAX_RETRY} after {delay:.1f}s")
                    _time.sleep(delay)
        except Exception as e:
            print(f"[GuidePipeline] Visual state setup failed: {e}")
            return {}
        return {}

    # ═══════════════════════════════════════════════════════════
    # Step 2: Graph Localization
    # ═══════════════════════════════════════════════════════════

    def localize_to_graph(
        self,
        visual_state: Dict,
        hint_workflow_id: Optional[str] = None,
        screenshot_b64: Optional[str] = None,
        manual_ids: Optional[List[str]] = None,
        user_goal: str = "",
        visited_node_ids: Optional[List[str]] = None,
        last_node_id: Optional[str] = None,
        completed_steps: Optional[List[str]] = None,
    ) -> Dict:
        """
        Match visual state to a workflow graph node using:
          1. Top-K candidates: embedding similarity (v3) and/or v2 substring
             score (ROUTER_MATCHER = embedding | substring | hybrid)
          2. Top-K CLIP image candidates (on manual screenshots)
          2b. Graph prior (v3): successors of the last confirmed node are
             always in the pool and flagged to the rerank as expected-next
          3. Gemini rerank over the combined candidate set (v3: also sees the
             session's completed steps)

        The LLM rerank is the highest-accuracy signal because it understands
        user intent (goal), UI semantics (visual_state), and workflow
        descriptions — solving the problem where keyword/CLIP alone match
        generic chrome like "Scene", "OpendTect window".

        Returns {"node": node_dict or None, "confidence": float, "match_method": str}.
        """
        # Legacy single-best for logging + fallback path
        kw_node, kw_score = self.graph.get_current_node(visual_state, hint_workflow_id)

        # CLIP is a weak-to-ambiguous signal for UI screenshots — two different
        # OpendTect panes routinely cosine ≥0.85 because they share UI chrome.
        # Keyword top-k and CLIP top-k are therefore pooled as candidates and
        # the LLM rerank decides; neither score is used as a threshold.

        clip_node = None
        clip_score = 0.0
        if screenshot_b64 and manual_ids:
            try:
                from .visual_matcher import get_visual_matcher
                matcher = get_visual_matcher()
                if matcher.available():
                  with stage_timer.timed("clip"):
                    for mid in manual_ids:
                        node, score = matcher.match_to_workflow_node(
                            screenshot_b64, mid, self.graph
                        )
                        if node and score > clip_score:
                            clip_node = node
                            clip_score = float(score)
            except Exception as e:
                print(f"[GUIDE] CLIP match failed: {e}")

        # Log what Gemini extracted so we can debug mismatches offline
        vs_summary = (visual_state.get("current_dialog") or "")[:40] + " / " + \
                     (visual_state.get("active_menu") or "")[:40]
        print(f"[GUIDE] visual_state: {vs_summary!r}")

        # Build the candidate pool (dedup by node id):
        #   embedding top-K and/or substring top-3 (ROUTER_MATCHER), CLIP top-3,
        #   plus the graph prior (successors of the last confirmed node).
        from . import node_matcher
        kind = node_matcher.matcher_kind()
        kw_top: List[Tuple[Dict, float]] = []
        if kind in ("embedding", "hybrid"):
            kw_top += node_matcher.top_k(visual_state, self.graph.get_all_nodes(), k=ROUTER_POOL_K,
                                         hint_workflow_id=hint_workflow_id)
        if kind in ("substring", "hybrid"):
            kw_top += self.graph.get_top_k_nodes_substring(visual_state, k=3, hint_workflow_id=hint_workflow_id)
        prior_top: List[Tuple[Dict, float]] = []
        expected_next_ids: List[str] = []
        if ROUTER_GRAPH_PRIOR and last_node_id and self.graph.get_node(last_node_id):
            for nxt in self.graph.get_next_steps(last_node_id):
                prior_top.append((nxt, 1.0))
                expected_next_ids.append(nxt.get("id"))
            # the last node itself stays a candidate (dialog may still be open)
            prior_top.append((self.graph.get_node(last_node_id), 1.0))
        clip_top: List[Tuple[Dict, float]] = []
        if screenshot_b64 and manual_ids:
            try:
                from .visual_matcher import get_visual_matcher
                matcher = get_visual_matcher()
                if matcher.available():
                    for mid in manual_ids:
                        clip_top.extend(
                            matcher.match_to_workflow_nodes_top_k(
                                screenshot_b64, mid, self.graph, k=3
                            )
                        )
            except Exception as e:
                print(f"[GUIDE] CLIP top-k failed: {e}")

        seen_ids: set = set()
        candidates: List[Dict] = []
        for node, score in prior_top + kw_top + clip_top:
            nid = node.get("id")
            if not nid or nid in seen_ids:
                continue
            seen_ids.add(nid)
            candidates.append({"node": node, "source_score": score})

        print(f"[GUIDE] candidates: {len(candidates)} (matcher={kind} kw_top={len(kw_top)}, clip_top={len(clip_top)}, prior={len(prior_top)})")

        # Ask Gemini to pick the best candidate (authoritative signal).
        # visited_node_ids tells it which nodes the user has already passed,
        # so if the screenshot still looks like one of them (common when a
        # wizard dialog stays up after Import) it should advance to the
        # successor instead of repeating.
        if candidates:
            picked_id, picked_conf = self._llm_rerank_candidates(
                candidates, visual_state, user_goal,
                visited_node_ids=visited_node_ids,
                expected_next_ids=expected_next_ids,
                completed_steps=completed_steps,
            )
            if picked_id:
                for c in candidates:
                    if c["node"].get("id") == picked_id:
                        node = c["node"]
                        print(f"[GUIDE] localize via LLM rerank: node={picked_id} conf={picked_conf:.2f}")
                        _set_localize_meta(node, picked_conf, "llm")
                        return {"node": node, "confidence": picked_conf, "match_method": "llm"}

            # LLM rerank returned "none" OR failed after retries.
            # Do NOT fall back to keyword top-1 — keyword matching latches
            # onto generic UI terms (Scene, Window, Cross-line) and routinely
            # picks a wrong workflow whose manual context misleads the guide
            # LLM. Returning node=None lets RAG vector search supply chunks
            # by user_message similarity instead — better than wrong context.
            print(f"[GUIDE] LLM rerank gave no answer - node=None (vector RAG will provide context)")
            _set_localize_meta(None, 0.0, "none")
            return {"node": None, "confidence": 0.0, "match_method": "none"}

        # No candidates at all — fall back to single-best keyword
        print(f"[GUIDE] no candidates; fallback node={kw_node.get('id') if kw_node else None} score={kw_score:.3f}")
        _set_localize_meta(kw_node, kw_score, "keyword")
        return {"node": kw_node, "confidence": kw_score, "match_method": "keyword"}

    def _llm_rerank_candidates(
        self,
        candidates: List[Dict],
        visual_state: Dict,
        user_goal: str,
        visited_node_ids: Optional[List[str]] = None,
        expected_next_ids: Optional[List[str]] = None,
        completed_steps: Optional[List[str]] = None,
    ) -> Tuple[Optional[str], float]:
        """Ask Gemini Flash to pick the candidate whose workflow step best
        matches the user's current situation. Returns (node_id, confidence 0-1)
        or (None, 0.0) if no candidate fits or Gemini fails."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None, 0.0
        expected_next_ids = [e for e in (expected_next_ids or []) if e]
        completed_steps = [s for s in (completed_steps or []) if s]

        # Build a compact candidate list for the prompt
        lines = []
        for i, c in enumerate(candidates, start=1):
            n = c["node"]
            wf = (n.get("workflow_id") or "").replace("auto_", "").split("__", 1)[-1]
            title = (n.get("title") or "")[:80]
            desc = (n.get("description") or "")[:120]
            step = n.get("step_number", "?")
            line = f'{i}. id="{n.get("id")}" workflow="{wf}" step={step}\n   title: {title}\n   desc: {desc}'
            if RERANK_PROMPT_VERSION != "v2":
                # v3: the decision rule asks the model to compare on-screen strings with
                # each candidate's expected dialog / elements / keywords, so show them.
                sig = n.get("visual_signature") or {}
                dlg = (sig.get("expected_dialog") or "")[:90]
                els = ", ".join(str(e).replace("_", " ") for e in (sig.get("expected_ui_elements") or [])[:8])[:160]
                kws = ", ".join(str(k) for k in (sig.get("screenshot_keywords") or [])[:10])[:160]
                if dlg:
                    line += f"\n   expected dialog: {dlg}"
                if els:
                    line += f"\n   expected elements: {els}"
                if kws:
                    line += f"\n   keywords: {kws}"
            lines.append(line)
        candidate_block = "\n".join(lines)

        goal_line = f"User goal: {user_goal.strip()}" if user_goal.strip() else "User goal: (unspecified)"
        vs_line = json.dumps(visual_state, ensure_ascii=False)[:500]

        visited_line = ""
        if visited_node_ids:
            # Only mention ones that actually appear in the candidate pool
            candidate_ids = {c["node"].get("id") for c in candidates}
            visited_in_pool = [v for v in visited_node_ids if v in candidate_ids]
            if visited_in_pool and RERANK_PROMPT_VERSION == "v2":
                visited_line = (
                    "\nAlready-completed candidate nodes (the user has finished these — "
                    "DO NOT pick one of these again if the screenshot shows the same state "
                    "after completion; prefer a candidate that represents the NEXT step, "
                    "or return \"none\" to let the user discover the Close/Finish button "
                    "themselves): " + ", ".join(visited_in_pool)
                )
            elif visited_in_pool:
                visited_line = (
                    "\nCandidates matched in previous turns of this session (a step can span several "
                    "actions — pick one of these again if its dialog is still on screen and the "
                    "instructions already given do not cover all of its actions): " + ", ".join(visited_in_pool)
                )

        session_block = ""
        if completed_steps:
            recent = completed_steps[-6:]
            session_block = "\nInstructions already given to the user in this session (oldest first):\n" + \
                "\n".join(f"  {i + 1}. {s[:160]}" for i, s in enumerate(recent))
        expected_block = ""
        if expected_next_ids:
            expected_block = ("\nGraph prior: after the last confirmed step, the workflow expects one of these next: "
                              + ", ".join(expected_next_ids) + ". Prefer them when the screen is consistent with them.")

        if RERANK_PROMPT_VERSION == "v2":
            session_block = ""
            expected_block = ""
            rule_block = _RERANK_RULE_V2
            wizard_block = _RERANK_WIZARD_V2
        else:
            rule_block = _RERANK_RULE_V3.replace("{thr}", f"{CONFIDENCE_THRESHOLD:.2f}")
            wizard_block = _RERANK_WIZARD_V3

        prompt = f"""You rank workflow steps by how well they match the user's current UI situation.

{goal_line}
Current UI visual_state JSON: {vs_line}{visited_line}{session_block}{expected_block}

Candidate workflow steps (from a software manual):
{candidate_block}

Pick the candidate whose step description best matches what the user is CURRENTLY doing or trying to do next — aligned to the goal, the visible UI state, and the instructions already given.

{rule_block}

{wizard_block}

Respond with JSON only:
{{"id": "<candidate_id_or_none>", "confidence": 0.0-1.0}}"""

        from google import genai
        from google.genai import types
        import time as _time, random as _random

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=40_000),
        )
        cfg = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0,
            thinking_config=_aux_thinking_config(types),
        )

        RERANK_MAX_RETRIES = 3
        RERANK_BASE_BACKOFF = 1.5
        raw = ""
        last_err = None
        for attempt in range(RERANK_MAX_RETRIES + 1):
            try:
                _t_rr = _time.perf_counter()
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=cfg,
                )
                _dt_rr = _time.perf_counter() - _t_rr
                stage_timer.record("rerank", _dt_rr)
                record_aux_usage("rerank", "gemini-2.5-flash",
                                 getattr(response, "usage_metadata", None),
                                 latency_sec=_dt_rr)
                raw = (response.text or "").strip()
                if attempt > 0:
                    print(f"[GUIDE] rerank recovered on retry {attempt}")
                break
            except Exception as e:
                last_err = e
                msg = str(e)
                transient = any(m in msg for m in (
                    "503", "429", "500", "504", "UNAVAILABLE",
                    "RESOURCE_EXHAUSTED", "DEADLINE_EXCEEDED", "timed out", "Timeout"
                ))
                if not transient or attempt >= RERANK_MAX_RETRIES:
                    print(f"[GUIDE] LLM rerank failed: {e}")
                    return None, 0.0
                delay = RERANK_BASE_BACKOFF * (2 ** attempt) + _random.uniform(0, 0.5)
                print(f"[GUIDE] rerank transient ({e.__class__.__name__}); retry {attempt + 1}/{RERANK_MAX_RETRIES} after {delay:.1f}s")
                _time.sleep(delay)

        if not raw:
            print(f"[GUIDE] LLM rerank empty response after retries: {last_err}")
            return None, 0.0

        try:
            parsed = json.loads(raw)
        except Exception as e:
            print(f"[GUIDE] LLM rerank JSON parse failed: {e}")
            return None, 0.0
        pid = str(parsed.get("id", "") or "").strip()
        conf = float(parsed.get("confidence", 0.0) or 0.0)
        if not pid or pid.lower() == "none":
            return None, 0.0
        return pid, max(0.0, min(1.0, conf))

    # ═══════════════════════════════════════════════════════════
    # Step 3-5: Main processing
    # ═══════════════════════════════════════════════════════════

    def process_guide_request(
        self,
        screenshot_b64: Optional[str],
        user_message: str,
        session_history: Optional[Dict] = None,
        manual_ids: Optional[List[str]] = None,
    ) -> Dict:
        """
        Main entry point. Returns a structured context dict for the LLM:
        {
          "visual_state": {...},
          "current_node": {...} or None,
          "confidence": 0.0-1.0,
          "next_nodes": [...],
          "graph_context": [...],
          "vector_context": "...",
          "correction": {...} or None,
          "intent": "next_step" | "explain" | "qa",
        }
        """
        session_history = session_history or {}
        last_node_id = session_history.get("last_confirmed_node_id")
        completed_steps = session_history.get("completed_steps") or []

        # v3: the goal-query vector retrieval is the same retrieval the
        # vanilla baseline performs and does not depend on the screenshot,
        # so it runs in a worker thread while vision + localization run.
        # It is the fallback context (routing rejected / below threshold)
        # and the auxiliary vector block of the routed context.
        vec_future = None
        executor = None
        if manual_ids and user_message and PARALLEL_RETRIEVAL:
            executor = ThreadPoolExecutor(max_workers=1)
            vec_future = executor.submit(_timed_call, "goal_retrieval", self.retriever.retrieve_by_vector, user_message, manual_ids)

        # Step 1: Recognize visual state
        visual_state: Dict = {}
        if screenshot_b64:
            visual_state = self.recognize_visual_state(screenshot_b64)

        # Step 2: Detect intent
        intent = self._detect_intent(user_message)

        # Step 3: Localize (keyword + CLIP top-K → Gemini rerank)
        hint = session_history.get("active_workflow_id")
        visited = session_history.get("visited_node_ids") or []
        with stage_timer.timed("localize"):
            localization = self.localize_to_graph(
                visual_state,
                hint,
                screenshot_b64=screenshot_b64,
                manual_ids=manual_ids,
                user_goal=user_message,
                visited_node_ids=visited,
                last_node_id=last_node_id,
                completed_steps=completed_steps,
            )
        current_node = localization["node"]
        confidence = localization["confidence"]
        match_method = localization.get("match_method", "")
        current_node_id = current_node["id"] if current_node else None

        # Confidence gate — if rerank picked a node but only weakly, treat as
        # "no reliable match" and fall back to pure vector retrieval. Low-
        # confidence graph picks poison the context with the wrong workflow's
        # chunks and misdirect the guide LLM. Better to ground on user-message
        # vector similarity alone than on a mis-routed node.
        fallback_activated = False
        if current_node_id and confidence < CONFIDENCE_THRESHOLD:
            print(
                f"[GUIDE] confidence fallback — node={current_node_id} "
                f"conf={confidence:.2f} < threshold={CONFIDENCE_THRESHOLD:.2f}; "
                f"suppressing graph_context, using vector-only"
            )
            fallback_activated = True
            current_node = None
            current_node_id = None
        elif current_node_id is None and match_method == "none":
            # v3: the rerank rejected every candidate. Retrieval is identical
            # to the confidence fallback (vector-only), so label it as such.
            # In v2 this path left fallback_activated=False (the "NONE
            # bucket": 64/160 attribute steps in unified4 logged as
            # "no routing" although they received fallback semantics).
            fallback_activated = True

        # Record for the benchmark harness (module-level, read via
        # get_last_localize_meta() after the pipeline call returns).
        picked = localization.get("node") or {}
        _LAST_LOCALIZE_META.update({
            "confidence": confidence,
            "picked_node_id": picked.get("id"),
            "picked_workflow_id": picked.get("workflow_id"),
            "match_method": match_method,
            "fallback_activated": fallback_activated,
            "threshold": CONFIDENCE_THRESHOLD,
        })

        # Step 4: Retrieve context
        goal_vector_ctx: Optional[str] = None
        try:
            if vec_future is not None:
                goal_vector_ctx = vec_future.result()
            elif manual_ids and user_message:
                goal_vector_ctx = _timed_call("goal_retrieval", self.retriever.retrieve_by_vector, user_message, manual_ids)
        except Exception as e:
            print(f"[GUIDE] goal vector retrieval failed: {e}")
        finally:
            if executor is not None:
                executor.shutdown(wait=False)
        with stage_timer.timed("routed_retrieval"):
            retrieval = self.retriever.hybrid_retrieve(
                current_node_id=current_node_id,
                query=user_message,
                intent=intent,
                manual_ids=manual_ids,
                precomputed_vector_context=goal_vector_ctx,
            )

        # Step 5: Correction check
        correction = None
        expected_node_id = session_history.get("expected_next_node_id")
        if current_node_id and expected_node_id:
            correction = self.graph.analyze_position(current_node_id, expected_node_id)

        # Step 6: Post-completion detection — fires when the matched node was
        # visited in the RECENT window (last 3 entries). This catches:
        #   step1: Click Next on Import SEG-Y Data (node A)
        #   step2: Click Import on Import Volume   (node B)
        #   step3: Import SEG-Y Data dialog returns → matches A again  ← fire
        # while NOT firing for legitimate backtracks 5+ steps later.
        RECENT_WINDOW = 3
        recent_visited = visited[-RECENT_WINDOW:] if visited else []
        post_completion = bool(current_node_id and current_node_id in recent_visited)
        if post_completion:
            pos = len(visited) - 1 - recent_visited[::-1].index(current_node_id)
            print(f"[GUIDE] post-completion detected — node {current_node_id} visited at history[{pos}] (within last {RECENT_WINDOW})")

        return {
            "visual_state": visual_state,
            "current_node": current_node,
            "confidence": confidence,
            "next_nodes": retrieval.get("next_nodes", []),
            "graph_context": retrieval.get("graph_context", []),
            "vector_context": retrieval.get("vector_context"),
            "correction": correction,
            "intent": intent,
            "post_completion": post_completion,
            "fallback_activated": fallback_activated,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
        }

    # ═══════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _detect_intent(user_message: str) -> str:
        """Classify user message into intent."""
        if not user_message:
            return "next_step"
        msg = user_message.lower()
        explain_keywords = ["explain", "what is", "meaning", "설명", "뜻", "의미"]
        qa_keywords = ["why", "how does", "difference", "왜", "차이"]
        next_keywords = ["next", "then", "after", "다음", "이제", "어떻게"]

        if any(kw in msg for kw in explain_keywords):
            return "explain"
        if any(kw in msg for kw in qa_keywords):
            return "qa"
        if any(kw in msg for kw in next_keywords):
            return "next_step"
        return "next_step"

    @staticmethod
    def build_context_block(pipeline_output: Dict) -> str:
        """
        Build a text context block to inject into the LLM system prompt.
        """
        parts = []

        # Post-completion — v2 ("override"): a dismiss-the-dialog override placed at
        # the TOP. v3 default ("soft"): a step can span several actions (e.g. a
        # configure node covering three scenario steps), so re-matching the same
        # node is not evidence that it is finished; the generator is told to
        # continue with the next action not yet given (it sees the completed
        # instructions in its prompt). "off" renders nothing.
        if pipeline_output.get("post_completion") and POST_COMPLETION_MODE == "soft":
            parts.append(
                "[Same Step As Previous Turn]\n"
                "The matched workflow step is the same one matched in a previous turn. A step can span "
                "several actions. Using the list of instructions already given, continue with the NEXT "
                "action of this step that has not been given yet; do not repeat an instruction already "
                "given. If every action of this step is done, tell the user to confirm or close the "
                "dialog with the button actually visible on screen and move on to the next step."
            )
        if pipeline_output.get("post_completion") and POST_COMPLETION_MODE == "override":
            parts.append(
                "[██ POST-COMPLETION STATE — OVERRIDE ALL OTHER GUIDANCE ██]\n"
                "The user has already completed the action for the matched workflow step. "
                "The dialog is still on screen only because the wizard has not been dismissed yet — "
                "this is NOT a cue to repeat the previous action (e.g. clicking Next again).\n"
                "INSTRUCTION: Tell the user to DISMISS the current dialog by clicking the visible "
                "\"Close\", \"Finish\", \"Done\", \"OK\", \"Cancel\", or \"X\" button — whichever is "
                "actually shown in the screenshot. Do NOT repeat any previously completed instruction."
            )

        current = pipeline_output.get("current_node")
        if current:
            parts.append(
                f"[Current Step] {current.get('workflow_id', '')} > "
                f"Step {current.get('step_number', '?')}: {current.get('title', '')}\n"
                f"Description: {current.get('description', '')}"
            )

        next_nodes = pipeline_output.get("next_nodes") or []
        if next_nodes:
            next_lines = []
            for n in next_nodes:
                cond = f" [if: {n.get('edge_condition')}]" if n.get("edge_condition") else ""
                next_lines.append(
                    f"  - Next ({n.get('edge_type', 'sequential')}){cond}: "
                    f"Step {n.get('step_number', '?')} {n.get('title', '')} — "
                    f"{n.get('edge_instruction') or n.get('description', '')}"
                )
            parts.append("[Possible Next Steps]\n" + "\n".join(next_lines))

        correction = pipeline_output.get("correction")
        if correction and correction.get("case") not in (None, "on_target", "unknown", "no_target"):
            parts.append(f"[Correction Needed] case={correction.get('case')}\n{json.dumps(correction, ensure_ascii=False, indent=2)[:500]}")

        # v3 budgets (env knobs, see module top). Routed: GRAPH_CTX_ITEMS ×
        # GRAPH_CTX_CHARS of linked-chunk text first, then VECTOR_CTX_CHARS
        # of the goal-query retrieval. Not routed (fallback): the goal-query
        # retrieval alone under FALLBACK_CTX_CHARS — the same text and the
        # same budget as the vanilla_budget baseline, so a fallback step
        # can never be worse-informed than vanilla.
        graph_ctx = (pipeline_output.get("graph_context") or []) if current else []
        for g in graph_ctx[:GRAPH_CTX_ITEMS]:
            if g.get("text"):
                parts.append(f"[Manual Context (graph)]\n{g['text'][:GRAPH_CTX_CHARS]}")

        vector_ctx = pipeline_output.get("vector_context")
        if vector_ctx:
            budget = VECTOR_CTX_CHARS if current else FALLBACK_CTX_CHARS
            parts.append(f"[Manual Context (vector)]\n{vector_ctx[:budget]}")

        if not parts:
            return ""
        return "\n\n".join(parts)


# Singleton
_guide_pipeline_instance: Optional[GuideRAGPipeline] = None


def get_guide_pipeline() -> GuideRAGPipeline:
    global _guide_pipeline_instance
    if _guide_pipeline_instance is None:
        _guide_pipeline_instance = GuideRAGPipeline()
    return _guide_pipeline_instance
