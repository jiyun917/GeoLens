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
import re
import sys
from typing import Callable, Dict, List, Optional

# Belt + suspenders: same UTF-8 fix as bench_runner. Any module in the
# call chain that prints Unicode without this will crash on Windows cp949
# and silently be caught by the evaluator's try/except.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


# ─────────────────────────────────────────────────────────────────────
# Generator model selection
#
# Set BENCH_MODEL env var to switch which LLM generates responses:
#   "gemini"  — Gemini 2.5 Pro (default, matches production /step primary)
#   "claude"  — Claude Sonnet 4.6 (sub-agent in production)
#   "qwen"    — Qwen3-235B-A22B-Instruct hosted at NAS (INT4 GPTQ)
#   "gpt"     — GPT-4o (requires OPENAI_API_KEY, not yet wired)
# ─────────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "gemini"
QWEN_BASE_URL = "http://168.131.141.77:28000/v1"
QWEN_MODEL = "qwen3-235b-a22b-instruct"
QWEN_API_KEY = "EMPTY"  # vLLM does not validate the key


# Per-model USD per 1M tokens (input, output). Self-hosted = 0 (or GPU-time
# equivalent to be reported in prose). Prices reflect 2026-07 published rates.
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gemini":       {"in_per_m": 1.25, "out_per_m": 10.00, "label": "gemini-2.5-pro"},
    "gemini_flash": {"in_per_m": 0.30, "out_per_m": 2.50,  "label": "gemini-2.5-flash"},
    "claude":       {"in_per_m": 3.00, "out_per_m": 15.00, "label": "claude-sonnet-4-6"},
    "gpt":          {"in_per_m": 2.50, "out_per_m": 10.00, "label": "gpt-4o"},
    "qwen":         {"in_per_m": 0.00, "out_per_m": 0.00,  "label": "qwen3-235b-a22b-instruct (self-hosted)"},
}


# Module-level scratch space for the most recent call's token usage. The
# bench_runner reads this immediately after each backend call so we don't
# have to refactor every backend signature. Reset before each call.
_LAST_USAGE: Dict[str, float] = {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "model": ""}


def _reset_usage() -> None:
    _LAST_USAGE["input_tokens"] = 0
    _LAST_USAGE["output_tokens"] = 0
    _LAST_USAGE["cost_usd"] = 0.0
    _LAST_USAGE["model"] = ""


def _record_usage(model: str, input_tokens: int, output_tokens: int) -> None:
    price = MODEL_PRICING.get(model, {"in_per_m": 0.0, "out_per_m": 0.0})
    cost = (input_tokens / 1_000_000) * price["in_per_m"] + (output_tokens / 1_000_000) * price["out_per_m"]
    _LAST_USAGE["input_tokens"] = int(input_tokens)
    _LAST_USAGE["output_tokens"] = int(output_tokens)
    _LAST_USAGE["cost_usd"] = round(cost, 6)
    _LAST_USAGE["model"] = model


def get_last_usage() -> Dict[str, float]:
    """Snapshot of the token usage + cost of the most recent LLM call.
    bench_runner uses this to attach per-step cost."""
    return dict(_LAST_USAGE)


def _get_bench_model() -> str:
    return os.environ.get("BENCH_MODEL", DEFAULT_MODEL).lower().strip() or DEFAULT_MODEL


def _strip_thinking(text: str) -> str:
    """Remove <think>...</think> reasoning blocks emitted by Qwen3-instruct
    style models. Also strips a trailing bare </think> in case the closing
    tag survives a truncated stream."""
    if not text:
        return ""
    text = re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL)
    text = re.sub(r"^\s*</think>\s*", "", text)
    return text.strip()


def _messages_to_text_only(messages: List[Dict]) -> List[Dict]:
    """Flatten multimodal messages to text-only for models that don't accept
    images. Qwen3-235B-Instruct is a text-only variant."""
    flat: List[Dict] = []
    for m in messages:
        content = m.get("content")
        if isinstance(content, str):
            flat.append({"role": m["role"], "content": content})
        elif isinstance(content, list):
            parts = [p.get("text", "") for p in content if p.get("type") == "text"]
            joined = "\n".join(t for t in parts if t)
            flat.append({"role": m["role"], "content": joined or "(image omitted — text-only model)"})
        else:
            flat.append({"role": m["role"], "content": str(content or "")})
    return flat


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


