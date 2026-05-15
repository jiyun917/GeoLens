"""
Benchmark backends — four side-by-side strategies for procedural UI
guidance, used by ScenarioEvaluator to produce paper-quality comparison
numbers.

Each backend is a callable with signature

    backend(step_index: int, scenario: dict, prior_responses: list[str]) -> str

It returns ONE instruction string (the predicted next action for that
step). The framework loads `scenario.steps[step_index].screenshot_path`
from disk, feeds it through the backend-specific pipeline, and the
ScenarioEvaluator scores the response against the step's ground-truth.

Backends:
  1. vanilla_vector  — pure ChromaDB vector RAG, no workflow graph,
                       no CLIP. Baseline floor.
  2. graph_only      — workflow keyword localizer + linked-chunks
                       retrieval. No CLIP, no LLM rerank.
  3. vision_only     — CLIP-based localizer alone. No keyword, no rerank.
  4. full_system     — the production hybrid (keyword + CLIP + Gemini
                       rerank + Claude Sonnet generation).

All backends share the same downstream generator (Claude / Gemini)
controlled by env vars. They differ ONLY in how the RAG context is
selected.
"""

import base64
import json
import os
from typing import Callable, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────

def _load_screenshot_b64(scenario: Dict, step_index: int) -> Optional[str]:
    """Resolve scenario.steps[i].screenshot_path → base64 data URL."""
    steps = scenario.get("steps") or []
    if step_index < len(steps):
        path = steps[step_index].get("screenshot_path")
    else:
        path = (scenario.get("completion") or {}).get("final_screenshot_path")
    if not path:
        return None
    abs_path = path
    if not os.path.isabs(abs_path):
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        abs_path = os.path.join(root, path)
    if not os.path.exists(abs_path):
        return None
    with open(abs_path, "rb") as f:
        data = f.read()
    ext = abs_path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def _build_messages(scenario: Dict, step_index: int, prior_responses: List[str],
                    context_block: str = "") -> List[Dict]:
    """Build OpenAI-style messages for the generator LLM.

    system: action prompt with goal + completedSteps + context_block
    user (final): the screenshot for this step + user-message hint
    """
    # We don't have a Python port of lib/prompts/action.ts here, so inline a
    # minimal generator-side prompt. The benchmark exercises the RAG context
    # selection (where backends differ) more than the prompt scaffolding.
    goal = scenario.get("goal", "")
    language = scenario.get("language", "en")
    completed = list(prior_responses)
    sys_text = _inline_action_prompt(goal, completed, context_block, language)
    user_content: List[Dict] = []
    b64 = _load_screenshot_b64(scenario, step_index)
    if b64:
        user_content.append({"type": "image_url", "image_url": {"url": b64}})
    user_content.append({"type": "text", "text": "What is the next single action?"})
    return [
        {"role": "system", "content": sys_text},
        {"role": "user", "content": user_content},
    ]


def _inline_action_prompt(goal: str, completed: List[str], context_block: str,
                          language: str) -> str:
    lang = "한국어" if language == "ko" else "English"
    steps_section = ""
    if completed:
        body = "\n".join(f"{i+1}. {t}" for i, t in enumerate(completed[-6:]))
        steps_section = f"\n\n# Steps Already Completed\n{body}"
    ctx_section = f"\n\n# Reference Manual Context\n{context_block}" if context_block else ""
    return (
        f"You are a UI navigation assistant. Respond in {lang}.\n"
        "Output ONE action only based on what you see in the screenshot.\n"
        "Goal-complete sentinel: respond exactly 'Done' (or '완료').\n"
        f"\n# Goal\n{goal}"
        f"{steps_section}{ctx_section}\n"
        "\nResponse Format: one short instruction; no bullets, no explanation."
    )


def _call_generator(messages: List[Dict]) -> str:
    """Run the messages through Claude Sonnet (preferred) or Gemini Flash.
    Returns the assistant text or "" on failure."""
    # Try Claude first
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            sys_text = ""
            claude_msgs = []
            for m in messages:
                if m["role"] == "system":
                    c = m["content"]
                    sys_text = c if isinstance(c, str) else " ".join(
                        p.get("text", "") for p in c if p.get("type") == "text"
                    )
                    continue
                role = m["role"]
                content = m["content"]
                if isinstance(content, str):
                    claude_msgs.append({"role": role, "content": content})
                else:
                    parts = []
                    for p in content:
                        if p.get("type") == "text":
                            parts.append({"type": "text", "text": p["text"]})
                        elif p.get("type") == "image_url":
                            url = p["image_url"]["url"]
                            if url.startswith("data:image/"):
                                header, data = url.split(",", 1)
                                mt = header.split(";")[0].split(":")[1]
                                parts.append({
                                    "type": "image",
                                    "source": {"type": "base64", "media_type": mt, "data": data},
                                })
                    if parts:
                        claude_msgs.append({"role": role, "content": parts})
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=512,
                system=sys_text,
                messages=claude_msgs,
            )
            return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
        except Exception as e:
            print(f"[BENCH] Claude call failed: {e}")

    # Fallback: Gemini Flash
    gkey = os.environ.get("GEMINI_API_KEY")
    if gkey:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gkey, http_options=types.HttpOptions(timeout=30_000))
            # Flatten to Gemini format
            from api.routers.task import convert_openai_to_gemini  # type: ignore
            sys_text = ""
            non_sys = []
            for m in messages:
                if m["role"] == "system":
                    c = m["content"]
                    sys_text = c if isinstance(c, str) else " ".join(
                        p.get("text", "") for p in c if p.get("type") == "text"
                    )
                else:
                    non_sys.append(m)
            contents = convert_openai_to_gemini(non_sys)
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=types.Content(
                        parts=[types.Part.from_text(text=sys_text)]
                    ) if sys_text else None,
                ),
            )
            return (resp.text or "").strip()
        except Exception as e:
            print(f"[BENCH] Gemini fallback failed: {e}")
    return ""


