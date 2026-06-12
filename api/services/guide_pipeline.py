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
from typing import Any, Dict, List, Optional, Tuple

from .workflow_graph import WorkflowGraph, get_workflow_graph
from .graph_retriever import GraphRetriever, get_graph_retriever


VISUAL_STATE_PROMPT = """You are analyzing a screenshot of the OpendTect geophysics software.
Extract the current UI state into JSON:

{
  "current_dialog": "name of the currently visible dialog/window",
  "active_menu": "currently active menu or tab, if visible",
  "visible_elements": ["key UI elements visible on screen"],
  "data_state": "state of data loaded (e.g., '3D seismic loaded', 'none')",
  "current_action": "what action appears to be in progress"
}

Respond with JSON only, no markdown fences, no explanation."""


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
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {}

        from google import genai
        from google.genai import types
        import base64 as b64module
        import time as _time, random as _random

        try:
            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=30_000),
            )

            # Extract base64 payload
            b64_data = screenshot_b64
            mime = "image/jpeg"
            if screenshot_b64.startswith("data:image/"):
                header, b64_data = screenshot_b64.split(",", 1)
                try:
                    mime = header.split(";")[0].split(":")[1]
                except Exception:
                    mime = "image/jpeg"

            image_bytes = b64module.b64decode(b64_data)

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=VISUAL_STATE_PROMPT),
                        types.Part.from_bytes(data=image_bytes, mime_type=mime),
                    ],
                )
            ]
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0,
            )

            MAX_RETRY = 3
            for attempt in range(MAX_RETRY + 1):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", contents=contents, config=config
                    )
                    return _extract_json(response.text) or {}
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
    ) -> Dict:
        """
        Match visual state to a workflow graph node using:
          1. Top-K keyword candidates (on visual_signature)
          2. Top-K CLIP image candidates (on manual screenshots)
          3. Gemini rerank over the combined candidate set

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
        # So we prefer keyword matching whenever it has real signal, and only
        # fall back to CLIP when keyword gives no answer at all.
        KW_TRUST_FLOOR = 0.20      # kw ≥ this → trust keyword, ignore CLIP
        CLIP_MIN_SCORE = 0.85      # CLIP must be this confident to override silence

        clip_node = None
        clip_score = 0.0
        if screenshot_b64 and manual_ids:
            try:
                from .visual_matcher import get_visual_matcher
                matcher = get_visual_matcher()
                if matcher.available():
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

        # Build top-K candidate pool (keyword top-3 + CLIP top-3, dedup by node id)
        kw_top = self.graph.get_top_k_nodes(visual_state, k=3, hint_workflow_id=hint_workflow_id)
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
        for node, score in kw_top + clip_top:
            nid = node.get("id")
            if not nid or nid in seen_ids:
                continue
            seen_ids.add(nid)
            candidates.append({"node": node, "source_score": score})

        print(f"[GUIDE] candidates: {len(candidates)} (kw_top={len(kw_top)}, clip_top={len(clip_top)})")

        # Ask Gemini to pick the best candidate (authoritative signal).
        # visited_node_ids tells it which nodes the user has already passed,
        # so if the screenshot still looks like one of them (common when a
        # wizard dialog stays up after Import) it should advance to the
        # successor instead of repeating.
        if candidates:
            picked_id, picked_conf = self._llm_rerank_candidates(
                candidates, visual_state, user_goal,
                visited_node_ids=visited_node_ids,
            )
            if picked_id:
                for c in candidates:
                    if c["node"].get("id") == picked_id:
                        node = c["node"]
                        print(f"[GUIDE] localize via LLM rerank: node={picked_id} conf={picked_conf:.2f}")
                        return {"node": node, "confidence": picked_conf, "match_method": "llm"}

            # LLM rerank returned "none" OR failed after retries.
            # Do NOT fall back to keyword top-1 — keyword matching latches
            # onto generic UI terms (Scene, Window, Cross-line) and routinely
            # picks a wrong workflow whose manual context misleads the guide
            # LLM. Returning node=None lets RAG vector search supply chunks
            # by user_message similarity instead — better than wrong context.
            print(f"[GUIDE] LLM rerank gave no answer - node=None (vector RAG will provide context)")
            return {"node": None, "confidence": 0.0, "match_method": "none"}

        # No candidates at all — fall back to single-best keyword
        print(f"[GUIDE] no candidates; fallback node={kw_node.get('id') if kw_node else None} score={kw_score:.3f}")
        return {"node": kw_node, "confidence": kw_score, "match_method": "keyword"}

    def _llm_rerank_candidates(
        self,
        candidates: List[Dict],
        visual_state: Dict,
        user_goal: str,
        visited_node_ids: Optional[List[str]] = None,
    ) -> Tuple[Optional[str], float]:
        """Ask Gemini Flash to pick the candidate whose workflow step best
        matches the user's current situation. Returns (node_id, confidence 0-1)
        or (None, 0.0) if no candidate fits or Gemini fails."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None, 0.0

        # Build a compact candidate list for the prompt
        lines = []
        for i, c in enumerate(candidates, start=1):
            n = c["node"]
            wf = (n.get("workflow_id") or "").replace("auto_", "").split("__", 1)[-1]
            title = (n.get("title") or "")[:80]
            desc = (n.get("description") or "")[:120]
            step = n.get("step_number", "?")
            lines.append(f'{i}. id="{n.get("id")}" workflow="{wf}" step={step}\n   title: {title}\n   desc: {desc}')
        candidate_block = "\n".join(lines)

        goal_line = f"User goal: {user_goal.strip()}" if user_goal.strip() else "User goal: (unspecified)"
        vs_line = json.dumps(visual_state, ensure_ascii=False)[:500]

        visited_line = ""
        if visited_node_ids:
            # Only mention ones that actually appear in the candidate pool
            candidate_ids = {c["node"].get("id") for c in candidates}
            visited_in_pool = [v for v in visited_node_ids if v in candidate_ids]
            if visited_in_pool:
                visited_line = (
                    "\nAlready-completed candidate nodes (the user has finished these — "
                    "DO NOT pick one of these again if the screenshot shows the same state "
                    "after completion; prefer a candidate that represents the NEXT step, "
                    "or return \"none\" to let the user discover the Close/Finish button "
                    "themselves): " + ", ".join(visited_in_pool)
                )

        prompt = f"""You rank workflow steps by how well they match the user's current UI situation.

{goal_line}
Current UI visual_state JSON: {vs_line}{visited_line}

Candidate workflow steps (from a software manual):
{candidate_block}

Pick the candidate whose step description best matches what the user is CURRENTLY doing or trying to do next — aligned to both the goal and the visible UI state.

DECISION RULE — bias toward PICKING a candidate:
- If ANY candidate's title/description shares the dialog name, screen name, or topic with the visual_state, PICK that candidate. Confidence in [0.5, 0.9] is fine for partial matches; use higher only when title essentially names what's on screen.
- Returning "none" is ONLY for cases where NO candidate is even loosely related (different application, different module, totally unrelated topic).
- Picking a slightly-imperfect candidate is better than "none", because downstream logic uses the picked node for state tracking (post-completion detection, next-step hints). Returning "none" disables those.

IMPORTANT — wizard dialogs stay on screen after their action completes:
- If the screenshot still looks like a candidate the user ALREADY completed (see "Already-completed" list above), they are NOT re-doing it. The wizard just hasn't been dismissed yet.
- In that case, prefer a NEXT candidate in the same workflow, OR (if no next exists) STILL pick the visited candidate — downstream code will detect post-completion from that match.

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
        )

        RERANK_MAX_RETRIES = 3
        RERANK_BASE_BACKOFF = 1.5
        raw = ""
        last_err = None
        for attempt in range(RERANK_MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=cfg,
                )
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

        # Step 1: Recognize visual state
        visual_state: Dict = {}
        if screenshot_b64:
            visual_state = self.recognize_visual_state(screenshot_b64)

        # Step 2: Detect intent
        intent = self._detect_intent(user_message)

        # Step 3: Localize (keyword + CLIP top-K → Gemini rerank)
        hint = session_history.get("active_workflow_id")
        visited = session_history.get("visited_node_ids") or []
        localization = self.localize_to_graph(
            visual_state,
            hint,
            screenshot_b64=screenshot_b64,
            manual_ids=manual_ids,
            user_goal=user_message,
            visited_node_ids=visited,
        )
        current_node = localization["node"]
        confidence = localization["confidence"]
        current_node_id = current_node["id"] if current_node else None

        # Step 4: Retrieve context
        retrieval = self.retriever.hybrid_retrieve(
            current_node_id=current_node_id,
            query=user_message,
            intent=intent,
            manual_ids=manual_ids,
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

        # Post-completion override — place at TOP so it wins over manual context.
        if pipeline_output.get("post_completion"):
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

        graph_ctx = pipeline_output.get("graph_context") or []
        for g in graph_ctx[:3]:
            if g.get("text"):
                parts.append(f"[Manual Context (graph)]\n{g['text'][:800]}")

        vector_ctx = pipeline_output.get("vector_context")
        if vector_ctx:
            parts.append(f"[Manual Context (vector)]\n{vector_ctx[:1500]}")

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
