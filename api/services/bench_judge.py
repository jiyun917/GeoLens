"""
LLM-as-judge — a more lenient step-accuracy metric for the benchmark.

The default `step_match` in evaluation.py uses regex/keyword matching. That
penalizes correct paraphrases ("click Save" vs "press Save button" vs
"Save 누르기"). For paper-quality numbers we also report a semantic-judge
variant: a small Claude/Gemini call rates 0/1 whether the response performs
the action expected by the step.

This is OPTIONAL (controlled by --judge flag on bench_runner) because it
roughly doubles the API call count of a benchmark run.

Two judges are supported and the higher score is taken (consensus rule
attenuates one-judge bias):
  - Claude judge   (claude-haiku, cheap)
  - Gemini judge   (gemini-2.5-flash)

Each judge gets a STRICT rubric so its 0/1 verdicts are reproducible.
"""

import json
import os
import re
from typing import Dict, Optional


# ────────────────────────────────────────────────────────────────────
# Prompt
# ────────────────────────────────────────────────────────────────────

JUDGE_PROMPT = """You are a strict semantic equivalence judge for UI guidance.

Decide whether the MODEL_RESPONSE correctly performs the action that the
STEP expects. The action target may be named differently (paraphrased or
translated) as long as it is the SAME UI element on the SAME screen.

Score 1 if and ONLY if all are true:
  - the action verb is equivalent (click ≈ tap ≈ press; choose ≈ select;
    type ≈ enter ≈ input; etc.)
  - the target element refers to the SAME button/menu/field
  - if the step has a `trap` field, the model_response must NOT pick the
    trap option (e.g. "Skip" when the expected action is "Run").

Otherwise score 0.

STEP expected_action_keywords: {keywords}
STEP expected_action_pattern:  {pattern}
STEP allowed_alternatives:     {alternatives}
STEP trap (if any):            {trap}
STEP description (context):    {description}

MODEL_RESPONSE:
{response}

Respond with JSON only: {{"score": 0 or 1, "reason": "<one short sentence>"}}"""


def _build_prompt(step: Dict, response: str) -> str:
    kws = step.get("expected_action_keywords") or []
    pat = step.get("expected_action_text_pattern") or "(none)"
    alts = step.get("allowed_alternatives") or []
    alt_str = "; ".join(a.get("pattern", "") for a in alts) or "(none)"
    trap = step.get("trap")
    trap_str = json.dumps(trap, ensure_ascii=False) if trap else "(none)"
    desc = (step.get("_node_hint") or {}).get("description") or ""
    return JUDGE_PROMPT.format(
        keywords=", ".join(kws) or "(none)",
        pattern=pat,
        alternatives=alt_str,
        trap=trap_str,
        description=desc[:200],
        response=(response or "")[:500],
    )


def _parse_score(raw: str) -> Optional[int]:
    if not raw:
        return None
    try:
        d = json.loads(raw)
        s = int(d.get("score", -1))
        if s in (0, 1):
            return s
    except Exception:
        pass
    # Tolerate non-JSON: look for a 0/1 number in the text
    m = re.search(r'"?score"?\s*[:=]\s*([01])', raw)
    if m:
        return int(m.group(1))
    return None


# ────────────────────────────────────────────────────────────────────
# Judges
# ────────────────────────────────────────────────────────────────────

def _judge_claude(prompt: str) -> Optional[int]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=128,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        return _parse_score(text.strip())
    except Exception as e:
        print(f"[JUDGE] claude failed: {e}")
        return None


def _judge_gemini(prompt: str) -> Optional[int]:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=20_000))
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0,
            ),
        )
        return _parse_score((resp.text or "").strip())
    except Exception as e:
        print(f"[JUDGE] gemini failed: {e}")
        return None


# ────────────────────────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────────────────────────

def llm_judge_step(step: Dict, response: str, mode: str = "consensus") -> Optional[int]:
    """Return 0/1 verdict or None if both judges failed.

    mode:
      - "claude"     : Claude judge only
      - "gemini"     : Gemini judge only
      - "consensus"  : run both, take max (more lenient — favors 1 if either says 1)
      - "strict"     : run both, take min (more strict — only 1 if both agree)
    """
    prompt = _build_prompt(step, response)
    if mode == "claude":
        return _judge_claude(prompt)
    if mode == "gemini":
        return _judge_gemini(prompt)

    s1 = _judge_claude(prompt)
    s2 = _judge_gemini(prompt)
    if s1 is None and s2 is None:
        return None
    if s1 is None:
        return s2
    if s2 is None:
        return s1
    return max(s1, s2) if mode == "consensus" else min(s1, s2)


def annotate_with_judge(per_step_records: list, scenario_steps: list,
                        mode: str = "consensus") -> Dict:
    """Run the LLM judge over every per-step record from ScenarioEvaluator
    and return (per_step + judge_score) plus an aggregate judge_step_accuracy."""
    n = len(per_step_records)
    matched_by_judge = 0
    judged = 0
    for rec, step in zip(per_step_records, scenario_steps):
        if not rec.get("response"):
            rec["judge_score"] = None
            continue
        s = llm_judge_step(step, rec["response"], mode=mode)
        rec["judge_score"] = s
        if s is not None:
            judged += 1
            matched_by_judge += s
    return {
        "judge_mode": mode,
        "judge_step_accuracy": (matched_by_judge / judged) if judged else None,
        "judged_steps": judged,
        "total_steps": n,
    }