# ─────────────────────────────────────────────────────────────────────
# Backend 1: vanilla_vector
# ─────────────────────────────────────────────────────────────────────

def backend_vanilla_vector(step_index: int, scenario: Dict,
                            prior_responses: List[str]) -> str:
    from .rag import get_manual_context
    manual_ids = [scenario["manual_id"]]
    # Query = user goal (no workflow / no visual signal)
    query = scenario.get("goal", "")
    ctx = get_manual_context(manual_ids, query, top_k=5) or ""
    messages = _build_messages(scenario, step_index, prior_responses, context_block=ctx)
    return _call_generator(messages)


# ─────────────────────────────────────────────────────────────────────
# Backend 2: graph_only — keyword localizer + linked_chunks
# ─────────────────────────────────────────────────────────────────────

def backend_graph_only(step_index: int, scenario: Dict,
                       prior_responses: List[str]) -> str:
    from .guide_pipeline import get_guide_pipeline
    pipeline = get_guide_pipeline()
    screenshot_b64 = _load_screenshot_b64(scenario, step_index)
    visual_state = pipeline.recognize_visual_state(screenshot_b64) if screenshot_b64 else {}
    # Use ONLY keyword localizer
    node, score = pipeline.graph.get_current_node(visual_state)
    ctx_parts: List[str] = []
    if node:
        ctx_parts.append(
            f"[Current Step] {node.get('workflow_id','')} > "
            f"Step {node.get('step_number','?')}: {node.get('title','')}\n"
            f"Description: {node.get('description','')}"
        )
        # next steps
        for n in pipeline.graph.get_next_steps(node["id"]):
            ctx_parts.append(
                f"[Possible Next] Step {n.get('step_number','?')} {n.get('title','')}"
            )
    context_block = "\n\n".join(ctx_parts)
    messages = _build_messages(scenario, step_index, prior_responses, context_block=context_block)
    return _call_generator(messages)


# ─────────────────────────────────────────────────────────────────────
# Backend 3: vision_only — CLIP localizer alone
# ─────────────────────────────────────────────────────────────────────

def backend_vision_only(step_index: int, scenario: Dict,
                        prior_responses: List[str]) -> str:
    from .visual_matcher import get_visual_matcher
    from .workflow_graph import get_workflow_graph
    matcher = get_visual_matcher()
    wg = get_workflow_graph()
    screenshot_b64 = _load_screenshot_b64(scenario, step_index)
    if not screenshot_b64 or not matcher.available():
        return _call_generator(_build_messages(scenario, step_index, prior_responses))
    node, score = matcher.match_to_workflow_node(
        screenshot_b64, scenario["manual_id"], wg
    )
    ctx = ""
    if node:
        ctx = (
            f"[Current Step] {node.get('workflow_id','')} > "
            f"Step {node.get('step_number','?')}: {node.get('title','')}\n"
            f"Description: {node.get('description','')}"
        )
    messages = _build_messages(scenario, step_index, prior_responses, context_block=ctx)
    return _call_generator(messages)


# ─────────────────────────────────────────────────────────────────────
# Backend 4: full_system — production hybrid (keyword + CLIP + rerank)
# ─────────────────────────────────────────────────────────────────────

def backend_full_system(step_index: int, scenario: Dict,
                        prior_responses: List[str]) -> str:
    from .rag_router import get_rag_router
    screenshot_b64 = _load_screenshot_b64(scenario, step_index)
    visited_node_ids: List[str] = []
    # Reconstruct visited by re-running localizer on each prior step's screenshot
    # — heuristic; for honest benchmarking we accept that visited tracking
    # depends on what the same backend matched at earlier steps.
    if step_index > 0:
        from .guide_pipeline import get_guide_pipeline
        pipeline = get_guide_pipeline()
        for j in range(step_index):
            prev_b64 = _load_screenshot_b64(scenario, j)
            if not prev_b64:
                continue
            vs = pipeline.recognize_visual_state(prev_b64)
            loc = pipeline.localize_to_graph(
                vs, None, screenshot_b64=prev_b64,
                manual_ids=[scenario["manual_id"]],
                user_goal=scenario.get("goal", ""),
                visited_node_ids=list(visited_node_ids),
            )
            n = loc.get("node")
            if n and n["id"] not in visited_node_ids:
                visited_node_ids.append(n["id"])

    session_state = {
        "mode": "guide",
        "visited_node_ids": visited_node_ids,
    }
    result = get_rag_router().route(
        user_message=scenario.get("goal", ""),
        screenshot_b64=screenshot_b64,
        session_state=session_state,
        manual_ids=[scenario["manual_id"]],
    )
    context_block = result.get("context_block", "") or ""
    messages = _build_messages(scenario, step_index, prior_responses, context_block=context_block)
    return _call_generator(messages)


# ─────────────────────────────────────────────────────────────────────
# Registry — used by run_benchmark.py
# ─────────────────────────────────────────────────────────────────────

BACKEND_REGISTRY: Dict[str, Callable[[int, Dict, List[str]], str]] = {
    "vanilla_vector": backend_vanilla_vector,
    "graph_only":     backend_graph_only,
    "vision_only":    backend_vision_only,
    "full_system":    backend_full_system,
}
