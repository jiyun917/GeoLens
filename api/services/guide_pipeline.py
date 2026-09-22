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
    # v3 telemetry fix (2026-09-18): clear the extra telemetry keys too (candidates,
    # emb_top, goal_state_node, evidence, rerank_prompt, ...) — they were persisting
    # from the last routing call into the per_step records of non-routing backends.
    _LAST_LOCALIZE_META.clear()
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
# v3 last development change (2026-09-18): context assembly v4 — the routed node is
# rendered as the STATE reached (signature states only, no description with manual
# example values) and the guidance comes from the outgoing edge ("[Next Action]").
# v3 = the previous [Current Step] (title + description) / [Possible Next Steps] block.
CONTEXT_ASSEMBLY = os.environ.get("CONTEXT_ASSEMBLY", "v4").strip().lower()
# v6 (study 2): v4 + an ordered-actions rule on [Next Action] (first not-yet-visible action only;
# completion sentinel when everything is visibly done). See methodology_audit_trail.md V3-28.
_CTX_V6_RULE = ("Rule: if the action above lists several actions, they are in ORDER - instruct ONLY the first one "
                "whose result is not yet visible on the screen (never skip ahead to a later one). If every listed action "
                "is already visibly done, or the screen already shows the workflow goal achieved, answer with the "
                "completion sentinel '완료' / 'Done' instead.")
# study 2: 0 = do not show the session's earlier generator answers to the rerank (removes the
# generator -> routing coupling found in V3-22); 1 = v3 behaviour.
RERANK_SESSION_BLOCK = os.environ.get("RERANK_SESSION_BLOCK", "1").strip() == "1"
# study 2 (V3-30): session stickiness on identical dialog titles across workflows (R1) and the
# history-aware [Next Action] of assembly v7 (C1). Defaults keep the v3 behaviour.
ROUTER_SESSION_STICKY = os.environ.get("ROUTER_SESSION_STICKY", "0").strip() == "1"
# study 3 (R2): advance to the single successor when the rerank repeats the last confirmed node
# although the previous instruction already covered that node's outgoing edge (V3-37).
ROUTER_HISTORY_ADVANCE = os.environ.get("ROUTER_HISTORY_ADVANCE", "0").strip() == "1"
_CTX_V7_DONE = ("[Next Action] The previous instruction ({prev}) was the final action of this workflow. "
                "If the screen shows nothing that contradicts it having been carried out, the goal is reached - answer with the "
                "completion sentinel '완료' / 'Done'. Otherwise repeat only the part that is visibly not done.")
_CTX_V7_ADVANCE = ("[Next Action] (the previous instruction - {prev} - already covered the step above; if the screen shows "
                   "nothing contradicting it, continue with the next action from the workflow)")


def _edge_covered(last_instruction: str, edge_instruction: str) -> bool:
    """True if the previous instruction already told the user to do this edge's action. Latin UI
    tokens / numbers of the edge must be mostly present in the previous instruction; for edges with
    fewer than two such tokens a character-bigram Jaccard on the normalised text is used."""
    if not last_instruction or not edge_instruction:
        return False
    stop = {"the", "and", "then", "click", "select", "with"}
    tok = lambda t: {x for x in re.findall(r"[A-Za-z][A-Za-z\-]{2,}|\d+", (t or "").lower()) if x not in stop}
    e, l = tok(edge_instruction), tok(last_instruction)
    if len(e) >= 2:
        return len(e & l) / len(e) >= 0.6
    a, b = _norm_text(edge_instruction), _norm_text(last_instruction)
    ga = {a[i:i + 2] for i in range(len(a) - 1)}; gb = {b[i:i + 2] for i in range(len(b) - 1)}
    return bool(ga) and len(ga & gb) / len(ga | gb) >= 0.35
_CTX_NOTE = ("Note: 매뉴얼의 예시 값(파일명·파라미터)은 사용자의 데이터와 다를 수 있다. 화면에 이미 설정된 값을 고치도록 안내하지 않는다. "
             "(Manual example values may differ from the user's data; do not instruct the user to change a value that is already set on screen.)")