def _call_claude(messages: List[Dict]) -> str:
    """Claude Sonnet 4.6 — full multimodal (accepts images)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[BENCH] Claude skipped: ANTHROPIC_API_KEY not set")
        return ""
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
        usage = getattr(resp, "usage", None)
        if usage is not None:
            _record_usage("claude", getattr(usage, "input_tokens", 0), getattr(usage, "output_tokens", 0))
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
    except Exception as e:
        print(f"[BENCH] Claude call failed: {e}")
        return ""


def _call_gemini_variant(messages: List[Dict], model_id: str, usage_tag: str) -> str:
    """Call Gemini with automatic retry on empty responses. Empty text under
    FinishReason.STOP with normal token usage has been observed sporadically
    (likely transient API-side truncation or reasoning-token exhaustion in
    parallel-load conditions). We retry up to 3 times with a short backoff;
    on every retry we log the raw candidate metadata so we can spot patterns."""
    import time as _t
    gkey = os.environ.get("GEMINI_API_KEY")
    if not gkey:
        print(f"[BENCH] {usage_tag} skipped: GEMINI_API_KEY not set")
        return ""
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=gkey, http_options=types.HttpOptions(timeout=120_000))
        from api.routers.task import convert_openai_to_gemini  # type: ignore
    except Exception as e:
        print(f"[BENCH] {usage_tag} client init failed: {e}")
        return ""

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
    # NOTE: Do NOT set max_output_tokens for Gemini 2.5 thinking models.
    # Thinking tokens (`thoughts_token_count`) are billed separately but
    # observably eat into the completion budget under load — an explicit
    # small ceiling here caused a repeatable "thinks a lot, returns empty"
    # failure pattern in earlier runs. Leave it unset (Google default is
    # generous enough for our 1-instruction responses).
    config = types.GenerateContentConfig(
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=sys_text)]
        ) if sys_text else None,
    )

    last_um = None
    for attempt in range(1, 4):
        try:
            resp = client.models.generate_content(
                model=model_id,
                contents=contents,
                config=config,
            )
        except Exception as e:
            print(f"[BENCH] {usage_tag} attempt {attempt} exception: {e}")
            _t.sleep(2)
            continue

        text = (resp.text or "").strip()
        last_um = getattr(resp, "usage_metadata", None)

        if text:
            if last_um is not None:
                _record_usage(
                    usage_tag,
                    getattr(last_um, "prompt_token_count", 0) or 0,
                    getattr(last_um, "candidates_token_count", 0) or 0,
                )
            return text

        # Empty response — dump diagnostics and retry
        cand = (resp.candidates or [None])[0]
        fr = str(getattr(cand, "finish_reason", None)) if cand else "no_candidate"
        pf = getattr(resp, "prompt_feedback", None)
        br = str(getattr(pf, "block_reason", None)) if pf else "none"
        pt = getattr(last_um, "prompt_token_count", None) if last_um else None
        ct = getattr(last_um, "candidates_token_count", None) if last_um else None
        tt = getattr(last_um, "total_token_count", None) if last_um else None
        print(
            f"[BENCH] {usage_tag} attempt {attempt} EMPTY: "
            f"finish_reason={fr} block_reason={br} tokens(p/c/t)={pt}/{ct}/{tt}"
        )
        _t.sleep(2 * attempt)  # 2s, 4s, 6s

    # All retries failed — record what we saw and return empty
    if last_um is not None:
        _record_usage(
            usage_tag,
            getattr(last_um, "prompt_token_count", 0) or 0,
            getattr(last_um, "candidates_token_count", 0) or 0,
        )
    print(f"[BENCH] {usage_tag} exhausted 3 retries, returning empty")
    return ""


def _call_gemini(messages: List[Dict]) -> str:
    """Gemini 2.5 Pro — full multimodal. Matches production /step primary."""
    return _call_gemini_variant(messages, "gemini-2.5-pro", "gemini")


def _call_gemini_flash(messages: List[Dict]) -> str:
    """Gemini 2.5 Flash — smaller/cheaper/faster sibling. Used to test
    whether RAG contributes more clearly when the base model is weaker."""
    return _call_gemini_variant(messages, "gemini-2.5-flash", "gemini_flash")


def _call_gpt(messages: List[Dict]) -> str:
    """GPT-4o via OpenAI API — full multimodal (accepts images in the
    OpenAI-native image_url format that our messages already use)."""
    okey = os.environ.get("OPENAI_API_KEY")
    if not okey:
        print("[BENCH] GPT skipped: OPENAI_API_KEY not set")
        return ""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=okey, timeout=90.0)
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=512,
        )
        u = getattr(resp, "usage", None)
        if u is not None:
            _record_usage("gpt", getattr(u, "prompt_tokens", 0) or 0, getattr(u, "completion_tokens", 0) or 0)
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"[BENCH] GPT call failed: {e}")
        return ""


def _call_qwen(messages: List[Dict]) -> str:
    """Qwen3-235B-A22B-Instruct (INT4 GPTQ) hosted at NAS vLLM endpoint.
    Text-only variant — images are stripped from messages. Reasoning
    <think>...</think> blocks are removed from the response."""
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url=QWEN_BASE_URL,
            api_key=QWEN_API_KEY,
            timeout=90.0,
        )
        flat = _messages_to_text_only(messages)
        resp = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=flat,
            max_tokens=1024,   # room for <think> block plus final answer
            temperature=0.2,
        )
        u = getattr(resp, "usage", None)
        if u is not None:
            _record_usage("qwen", getattr(u, "prompt_tokens", 0) or 0, getattr(u, "completion_tokens", 0) or 0)
        text = resp.choices[0].message.content or ""
        return _strip_thinking(text)
    except Exception as e:
        print(f"[BENCH] Qwen call failed: {e}")
        return ""


def _call_generator(messages: List[Dict]) -> str:
    """Dispatch to the model selected via BENCH_MODEL env var.
    Defaults to Gemini 2.5 Pro (production primary).
    Also resets and populates _LAST_USAGE — read via get_last_usage()."""
    _reset_usage()
    model = _get_bench_model()
    if model == "claude":
        return _call_claude(messages)
    if model == "qwen":
        return _call_qwen(messages)
    if model == "gpt":
        return _call_gpt(messages)
    if model in ("gemini_flash", "flash"):
        return _call_gemini_flash(messages)
    if model == "gemini":
        return _call_gemini(messages)
    print(f"[BENCH] Unknown BENCH_MODEL={model!r}, falling back to gemini")
    return _call_gemini(messages)


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
# Backend 5: state_path — Procedural State-Path Retrieval (PSPR, novel)
# ─────────────────────────────────────────────────────────────────────

def backend_state_path(step_index: int, scenario: Dict,
                       prior_responses: List[str]) -> str:
    """Localize anchor like full_system, then use StatePathRetriever to
    expand a temporal sub-path (prev → current → next) with per-step chunks,
    and inject the structured PROCEDURAL PATH block. The novelty is in the
    CONTEXT FORMAT — same generator, same localization, but path-structured
    context instead of an unordered chunk bag."""
    from .guide_pipeline import get_guide_pipeline
    from .state_path_retriever import get_state_path_retriever, format_step_path

    screenshot_b64 = _load_screenshot_b64(scenario, step_index)
    pipeline = get_guide_pipeline()
    retriever = get_state_path_retriever()

    # Reconstruct visited by re-localizing earlier steps (same as full_system)
    visited: List[str] = []
    if step_index > 0:
        for j in range(step_index):
            prev_b64 = _load_screenshot_b64(scenario, j)
            if not prev_b64:
                continue
            vs = pipeline.recognize_visual_state(prev_b64)
            loc = pipeline.localize_to_graph(
                vs, None, screenshot_b64=prev_b64,
                manual_ids=[scenario["manual_id"]],
                user_goal=scenario.get("goal", ""),
                visited_node_ids=list(visited),
            )
            n = loc.get("node")
            if n and n["id"] not in visited:
                visited.append(n["id"])

    # Anchor localization for THIS step
    visual_state = pipeline.recognize_visual_state(screenshot_b64) if screenshot_b64 else {}
    loc = pipeline.localize_to_graph(
        visual_state, None,
        screenshot_b64=screenshot_b64,
        manual_ids=[scenario["manual_id"]],
        user_goal=scenario.get("goal", ""),
        visited_node_ids=visited,
    )
    anchor_node = loc.get("node")
    anchor_id = anchor_node.get("id") if anchor_node else None
    conf = float(loc.get("confidence") or 0.0)

    # Expand sub-path
    path = retriever.retrieve(
        anchor_node_id=anchor_id,
        manual_id=scenario["manual_id"],
        visited_node_ids=visited,
        confidence=conf,
    )
    context_block = format_step_path(path)

    messages = _build_messages(scenario, step_index, prior_responses, context_block=context_block)
    return _call_generator(messages)


# ─────────────────────────────────────────────────────────────────────
# Registry — used by bench_runner.py
# ─────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────
# Backend 0: no_rag — LLM zero-shot baseline (no manual context at all)
# Establishes the "RAG-off" floor. If hallucination is dramatically
# higher here than in vanilla_vector, we've shown the manual grounding
# is doing real work; without this baseline the paper cannot argue for
# the framework's existence.
# ─────────────────────────────────────────────────────────────────────

def backend_no_rag(step_index: int, scenario: Dict,
                   prior_responses: List[str]) -> str:
    # No RAG lookup, no manual chunks, no workflow node localization.
    # The model sees only the goal, the completed-steps memory, and the
    # current screenshot — the same signal a naive user of the raw LLM
    # would supply. This is the "if you just asked GPT / Claude / Gemini"
    # baseline.
    messages = _build_messages(scenario, step_index, prior_responses, context_block="")
    return _call_generator(messages)


# ─────────────────────────────────────────────────────────────────────
# Backend: long_context — full manual injected as context (no retrieval)
# The "spend money to skip RAG" upper bound. Establishes the
# accuracy-vs-cost trade-off ceiling: if long_context ties or beats
# full_system, our contribution shifts from "accuracy" to "you get the
# same accuracy at ~1/N the cost".
# ─────────────────────────────────────────────────────────────────────

_LONG_CONTEXT_CACHE: Dict[str, str] = {}


def _get_full_manual_text(manual_id: str) -> str:
    """Reconstruct the entire manual text from its stored chunks, sorted
    by page then chunk_index for coherent reading order. Cached per
    manual_id so we don't hit ChromaDB on every step."""
    if manual_id in _LONG_CONTEXT_CACHE:
        return _LONG_CONTEXT_CACHE[manual_id]
    import chromadb
    chromadb_path = os.environ.get("CHROMADB_PATH", "./data/chromadb")
    client = chromadb.PersistentClient(path=chromadb_path)
    col = client.get_collection(f"manual_{manual_id}")
    data = col.get(include=["documents", "metadatas"])
    pairs = sorted(
        zip(data["documents"], data["metadatas"]),
        key=lambda x: (
            (x[1] or {}).get("page", 0),
            (x[1] or {}).get("chunk_index", 0),
        ),
    )
    full = "\n\n".join(d for d, _ in pairs)
    _LONG_CONTEXT_CACHE[manual_id] = full
    return full


def backend_long_context(step_index: int, scenario: Dict,
                         prior_responses: List[str]) -> str:
    """Inject the entire manual as context. No retrieval, no workflow
    routing, no vision analysis. This is the "just paste the whole PDF"
    baseline — costly in input tokens, but requires zero retrieval
    infrastructure. Only viable on models with large enough context
    windows (Gemini 2.5 Pro at 2M tokens; manual is ~191k tokens)."""
    manual_id = scenario.get("manual_id")
    manual_text = _get_full_manual_text(manual_id) if manual_id else ""
    context_block = (
        f"[Full Manual Text — inserted verbatim, no retrieval]\n"
        f"{manual_text}"
        if manual_text else ""
    )
    messages = _build_messages(scenario, step_index, prior_responses,
                               context_block=context_block)
    return _call_generator(messages)


BACKEND_REGISTRY: Dict[str, Callable[[int, Dict, List[str]], str]] = {
    "no_rag":         backend_no_rag,
    "vanilla_vector": backend_vanilla_vector,
    "graph_only":     backend_graph_only,
    "vision_only":    backend_vision_only,
    "full_system":    backend_full_system,
    "state_path":     backend_state_path,
    "long_context":   backend_long_context,
}