# v3 iteration 2 — two-stage routing: (i) workflow from the user goal (goal ↔
# name+description+node titles similarity, top ROUTER_WF_TOPN kept, plus the
# session's confirmed workflow), (ii) node within those workflows. A pick from
# a workflow other than the session's needs confidence ≥ threshold + margin.
ROUTER_TWO_STAGE = os.environ.get("ROUTER_TWO_STAGE", "0") != "0"   # iteration 2: ON HOLD (user decision); code kept for the s0/s1 reconstruction
ROUTER_WF_TOPN = int(os.environ.get("ROUTER_WF_TOPN", "2"))
ROUTER_SWITCH_MARGIN = float(os.environ.get("ROUTER_SWITCH_MARGIN", "0.15"))
# v3 iteration 2 — evidence-based verification of the rerank pick (replaces the
# confidence gate): confirmed only if (i) the node's expected_dialog is contained
# in the vision window titles / dialog name (normalised), or (ii) the pick is the
# last confirmed node or one of its successors, or (iii) the pick is the
# embedding top-1 with a top-1 − top-2 gap ≥ ROUTER_EMB_GAP. Rerank confidence is
# recorded but not used as a gate (ROUTER_CONF_FLOOR > 0 adds a floor).
ROUTER_EVIDENCE_GATE = os.environ.get("ROUTER_EVIDENCE_GATE", "0") != "0"   # iteration 2: enabled only if the offline table meets the user criterion
ROUTER_EMB_GAP = float(os.environ.get("ROUTER_EMB_GAP", "0.03"))
ROUTER_CONF_FLOOR = float(os.environ.get("ROUTER_CONF_FLOOR", "0.0"))
# v3 iteration 2 — goal-state block: when the workflow's final action node (or
# a node whose successors are all verification nodes) is the last confirmed /
# currently picked node AND the screen matches that node best among the
# workflow's nodes, the context tells the generator to answer with the
# completion sentinel if the goal is visibly achieved. Uses workflow
# structure, session state and the vision output only.
GOAL_STATE_HINT = os.environ.get("GOAL_STATE_HINT", "1") != "0"
# iteration 3: condition B of the goal-state check accepts a terminal node whose
# score is within GOAL_STATE_MARGIN of the workflow's top-scoring node (0 = must be top-1).
GOAL_STATE_MARGIN = float(os.environ.get("GOAL_STATE_MARGIN", "0.02"))
# iteration 3 (c): near-tie graph-order prior among candidates sharing an expected_dialog.
ROUTER_TIE_MARGIN = float(os.environ.get("ROUTER_TIE_MARGIN", "0.02"))
ROUTER_TIE_PRIOR = os.environ.get("ROUTER_TIE_PRIOR", "1") != "0"
# iteration 4 (final routing change): the graph-order prior applies to every group of
# candidates that share an expected_dialog, regardless of score gap, and the rerank gets a
# contrastive list of the members' distinguishing field states (ROUTER_GROUP_PRIOR=0 → the
# iteration-3 near-tie rule).
ROUTER_GROUP_PRIOR = os.environ.get("ROUTER_GROUP_PRIOR", "1") != "0"
# iteration 3 (d, optional): parallel rerank calls with majority vote (1 = single call).
RERANK_VOTES = max(1, int(os.environ.get("RERANK_VOTES", "1")))
_TERMINAL_STEP_TYPES = {"verification", "terminal", "end"}


def _norm_text(s: Any) -> str:
    return re.sub(r"[^0-9a-z가-힣]+", "", str(s or "").lower())
# v3 rerank prompt (calibrated confidence bands, session context); v2 = the
# unified4 prompt with the 'bias toward picking' decision rule.
RERANK_PROMPT_VERSION = os.environ.get("RERANK_PROMPT_VERSION", "v4").strip().lower()

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

_RERANK_RULE_V4 = """DECISION RULE (state match):
- Each candidate describes a SCREEN STATE — the state of the UI when that step is the user's current position (its expected dialog, expected elements and keywords describe what the screen shows at that point). Pick the candidate whose described state matches the CURRENT screen. Do NOT pick the step whose action the user is about to perform: the next action is supplied later from the workflow edges.
- Candidates that share the same dialog are told apart by FIELD VALUES in visual_state (field_values / labels): the selected dropdown entry, whether a text field is filled or empty, whether a checkbox is checked, whether a list is empty. A label merely being visible on screen (e.g. an unchecked checkbox or an empty field with its caption) is NOT evidence for a candidate that requires it to be set.
- Prefer a candidate from the same workflow as the session's previous steps and the graph prior, unless the screen clearly shows a different application module.
- Return "none" when NO candidate is even loosely related (different application, different module, totally unrelated topic).

CONFIDENCE (recorded, not used as a gate; below {thr} is treated as unsure):
- 0.9–1.0: the candidate's dialog AND its field states are literally on screen.
- 0.7–0.85: same dialog/workflow, field states consistent but not all visible.
- 0.5–0.65: plausible topic only. Use this when unsure; do NOT inflate."""

_RERANK_WIZARD_V4 = """NOTE — steps that span several actions and dialogs that stay open:
- A step may cover several actions; the screen still matches that step until its completion state (as described by its successor) is visible.
- Pick the SUCCESSOR only if the screen shows the successor's described state (its field values are now set). If the instructions already given completed a step but the screen has not changed, stay on that step."""

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
  "field_values": ["one entry per field/dropdown/checkbox/radio/list as 'Label: value' with the value copied verbatim — dropdown: the selected entry; text field: its content or (empty); checkbox/radio: checked/unchecked; list/table: '(empty)' or its entries"],
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
        clip_result: Optional[Tuple] = None,
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

        # v3 iteration 2: CLIP (local CPU) runs in a worker thread parallel to the
        # vision call when process_guide_request supplies clip_result.
        if clip_result is not None:
            clip_node, clip_score, clip_top = clip_result
        else:
            clip_node, clip_score, clip_top = self._clip_match(screenshot_b64, manual_ids)

        # Log what Gemini extracted so we can debug mismatches offline
        vs_summary = (visual_state.get("current_dialog") or "")[:40] + " / " + \
                     (visual_state.get("active_menu") or "")[:40]
        print(f"[GUIDE] visual_state: {vs_summary!r}")

        # Build the candidate pool (dedup by node id):
        #   embedding top-K and/or substring top-3 (ROUTER_MATCHER), CLIP top-3,
        #   plus the graph prior (successors of the last confirmed node).
        from . import node_matcher
        kind = node_matcher.matcher_kind()
        all_nodes = self.graph.get_all_nodes()
        # stage (i): workflow selection from the user goal (+ the session's workflow)
        session_wf = None
        if last_node_id and self.graph.get_node(last_node_id):
            session_wf = self.graph.get_node(last_node_id).get("workflow_id")
        wf_scores: List[Tuple[str, float]] = []
        selected_wfs: List[str] = []
        if ROUTER_TWO_STAGE and user_goal and not hint_workflow_id:
            try:
                wf_scores = node_matcher.workflow_scores(user_goal, self.graph.list_workflows(), all_nodes)
            except Exception as e:
                print(f"[GUIDE] workflow scoring failed: {e}")
            selected_wfs = [w for w, _ in wf_scores[:ROUTER_WF_TOPN]]
            if session_wf and session_wf not in selected_wfs:
                selected_wfs.append(session_wf)
        pool_nodes = [n for n in all_nodes if n.get("workflow_id") in selected_wfs] if selected_wfs else all_nodes
        escape_node: Optional[Dict] = None
        kw_top: List[Tuple[Dict, float]] = []
        emb_top: List[Tuple[str, float]] = []
        if kind in ("embedding", "hybrid"):
            kw_top += node_matcher.top_k(visual_state, pool_nodes, k=ROUTER_POOL_K,
                                         hint_workflow_id=hint_workflow_id)
            emb_top = [(n.get("id"), float(s)) for n, s in kw_top]
            if selected_wfs:
                # escape hatch: the global best node from an unselected workflow stays
                # visible to the rerank (flagged; the switch gate applies to it)
                g1 = node_matcher.top_k(visual_state, all_nodes, k=1, hint_workflow_id=hint_workflow_id)
                if g1 and g1[0][0].get("workflow_id") not in selected_wfs:
                    escape_node = g1[0][0]
                    kw_top.append(g1[0])
        if kind in ("substring", "hybrid"):
            kw_top += self.graph.get_top_k_nodes_substring(visual_state, k=3, hint_workflow_id=hint_workflow_id)
        _LAST_LOCALIZE_META["emb_top"] = emb_top
        if selected_wfs:
            print(f"[GUIDE] two-stage: workflows={[(w, round(s, 3)) for w, s in wf_scores[:3]]} selected={selected_wfs} session={session_wf}")
        prior_top: List[Tuple[Dict, float]] = []
        expected_next_ids: List[str] = []
        if ROUTER_GRAPH_PRIOR and last_node_id and self.graph.get_node(last_node_id):
            for nxt in self.graph.get_next_steps(last_node_id):
                prior_top.append((nxt, 1.0))
                expected_next_ids.append(nxt.get("id"))
            # the last node itself stays a candidate (dialog may still be open)
            prior_top.append((self.graph.get_node(last_node_id), 1.0))
        seen_ids: set = set()
        candidates: List[Dict] = []
        cand_sources: Dict[str, List[str]] = {}
        for src_name, lst in (("prior", prior_top), ("emb", kw_top), ("clip", clip_top)):
            for node, score in lst:
                nid = node.get("id")
                if not nid:
                    continue
                if selected_wfs and src_name == "clip" and node.get("workflow_id") not in selected_wfs:
                    continue   # two-stage: CLIP candidates outside the selected workflows are dropped
                cand_sources.setdefault(nid, []).append(f"{src_name}:{score:.2f}")
                if nid in seen_ids:
                    continue
                seen_ids.add(nid)
                candidates.append({"node": node, "source_score": score,
                                   "other_workflow": bool(selected_wfs and node.get("workflow_id") not in selected_wfs)})
        _LAST_LOCALIZE_META["candidates"] = [{"id": c["node"].get("id"), "sources": cand_sources.get(c["node"].get("id"), [])}
                                             for c in candidates]
        tie_pref: Optional[str] = None
        self._last_group = []
        if ROUTER_TIE_PRIOR and emb_top:
            tie_pref = self._tie_prior(emb_top, last_node_id)
            if tie_pref:
                # list the preferred node first among the candidates
                candidates.sort(key=lambda c: 0 if c["node"].get("id") == tie_pref else 1)
        tie_group = list(getattr(self, "_last_group", []) or []) if tie_pref else []
        _LAST_LOCALIZE_META["tie_group"] = tie_group
        _LAST_LOCALIZE_META["tie_prior"] = tie_pref
        _LAST_LOCALIZE_META["wf_scores"] = [(w, round(s, 3)) for w, s in wf_scores[:4]]
        _LAST_LOCALIZE_META["selected_wfs"] = list(selected_wfs)
        _LAST_LOCALIZE_META["session_wf"] = session_wf

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
                session_wf=session_wf,
                selected_wfs=selected_wfs,
                tie_pref=tie_pref,
                tie_group=tie_group,
                last_node_id=last_node_id,
            )
            if picked_id and ROUTER_SESSION_STICKY:
                picked_id = self._session_sticky(picked_id, candidates, session_wf, last_node_id)
            if picked_id and ROUTER_HISTORY_ADVANCE:
                picked_id = self._history_advance(picked_id, candidates, last_node_id, completed_steps)
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
        session_wf: Optional[str] = None,
        selected_wfs: Optional[List[str]] = None,
        tie_pref: Optional[str] = None,
        tie_group: Optional[List[str]] = None,
        last_node_id: Optional[str] = None,
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
            if c.get("other_workflow"):
                line += "\n   (candidate from a workflow NOT selected by the user goal — pick only with literal on-screen evidence)"
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
        vs_line = json.dumps(visual_state, ensure_ascii=False)[:1400 if RERANK_PROMPT_VERSION != "v2" else 500]

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
        if completed_steps and RERANK_SESSION_BLOCK:
            recent = completed_steps[-6:]
            session_block = "\nInstructions already given to the user in this session (oldest first):\n" + \
                "\n".join(f"  {i + 1}. {s[:160]}" for i, s in enumerate(recent))
        tie_block = ""
        if RERANK_PROMPT_VERSION != "v2" and tie_pref:
            if ROUTER_GROUP_PRIOR and tie_group:
                tie_block = self._group_contrast_block(tie_group, tie_pref, last_node_id)
            else:
                tie_block = (f"\nGraph-order prior: several candidates share the same dialog and score almost equally; "
                             f"by workflow order the expected one is {tie_pref}. Pick a different one of them only if a field "
                             f"value in visual_state (field_values / labels) contradicts it.")
        wf_block = ""
        if RERANK_PROMPT_VERSION != "v2" and ROUTER_TWO_STAGE and (selected_wfs or session_wf):
            wf_block = (f"\nWorkflow(s) selected from the user goal: {', '.join(selected_wfs or [])}."
                        + (f" Workflow confirmed earlier in this session: {session_wf}. Prefer its steps; switching to another "
                           f"workflow needs literal on-screen evidence and confidence ≥ {min(1.0, CONFIDENCE_THRESHOLD + ROUTER_SWITCH_MARGIN):.2f}."
                           if session_wf else ""))
        expected_block = ""
        if expected_next_ids:
            expected_block = ("\nGraph prior: after the last confirmed step, the workflow expects one of these next: "
                              + ", ".join(expected_next_ids) + ". Prefer them when the screen is consistent with them.")

        if RERANK_PROMPT_VERSION == "v2":
            session_block = ""
            expected_block = ""
            rule_block = _RERANK_RULE_V2
            wizard_block = _RERANK_WIZARD_V2
        elif RERANK_PROMPT_VERSION == "v3":
            rule_block = _RERANK_RULE_V3.replace("{thr}", f"{CONFIDENCE_THRESHOLD:.2f}")
            wizard_block = _RERANK_WIZARD_V3
        else:
            rule_block = _RERANK_RULE_V4.replace("{thr}", f"{CONFIDENCE_THRESHOLD:.2f}")
            wizard_block = _RERANK_WIZARD_V4

        task_line = ("Pick the candidate whose described screen state matches the CURRENT screen — the step the user has reached (not the action they will do next) — consistent with the goal and the instructions already given."
                     if RERANK_PROMPT_VERSION not in ("v2", "v3") else
                     "Pick the candidate whose step description best matches what the user is CURRENTLY doing or trying to do next — aligned to the goal, the visible UI state, and the instructions already given.")
        prompt = f"""You rank workflow steps by how well they match the user's current UI situation.

{goal_line}
Current UI visual_state JSON: {vs_line}{visited_line}{session_block}{expected_block}{wf_block}{tie_block}

Candidate workflow steps (from a software manual):
{candidate_block}

{task_line}

{rule_block}

{wizard_block}

Respond with JSON only:
{{"id": "<candidate_id_or_none>", "confidence": 0.0-1.0}}"""

        from google import genai
        from google.genai import types
        import time as _time, random as _random

        _LAST_LOCALIZE_META["rerank_prompt"] = prompt
        if RERANK_VOTES > 1:
            return self._rerank_vote(prompt, candidates)
        return self._rerank_once(prompt)

    def _rerank_vote(self, prompt: str, candidates: List[Dict]) -> Tuple[Optional[str], float]:
        """RERANK_VOTES parallel rerank calls; majority id wins (ties → the answer with the
        highest confidence); confidence = mean confidence of the winning votes."""
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=RERANK_VOTES) as ex:
            answers = list(ex.map(lambda _: self._rerank_once(prompt), range(RERANK_VOTES)))
        tally: Dict[str, List[float]] = {}
        for pid, conf in answers:
            tally.setdefault(pid or "none", []).append(conf)
        best = max(tally.items(), key=lambda kv: (len(kv[1]), max(kv[1])))
        _LAST_LOCALIZE_META["rerank_votes"] = [(pid or "none", round(c, 2)) for pid, c in answers]
        print(f"[GUIDE] rerank vote: {_LAST_LOCALIZE_META['rerank_votes']} -> {best[0]}")
        if best[0] == "none":
            return None, 0.0
        return best[0], sum(best[1]) / len(best[1])

    def _rerank_once(self, prompt: str) -> Tuple[Optional[str], float]:
        from google import genai
        from google.genai import types
        import time as _time, random as _random
        api_key = os.environ.get("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=40_000))
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
        _LAST_LOCALIZE_META["rerank_raw"] = raw[:300]
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
        clip_future = None
        executor = None
        if manual_ids and PARALLEL_RETRIEVAL:
            executor = ThreadPoolExecutor(max_workers=2)
            if user_message:
                vec_future = executor.submit(_timed_call, "goal_retrieval", self.retriever.retrieve_by_vector, user_message, manual_ids)
            if screenshot_b64:
                # v3 iteration 2: CLIP candidate matching is local CPU work that only
                # needs the screenshot, so it overlaps the network-bound vision call.
                clip_future = executor.submit(self._clip_match, screenshot_b64, manual_ids)

        # Step 1: Recognize visual state
        visual_state: Dict = {}
        if screenshot_b64:
            visual_state = self.recognize_visual_state(screenshot_b64)

        # Step 2: Detect intent
        intent = self._detect_intent(user_message)

        # Step 3: Localize (keyword + CLIP top-K → Gemini rerank)
        hint = session_history.get("active_workflow_id")
        visited = session_history.get("visited_node_ids") or []
        clip_result = None
        if clip_future is not None:
            try:
                clip_result = clip_future.result()
            except Exception as e:
                print(f"[GUIDE] parallel CLIP failed: {e}")
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
                clip_result=clip_result,
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
        gate_reason = ""
        session_wf = _LAST_LOCALIZE_META.get("session_wf")
        if (current_node_id and session_wf and ROUTER_TWO_STAGE
                and current_node.get("workflow_id") != session_wf
                and confidence < min(1.0, CONFIDENCE_THRESHOLD + ROUTER_SWITCH_MARGIN)):
            print(f"[GUIDE] switch gate — node={current_node_id} wf={current_node.get('workflow_id')} != session {session_wf}; "
                  f"conf={confidence:.2f} < {CONFIDENCE_THRESHOLD + ROUTER_SWITCH_MARGIN:.2f}; fallback")
            gate_reason = "switch_gate"
            fallback_activated = True
            current_node = None
            current_node_id = None
        if current_node_id and ROUTER_EVIDENCE_GATE:
            evidence = self._evidence_check(current_node, visual_state, last_node_id)
            _LAST_LOCALIZE_META["evidence"] = evidence
            if not evidence["ok"] or confidence < ROUTER_CONF_FLOOR:
                print(f"[GUIDE] evidence gate — node={current_node_id} conf={confidence:.2f} evidence={evidence}; fallback")
                gate_reason = "evidence_gate"
                fallback_activated = True
                current_node = None
                current_node_id = None
        if current_node_id and confidence < CONFIDENCE_THRESHOLD and not ROUTER_EVIDENCE_GATE:
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
            "gate_reason": gate_reason or ("confidence_gate" if (fallback_activated and picked.get("id")) else ("rerank_none" if fallback_activated else "")),
        })

        # Step 3b (v3 iteration 2): goal-state hint — workflow structure + session
        # state + vision only (no scenario ground truth is read here).
        goal_state = self._goal_state_check(visual_state, picked.get("id"), last_node_id) if GOAL_STATE_HINT else None
        _LAST_LOCALIZE_META["goal_state_node"] = goal_state.get("id") if goal_state else None

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
            "next_nodes_2": (self.graph.get_next_steps(retrieval["next_nodes"][0]["id"]) if retrieval.get("next_nodes") else []),
            "completed_steps": list(completed_steps or []),
            "graph_context": retrieval.get("graph_context", []),
            "vector_context": retrieval.get("vector_context"),
            "correction": correction,
            "intent": intent,
            "post_completion": post_completion,
            "fallback_activated": fallback_activated,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "goal_state": goal_state,
        }

    def _clip_match(self, screenshot_b64: Optional[str], manual_ids: Optional[List[str]]):
        """CLIP single-best + top-3 candidates for the screenshot (timed as 'clip')."""
        clip_node = None
        clip_score = 0.0
        clip_top: List[Tuple[Dict, float]] = []
        if not (screenshot_b64 and manual_ids):
            return clip_node, clip_score, clip_top
        with stage_timer.timed("clip"):
            try:
                from .visual_matcher import get_visual_matcher
                matcher = get_visual_matcher()
                if matcher.available():
                    for mid in manual_ids:
                        node, score = matcher.match_to_workflow_node(screenshot_b64, mid, self.graph)
                        if node and score > clip_score:
                            clip_node = node
                            clip_score = float(score)
                        clip_top.extend(matcher.match_to_workflow_nodes_top_k(screenshot_b64, mid, self.graph, k=3))
            except Exception as e:
                print(f"[GUIDE] CLIP match failed: {e}")
        return clip_node, clip_score, clip_top

    def _group_contrast_block(self, group: List[str], pref: str, last_node_id: Optional[str]) -> str:
        """Iteration 4: contrastive description of candidates that share a dialog —
        each member's keywords/elements that no other member of the group carries —
        plus the graph-order expectation. Generic: built from the signatures only."""
        members = [self.graph.get_node(nid) for nid in group if self.graph.get_node(nid)]
        if len(members) < 2:
            return ""
        def kws(n):
            sig = n.get("visual_signature") or {}
            out = [str(k) for k in (sig.get("screenshot_keywords") or [])]
            out += [str(e).replace("_", " ") for e in (sig.get("expected_ui_elements") or [])]
            return out
        norm_sets = {n["id"]: {_norm_text(k) for k in kws(n)} for n in members}
        dialog = ((members[0].get("visual_signature") or {}).get("expected_dialog") or "").split("/")[0].strip()
        lines = [f"\nCandidates sharing the dialog '{dialog}' — tell them apart by FIELD STATES "
                 f"(visual_state.field_values / labels), not by the dialog title:"]
        for n in sorted(members, key=lambda m: m.get("step_number", 0)):
            others = set().union(*(s for nid, s in norm_sets.items() if nid != n["id"]))
            distinct = [k for k in kws(n) if _norm_text(k) not in others][:8]
            lines.append(f"  - {n['id']} (step {n.get('step_number')}): " + ("; ".join(distinct) if distinct else "(no distinguishing state listed)"))
        if last_node_id and last_node_id in group:
            why = f"the last confirmed step {last_node_id} is in this group, so its successor is expected next"
        elif last_node_id:
            why = f"no step of this group is confirmed yet (last confirmed: {last_node_id}), so the earliest step of the group is expected"
        else:
            why = "no step is confirmed yet, so the earliest step of the group is expected"
        lines.append(f"Graph-order prior: {pref} — {why}. Pick another member of the group ONLY if a field state listed for it "
                     f"is literally present in visual_state and the prior's states are contradicted.")
        return "\n".join(lines)

    def _history_advance(self, picked_id: str, candidates: List[Dict], last_node_id: Optional[str],
                         completed_steps: Optional[List[str]]) -> str:
        """R2 (study 3): the rerank repeated the last confirmed node, but the previous instruction
        already told the user to do that node's outgoing action -> the user is on the successor."""
        if not last_node_id or picked_id != last_node_id:
            return picked_id
        hist = [h for h in (completed_steps or []) if h]
        if not hist:
            return picked_id
        succ = self.graph.get_next_steps(last_node_id)
        if len(succ) != 1:
            return picked_id
        edge_instr = succ[0].get("edge_instruction") or ""
        if not _edge_covered(hist[-1], edge_instr):
            return picked_id
        nxt = succ[0]["id"]
        if not any(c["node"].get("id") == nxt for c in candidates):
            node = self.graph.get_node(nxt)
            if node:
                candidates.append({"node": node, "sources": ["advance"]})
        print(f"[GUIDE] history-advance: {picked_id} -> {nxt} (previous instruction covered the edge)")
        _LAST_LOCALIZE_META["route_advance"] = {"from": picked_id, "to": nxt}
        return nxt

    def _session_sticky(self, picked_id: str, candidates: List[Dict], session_wf: Optional[str],
                        last_node_id: Optional[str]) -> str:
        """R1 (study 2): keep the session's workflow when the rerank jumped to another workflow's
        node that shows the same dialog title as a session-workflow candidate."""
        n = self.graph.get_node(picked_id)
        if not n or not session_wf or n.get("workflow_id") == session_wf:
            return picked_id
        key = _norm_text(((n.get("visual_signature") or {}).get("expected_dialog") or "").split("/")[0])
        if not key:
            return picked_id
        same = [c["node"] for c in candidates if c["node"].get("workflow_id") == session_wf
                and _norm_text(((c["node"].get("visual_signature") or {}).get("expected_dialog") or "").split("/")[0]) == key]
        if not same:
            return picked_id
        allowed = ({last_node_id} | {x["id"] for x in self.graph.get_next_steps(last_node_id)}) if last_node_id else set()
        pref = ([x for x in same if x["id"] in allowed and x["id"] != last_node_id]
                or [x for x in same if x["id"] in allowed] or same)
        chosen = pref[0]["id"]
        print(f"[GUIDE] session-sticky override: {picked_id} -> {chosen} (session workflow {session_wf}, same dialog '{key}')")
        _LAST_LOCALIZE_META["route_sticky"] = {"from": picked_id, "to": chosen}
        return chosen

    def _tie_prior(self, emb_top: List[Tuple[str, float]], last_node_id: Optional[str]) -> Optional[str]:
        """Iteration 3 (c): among the top embedding candidates that share the same
        expected_dialog and lie within ROUTER_TIE_MARGIN of the group's best score,
        return the node preferred by graph order — the successor of the last
        confirmed node (or that node itself) if it is in the group, otherwise the
        node with the smallest step_number. None when there is no near-tie."""
        if not emb_top:
            return None
        groups: Dict[str, List[Tuple[str, float]]] = {}
        for nid, score in emb_top:
            n = self.graph.get_node(nid)
            if not n:
                continue
            key = _norm_text(((n.get("visual_signature") or {}).get("expected_dialog") or "").split("/")[0])
            if key:
                # iteration 4 correction: a group is formed within ONE workflow — nodes of
                # different workflows that share a dialog title are not ordered against
                # each other (survey_setup_05 vs d3_visualization_01, both "OpendTect Main Window").
                groups.setdefault(f"{n.get('workflow_id')}|{key}", []).append((nid, score))
        # iteration 4: consider the group holding the top-scoring candidate first
        ordered = sorted(groups.items(), key=lambda kv: -max(s for _, s in kv[1]))
        for key, members in ordered:
            if len(members) < 2:
                continue
            best = max(s for _, s in members)
            tied = [nid for nid, s in members if ROUTER_GROUP_PRIOR or best - s <= ROUTER_TIE_MARGIN]
            if len(tied) < 2:
                continue
            self._last_group = list(tied)
            if last_node_id and self.graph.get_node(last_node_id):
                allowed = {last_node_id} | {n["id"] for n in self.graph.get_next_steps(last_node_id)}
                by_graph = [nid for nid in tied if nid in allowed]
                if by_graph:
                    # successor preferred over the last node itself
                    succ = [nid for nid in by_graph if nid != last_node_id]
                    pick = min(succ or by_graph, key=lambda nid: self.graph.get_node(nid).get("step_number", 0))
                    print(f"[GUIDE] tie prior: {tied} -> {pick} (graph successor of {last_node_id})")
                    return pick
            pick = min(tied, key=lambda nid: self.graph.get_node(nid).get("step_number", 0))
            print(f"[GUIDE] tie prior: {tied} -> {pick} (earliest step)")
            return pick
        return None

    def _evidence_check(self, node: Dict, visual_state: Dict, last_node_id: Optional[str]) -> Dict[str, Any]:
        """Evidence-based verification of a rerank pick (v3 iteration 2)."""
        from . import node_matcher
        sig = node.get("visual_signature") or {}
        screen = " ".join([str(visual_state.get("current_dialog") or "")] + node_matcher._lst(visual_state, "window_titles"))
        screen_n = _norm_text(screen)
        parts = [p.strip() for p in re.split(r"/|\bor\b|\|", str(sig.get("expected_dialog") or "")) if len(_norm_text(p)) >= 4]
        matched = [p for p in parts if _norm_text(p) in screen_n]
        i_ok = bool(matched)
        ii_ok = False
        if last_node_id and self.graph.get_node(last_node_id):
            ii_ok = node["id"] == last_node_id or node["id"] in {n["id"] for n in self.graph.get_next_steps(last_node_id)}
        emb_top = _LAST_LOCALIZE_META.get("emb_top") or []
        gap = (emb_top[0][1] - emb_top[1][1]) if len(emb_top) >= 2 else (emb_top[0][1] if emb_top else 0.0)
        iii_ok = bool(emb_top) and emb_top[0][0] == node["id"] and gap >= ROUTER_EMB_GAP
        return {"ok": bool(i_ok or ii_ok or iii_ok), "i_dialog": i_ok, "ii_graph": ii_ok, "iii_gap": iii_ok,
                "gap": round(float(gap), 4), "emb_top1": emb_top[0][0] if emb_top else None,
                "matched_dialog": matched[:2], "has_last": bool(last_node_id)}

    def _terminal_nodes(self, workflow_id: Optional[str]) -> List[Dict]:
        """Final action node(s) of a workflow: no successors, or every successor is a
        verification/terminal node (the verification nodes themselves included)."""
        if not workflow_id:
            return []
        out = []
        for n in self.graph.get_workflow_nodes(workflow_id):
            succ = self.graph.get_next_steps(n["id"])
            if not succ or all((s.get("step_type") or "") in _TERMINAL_STEP_TYPES for s in succ):
                out.append(n)
        return out

    def _goal_state_check(self, visual_state: Dict, picked_id: Optional[str],
                          last_node_id: Optional[str]) -> Optional[Dict]:
        """Return the terminal node whose completion state the screen matches, or None.
        Condition A: the last confirmed node or the current (pre-gate) pick is a terminal
        node of its workflow. Condition B: among that workflow's nodes, the screen
        (vision output) is closest to a terminal node."""
        from . import node_matcher
        if not visual_state:
            return None
        # iteration 3: anchors = the last confirmed node (user spec), plus the current
        # pre-gate pick only when it is a successor of the last confirmed node (the
        # router believes the final action was reached through a valid transition).
        anchors: List[str] = []
        if last_node_id and self.graph.get_node(last_node_id):
            anchors.append(last_node_id)
            if (picked_id and picked_id != last_node_id and self.graph.get_node(picked_id)
                    and picked_id in {n["id"] for n in self.graph.get_next_steps(last_node_id)}):
                anchors.append(picked_id)
        for nid in anchors:
            wf = self.graph.get_node(nid).get("workflow_id")
            terminals = self._terminal_nodes(wf)
            term_ids = {t["id"] for t in terminals}
            if nid not in term_ids:
                continue
            try:
                top = node_matcher.top_k(visual_state, self.graph.get_workflow_nodes(wf), k=1)
            except Exception as e:
                print(f"[GUIDE] goal-state matcher failed: {e}")
                return None
            if top and top[0][0].get("id") in term_ids:
                node = top[0][0]
                print(f"[GUIDE] goal-state hint: anchor={nid} screen≈{node['id']} (cos={top[0][1]:.3f})")
                return node
            if top and GOAL_STATE_MARGIN > 0:
                scored = sorted(node_matcher.score_nodes(visual_state, self.graph.get_workflow_nodes(wf)), key=lambda p: -p[1])
                best = scored[0][1] if scored else 0.0
                for n, s in scored:
                    if n.get("id") in term_ids and best - s <= GOAL_STATE_MARGIN:
                        print(f"[GUIDE] goal-state hint (margin): anchor={nid} terminal {n['id']} cos={s:.3f} vs top {scored[0][0]['id']} {best:.3f}")
                        return n
        return None

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

        goal_state = pipeline_output.get("goal_state")
        if goal_state:
            sig = goal_state.get("visual_signature") or {}
            evidence = "; ".join(x for x in [
                f"expected dialog/screen: {sig.get('expected_dialog')}" if sig.get("expected_dialog") else "",
                ("expected elements: " + ", ".join(str(e).replace("_", " ") for e in (sig.get("expected_ui_elements") or [])[:8]))
                if sig.get("expected_ui_elements") else "",
            ] if x)
            parts.append(
                "[Goal State Check]\n"
                f"The workflow's final step appears to be reached: '{goal_state.get('title', '')}' — {goal_state.get('description', '')}\n"
                + (f"Completion state of this step: {evidence}\n" if evidence else "")
                + "If the screenshot shows that the goal is achieved, respond with the completion sentinel only "
                "('완료' / 'Done'). If one action is still missing, give only that action."
            )

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
        next_nodes = pipeline_output.get("next_nodes") or []
        if current and CONTEXT_ASSEMBLY != "v3":
            sig = current.get("visual_signature") or {}
            state_bits = []
            if sig.get("expected_dialog"):
                state_bits.append(f"dialog/screen: {sig['expected_dialog']}")
            els = [str(e).replace("_", " ") for e in (sig.get("expected_ui_elements") or [])]
            if els:
                state_bits.append("elements: " + ", ".join(els))
            kws = [str(k) for k in (sig.get("screenshot_keywords") or [])]
            if kws:
                state_bits.append("states: " + "; ".join(kws))
            parts.append(
                f"[Current State (reached)] {current.get('workflow_id', '')} > "
                f"Step {current.get('step_number', '?')}: {current.get('title', '')}\n"
                + ("The screen at this step shows — " + " | ".join(state_bits) if state_bits else "")
            )
            def _act(n):
                cond = f" [if: {n.get('edge_condition')}]" if n.get("edge_condition") else ""
                instr = n.get("edge_instruction") or f"Step {n.get('step_number', '?')} {n.get('title', '')}"
                return f"  - {instr}{cond}  (→ Step {n.get('step_number', '?')}: {n.get('title', '')})"
            handled = False
            if CONTEXT_ASSEMBLY == "v7" and next_nodes:
                # C1: an action with no visible effect (Lock, a display toggle) cannot be seen on the
                # screenshot; if the previous instruction already gave this edge's action, do not
                # repeat it - declare the goal (terminal / goal-state) or advance to the next edge.
                hist = [h for h in (pipeline_output.get("completed_steps") or []) if h]
                last = (hist[-1] if hist else "").strip()
                first = next_nodes[0]
                if last and _edge_covered(last, first.get("edge_instruction") or ""):
                    nn2 = pipeline_output.get("next_nodes_2") or []
                    if goal_state or (first.get("step_type") or "") in _TERMINAL_STEP_TYPES or not nn2:
                        parts.append(_CTX_V7_DONE.format(prev=last[:160]))
                    else:
                        parts.append(_CTX_V7_ADVANCE.format(prev=last[:160]) + "\n" + "\n".join(_act(n) for n in nn2) + "\n" + _CTX_V6_RULE)
                    handled = True
            if not handled:
                if next_nodes:
                    parts.append("[Next Action] (from the workflow edge)\n" + "\n".join(_act(n) for n in next_nodes)
                                 + ("\n" + _CTX_V6_RULE if CONTEXT_ASSEMBLY in ("v6", "v7") else ""))
                else:
                    parts.append("[Next Action] This is the final step of the workflow; if the screen shows the goal achieved, answer with the completion sentinel.")
            parts.append(_CTX_NOTE)
        elif current:
            parts.append(
                f"[Current Step] {current.get('workflow_id', '')} > "
                f"Step {current.get('step_number', '?')}: {current.get('title', '')}\n"
                f"Description: {current.get('description', '')}"
            )
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
