"""
AutoProcRAG evaluation framework.

Three independent evaluators:

  GraphQualityEvaluator  — node/edge precision·recall + order + linked_chunks
                           overlap between hand-authored and auto-generated
                           workflow JSONs for the same manual.

  GuideAccuracyEvaluator — runs a test-question set through three guide
                           back-ends (baseline_vector, manual_graph, auto_graph)
                           and scores next_step accuracy and keyword coverage.

  VisualMatchEvaluator   — runs test screenshots through keyword matching,
                           CLIP matching, and a hybrid blend; scores top-1
                           node-localization accuracy.

None of the evaluators touch production singletons directly — each one loads
a filtered WorkflowGraph pointed at the subset of JSONs under evaluation.
Missing deps (CLIP, Gemini) degrade gracefully: affected rows score 0.0 rather
than raising.
"""

import glob
import json
import os
import re
import shutil
import tempfile
from typing import Dict, List, Optional, Tuple

from .workflow_graph import WORKFLOW_DIR, WorkflowGraph

EVAL_DIR = os.environ.get(
    "EVAL_DATA_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "eval"),
)

DEFAULT_TEST_QUESTIONS = os.path.join(EVAL_DIR, "test_questions.json")
DEFAULT_SCREENSHOT_DIR = os.path.join(EVAL_DIR, "test_screenshots")
DEFAULT_SCREENSHOT_MANIFEST = os.path.join(EVAL_DIR, "test_screenshots.json")


# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════

def _tokens(text: str) -> List[str]:
    return [t for t in re.findall(r"\w+", (text or "").lower()) if len(t) > 1]


def _jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _load_workflow_json(path: str) -> Optional[Dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[EVAL] failed to read {path}: {e}")
        return None


def _temp_workflow_dir(paths: List[str]) -> str:
    """Copy a subset of workflow JSONs into a fresh temp dir and return its path."""
    tmp = tempfile.mkdtemp(prefix="eval_workflows_")
    for p in paths:
        if os.path.exists(p):
            shutil.copy2(p, tmp)
    return tmp


def _manual_workflow_paths() -> List[str]:
    """Hand-authored workflow JSONs (anything that isn't auto_*)."""
    return [p for p in glob.glob(os.path.join(WORKFLOW_DIR, "*.json"))
            if not os.path.basename(p).startswith("auto_")]


def _auto_workflow_paths(manual_id: Optional[str] = None) -> List[str]:
    prefix = f"auto_{manual_id}__" if manual_id else "auto_"
    return [p for p in glob.glob(os.path.join(WORKFLOW_DIR, "*.json"))
            if os.path.basename(p).startswith(prefix)]


def _match_nodes(auto_nodes: List[Dict], manual_nodes: List[Dict], threshold: float = 0.25) -> List[Tuple[int, int, float]]:
    """Greedy best-match between auto and manual nodes using title+description token Jaccard.

    Returns a list of (auto_idx, manual_idx, similarity) pairs. Each manual
    node is matched to at most one auto node and vice versa.
    """
    scores: List[Tuple[int, int, float]] = []
    for i, an in enumerate(auto_nodes):
        a_tokens = _tokens(f"{an.get('title','')} {an.get('description','')}")
        for j, mn in enumerate(manual_nodes):
            m_tokens = _tokens(f"{mn.get('title','')} {mn.get('description','')}")
            s = _jaccard(a_tokens, m_tokens)
            if s >= threshold:
                scores.append((i, j, s))
    scores.sort(key=lambda t: t[2], reverse=True)

    used_a: set = set()
    used_m: set = set()
    pairs = []
    for i, j, s in scores:
        if i in used_a or j in used_m:
            continue
        pairs.append((i, j, s))
        used_a.add(i)
        used_m.add(j)
    return pairs


# ═══════════════════════════════════════════════════════════
# 1) Graph quality
# ═══════════════════════════════════════════════════════════

class GraphQualityEvaluator:
    """Compare an auto-generated workflow JSON against a hand-authored one."""

    def evaluate(self, auto_graph: Dict, manual_graph: Dict) -> Dict:
        auto_nodes = auto_graph.get("nodes", []) or []
        manual_nodes = manual_graph.get("nodes", []) or []
        auto_edges = auto_graph.get("edges", []) or []
        manual_edges = manual_graph.get("edges", []) or []

        pairs = _match_nodes(auto_nodes, manual_nodes)
        matched_auto = len({i for i, _, _ in pairs})
        matched_manual = len({j for _, j, _ in pairs})

        node_precision = matched_auto / len(auto_nodes) if auto_nodes else 0.0
        node_recall = matched_manual / len(manual_nodes) if manual_nodes else 0.0

        # Build id → matched_peer_id maps
        a2m_id = {auto_nodes[i]["id"]: manual_nodes[j]["id"] for i, j, _ in pairs}
        m2a_id = {v: k for k, v in a2m_id.items()}

        # Edge comparison: an auto edge "matches" if both endpoints have peers
        # AND the manual graph has an edge between those peers.
        manual_edge_set = {(e.get("source"), e.get("target")) for e in manual_edges}
        auto_edge_set = {(e.get("source"), e.get("target")) for e in auto_edges}

        auto_edge_hits = 0
        for e in auto_edges:
            ms = a2m_id.get(e.get("source"))
            mt = a2m_id.get(e.get("target"))
            if ms and mt and (ms, mt) in manual_edge_set:
                auto_edge_hits += 1

        manual_edge_hits = 0
        for e in manual_edges:
            as_ = m2a_id.get(e.get("source"))
            at_ = m2a_id.get(e.get("target"))
            if as_ and at_ and (as_, at_) in auto_edge_set:
                manual_edge_hits += 1

        edge_precision = auto_edge_hits / len(auto_edges) if auto_edges else 0.0
        edge_recall = manual_edge_hits / len(manual_edges) if manual_edges else 0.0

        # Order accuracy: for every matched pair (p, q) of nodes, check if
        # their relative ordering agrees between the two graphs.
        order_total = 0
        order_agree = 0
        for a_i, m_i, _ in pairs:
            for a_j, m_j, _ in pairs:
                if a_i == a_j:
                    continue
                step_a_i = auto_nodes[a_i].get("step_number", 0)
                step_a_j = auto_nodes[a_j].get("step_number", 0)
                step_m_i = manual_nodes[m_i].get("step_number", 0)
                step_m_j = manual_nodes[m_j].get("step_number", 0)
                # Only compare within the same workflow pair (step numbers are local)
                if auto_nodes[a_i].get("workflow_id") != auto_nodes[a_j].get("workflow_id"):
                    continue
                if manual_nodes[m_i].get("workflow_id") != manual_nodes[m_j].get("workflow_id"):
                    continue
                order_total += 1
                if (step_a_i < step_a_j) == (step_m_i < step_m_j):
                    order_agree += 1
        order_accuracy = order_agree / order_total if order_total else 0.0

        # linked_chunks overlap
        jaccards = []
        for a_i, m_i, _ in pairs:
            al = auto_nodes[a_i].get("linked_chunks") or []
            ml = manual_nodes[m_i].get("linked_chunks") or []
            if not al and not ml:
                continue
            jaccards.append(_jaccard(al, ml))
        linked_chunks_overlap = (sum(jaccards) / len(jaccards)) if jaccards else 0.0

        return {
            "node_precision": round(node_precision, 3),
            "node_recall": round(node_recall, 3),
            "edge_precision": round(edge_precision, 3),
            "edge_recall": round(edge_recall, 3),
            "order_accuracy": round(order_accuracy, 3),
            "linked_chunks_overlap": round(linked_chunks_overlap, 3),
            "matched_pairs": len(pairs),
            "auto_nodes": len(auto_nodes),
            "manual_nodes": len(manual_nodes),
        }


# ═══════════════════════════════════════════════════════════
# 2) Guide accuracy
# ═══════════════════════════════════════════════════════════

class GuideAccuracyEvaluator:
    """Run a test-question set through three back-ends and score accuracy."""

    def __init__(self, manual_ids: List[str]):
        self.manual_ids = manual_ids

    def evaluate_all(self, test_questions: List[Dict]) -> Dict:
        if not test_questions:
            return {"count": 0, "results": {}}

        results = {
            "baseline_vector": {"next_step_acc": 0.0, "keyword_hit": 0.0, "count": 0},
            "manual_graph":    {"next_step_acc": 0.0, "keyword_hit": 0.0, "count": 0},
            "auto_graph":      {"next_step_acc": 0.0, "keyword_hit": 0.0, "count": 0},
        }

        # Build filtered graph contexts once (reused across questions)
        manual_tmp = _temp_workflow_dir(_manual_workflow_paths())
        auto_paths = []
        for mid in self.manual_ids:
            auto_paths.extend(_auto_workflow_paths(mid))
        auto_tmp = _temp_workflow_dir(auto_paths)

        try:
            manual_wg = WorkflowGraph(manual_tmp)
            auto_wg = WorkflowGraph(auto_tmp)

            for q in test_questions:
                self._score_baseline(q, results["baseline_vector"])
                self._score_graph(q, manual_wg, results["manual_graph"])
                self._score_graph(q, auto_wg, results["auto_graph"])
        finally:
            shutil.rmtree(manual_tmp, ignore_errors=True)
            shutil.rmtree(auto_tmp, ignore_errors=True)

        # finalize averages
        for key, row in results.items():
            n = row["count"] or 1
            row["next_step_acc"] = round(row["next_step_acc"] / n, 3)
            row["keyword_hit"] = round(row["keyword_hit"] / n, 3)

        return {"count": len(test_questions), "results": results}

    # ─────────────────────────────────────────────────────

    def _score_baseline(self, q: Dict, row: Dict):
        try:
            from .rag import get_manual_context
            context = get_manual_context(self.manual_ids, q.get("question", ""), top_k=5) or ""
        except Exception as e:
            print(f"[EVAL] baseline failed: {e}")
            context = ""
        row["count"] += 1
        row["keyword_hit"] += _keyword_hit(context, q.get("expected_answer_keywords", []))
        # baseline has no structured next-step concept — skip

    def _score_graph(self, q: Dict, wg: WorkflowGraph, row: Dict):
        row["count"] += 1
        expected_next = q.get("expected_next_node")
        current_step = (q.get("context") or {}).get("current_step")

        predicted_next = None
        if current_step:
            nexts = wg.get_next_steps(current_step)
            if nexts:
                predicted_next = nexts[0].get("id")

        if expected_next and predicted_next:
            row["next_step_acc"] += 1.0 if predicted_next == expected_next else 0.0

        # Keyword coverage: collect linked_chunks' descriptions + next node description
        text_bag = []
        if current_step:
            cn = wg.get_node(current_step)
            if cn:
                text_bag.append(cn.get("description", ""))
                text_bag.append(" ".join(cn.get("linked_chunks", []) or []))
        for n in wg.get_next_steps(current_step) if current_step else []:
            text_bag.append(n.get("description", ""))
            text_bag.append(n.get("title", ""))
        row["keyword_hit"] += _keyword_hit(" ".join(text_bag), q.get("expected_answer_keywords", []))


def _keyword_hit(text: str, keywords: List[str]) -> float:
    if not keywords:
        return 0.0
    low = (text or "").lower()
    hits = sum(1 for kw in keywords if (kw or "").lower() in low)
    return hits / len(keywords)


# ═══════════════════════════════════════════════════════════
# 3) Visual match
# ═══════════════════════════════════════════════════════════

class VisualMatchEvaluator:
    """Compare keyword / CLIP / hybrid approaches for screenshot → node localization."""

    def __init__(self, manual_id: Optional[str] = None, alpha: float = 0.5):
        self.manual_id = manual_id
        self.alpha = alpha

    def evaluate(self, test_screenshots: List[Dict]) -> Dict:
        from .workflow_graph import get_workflow_graph
        wg = get_workflow_graph()

        counts = {"keyword_only": 0, "clip_only": 0, "hybrid": 0}
        hits = {"keyword_only": 0, "clip_only": 0, "hybrid": 0}

        matcher = None
        try:
            from .visual_matcher import get_visual_matcher
            matcher = get_visual_matcher()
        except Exception as e:
            print(f"[EVAL] visual matcher unavailable: {e}")

        for item in test_screenshots:
            screenshot_b64 = item.get("screenshot_b64") or _load_b64(item.get("screenshot_path"))
            expected = item.get("expected_node")
            if not screenshot_b64 or not expected:
                continue

            # keyword-only path
            visual_state = item.get("visual_state") or {
                "current_dialog": item.get("description", ""),
                "visible_elements": item.get("visible_elements", []) or [],
            }
            k_node, k_score = wg.get_current_node(visual_state)
            counts["keyword_only"] += 1
            if k_node and k_node.get("id") == expected:
                hits["keyword_only"] += 1

            # clip-only path
            c_node, c_score = None, 0.0
            if matcher and matcher.available() and self.manual_id:
                try:
                    c_node, c_score = matcher.match_to_workflow_node(screenshot_b64, self.manual_id, wg)
                except Exception as e:
                    print(f"[EVAL] clip match failed: {e}")
            counts["clip_only"] += 1
            if c_node and c_node.get("id") == expected:
                hits["clip_only"] += 1

            # hybrid: pick higher, blended score
            k_blend = self.alpha * (k_score or 0.0)
            c_blend = (1 - self.alpha) * (c_score or 0.0)
            hybrid_node = k_node if k_blend >= c_blend else c_node
            counts["hybrid"] += 1
            if hybrid_node and hybrid_node.get("id") == expected:
                hits["hybrid"] += 1

        def _acc(name):
            return round(hits[name] / counts[name], 3) if counts[name] else 0.0

        return {
            "count": len(test_screenshots),
            "keyword_only_acc": _acc("keyword_only"),
            "clip_only_acc": _acc("clip_only"),
            "hybrid_acc": _acc("hybrid"),
            "hits": hits,
            "counts": counts,
        }


def _load_b64(path: Optional[str]) -> Optional[str]:
    if not path or not os.path.exists(path):
        return None
    import base64
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


# ═══════════════════════════════════════════════════════════
# Convenience loaders
# ═══════════════════════════════════════════════════════════

def load_test_questions(path: Optional[str] = None) -> List[Dict]:
    path = path or DEFAULT_TEST_QUESTIONS
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[EVAL] failed to load {path}: {e}")
        return []


def load_test_screenshots(manifest: Optional[str] = None) -> List[Dict]:
    manifest = manifest or DEFAULT_SCREENSHOT_MANIFEST
    if not os.path.exists(manifest):
        return []
    try:
        with open(manifest, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[EVAL] failed to load {manifest}: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════
# Scenario-level benchmark — multi-step procedural evaluation
#
# Designed for the paper's benchmark. A "scenario" is a list of expected
# screen states with ground-truth actions. We run the scenario through
# four backends (vanilla_vector / graph_only / vision_only / full_system)
# and compute paper-grade metrics:
#
#   step_accuracy       — fraction of steps where AI response matches GT
#   hallucination_rate  — fraction of steps where AI references a UI element
#                          NOT in visual_state_gt.visible_elements
#   dwell_loop_rate     — fraction of steps where response equals previous
#                          response (after normalization)
#   recovery_rate       — among is_error_recovery_test steps, fraction
#                          where AI gave the expected corrective action
#   goal_completion_rate— 1.0 if final response ends with Done/완료 sentinel
#                          on the completion screenshot, else 0.0
#   trap_pass_rate      — fraction of trap steps the AI handled correctly
#                          (e.g. didn't pick Skip when Run was the right call)
# ═══════════════════════════════════════════════════════════════════

# Standard backend names — used as keys in result dicts.
# state_path is the novel contribution (Procedural State-Path Retrieval).
BACKENDS = ("no_rag", "vanilla_vector", "graph_only", "vision_only", "full_system", "state_path")


def _normalize_instruction(text: str) -> str:
    """Strip whitespace/punctuation/brackets for loop-detection comparison."""
    return re.sub(r"[\s\W_]+", "", (text or "").lower())


_DONE_SENTINEL_RE = re.compile(r"(?i)^\s*(완료|done)\.?\s*$")


def _visual_state_indicates_goal_reached(step_gt: Dict) -> bool:
    """Heuristic: the visual_state_gt / data_state / current_action fields
    of THIS step indicate that the workflow goal has already been achieved,
    so a bare 'Done'/'완료' response is a legitimate answer rather than a
    premature declaration. Signals: keywords like 'achieved', '완료',
    '전체 표시', 'goal reached', 'all three slices'; or a completion trap
    of type 'goal_completion_sentinel'; or capture_instructions.screen_state
    explicitly describing the goal-achieved terminal state.

    Applied only when the response is a bare completion sentinel — this
    filter prevents the sentinel from silently satisfying steps whose
    screen still shows an intermediate state."""
    trap = step_gt.get("trap") or {}
    if trap.get("type") == "goal_completion_sentinel":
        return True

    haystack_parts: List[str] = []
    vs = step_gt.get("visual_state_gt") or {}
    for k in ("current_dialog", "active_menu", "data_state", "current_action"):
        v = vs.get(k)
        if isinstance(v, str):
            haystack_parts.append(v)
    for v in (vs.get("visible_elements") or []):
        if isinstance(v, str):
            haystack_parts.append(v)
    ci = step_gt.get("capture_instructions") or {}
    for k in ("screen_state",):
        v = ci.get(k)
        if isinstance(v, str):
            haystack_parts.append(v)

    hay = " ".join(haystack_parts).lower()
    goal_markers = [
        "goal achieved", "goal reached", "goal complete", "goal-achieved",
        "achieved", "all three slices", "all slices",
        "완료", "달성", "goal state", "completed", "terminal state",
    ]
    return any(m in hay for m in goal_markers)


def step_match(response: str, step_gt: Dict) -> bool:
    """True if `response` satisfies the step's expected_action_text_pattern,
    expected_action_keywords, OR any allowed_alternatives pattern.

    Special rule for the bare '완료'/'Done' completion sentinel: it counts
    as a match ONLY when the step's visual_state indicates the workflow
    goal has actually been achieved. Otherwise the model is declaring
    completion prematurely and the response is a MISS, even if some
    allowed_alternatives pattern would have matched '완료' by regex. This
    stops zero-shot baselines from silently satisfying intermediate steps
    with an over-eager 'Done'."""
    if not response:
        return False
    text = response.strip()

    is_bare_sentinel = bool(_DONE_SENTINEL_RE.match(text))
    if is_bare_sentinel and not _visual_state_indicates_goal_reached(step_gt):
        return False

    pat = step_gt.get("expected_action_text_pattern")
    if pat:
        try:
            if re.search(pat, text):
                return True
        except re.error:
            pass

    kws = step_gt.get("expected_action_keywords") or []
    if kws:
        low = text.lower()
        if all(k.lower() in low for k in kws):
            return True

    for alt in step_gt.get("allowed_alternatives", []) or []:
        ap = alt.get("pattern")
        if ap:
            try:
                if re.search(ap, text):
                    return True
            except re.error:
                continue
    return False


def hallucinated_elements(response: str, visible_elements_gt: List[str]) -> List[str]:
    """Return list of UI-element-like tokens in `response` that are NOT in the
    ground-truth visible_elements list. Heuristic: looks at quoted strings
    'X' / "X" / 'X 버튼' since those are how the AI references UI items."""
    visible_lc = [e.lower() for e in (visible_elements_gt or [])]
    referenced = set()
    # quoted tokens: 'X', "X", `X`, X 버튼, X 메뉴, X 탭, X button
    for m in re.findall(r"['\"`]([^'\"`\n]{1,40})['\"`]", response or ""):
        referenced.add(m.strip())
    for m in re.findall(r"\b([A-Z][\w \-/]{1,30}?)\s*(?:버튼|메뉴|탭|button|menu|tab)\b",
                       response or ""):
        referenced.add(m.strip())
    halls = []
    for r in referenced:
        if not r or len(r) < 2:
            continue
        rlc = r.lower()
        # Lenient: skip if any visible element substring-contains it
        if any(rlc in v or v in rlc for v in visible_lc):
            continue
        halls.append(r)
    return halls


def has_done_sentinel(response: str) -> bool:
    if not response:
        return False
    t = response.strip()
    last_line = t.split("\n")[-1].strip()
    bare = re.sub(r"[\s.\W_]+", "", last_line.lower())
    if bare in ("done", "완료"):
        return True
    return bool(re.search(r"(?:^|\s)(done|완료)\.?\s*$", t, re.IGNORECASE))


# UI element categories that scenarios test the model's ability to observe
# on screen. If a completion declaration NAMES one of these but the actual
# final visual_state does not confirm its presence, the declaration is
# hallucinated — the model claimed to see something that wasn't there.
_COMPLETION_CLAIM_PATTERNS = [
    r"(In[- ]?line|Inline|Cross[- ]?line|Crossline|Z[- ]?slice|Time[- ]?slice|Depth[- ]?slice)",
    r"(3D Scene|Main Window|Tree scene)",
    r"(Seismic_data|F3[_ ]?Demo|Similarity|Curvature|Frequency)",
]


def _canon(token: str) -> str:
    """Canonicalize a UI element mention: lowercase, strip spaces/hyphens/underscores."""
    return re.sub(r"[\s\-_]+", "", (token or "").lower())


def completion_visually_grounded(
    response: str, final_step_gt: Dict
) -> Tuple[bool, List[str]]:
    """Verify that a completion declaration only names UI elements the final
    step's visual_state actually confirms as present.

    Returns (grounded: bool, hallucinated_terms: list[str]).

    A bare sentinel ("완료" / "Done") is always grounded — nothing to verify.
    An elaborated response ("In-line, Cross-line, Z-slice 모두 표시되어 있음
    → 완료") is grounded ONLY if each named category appears in the final
    visual_state's data_state / visible_elements / current_action / dialog /
    capture_instructions.screen_state.

    This closes a scoring gap: without it, no_rag zero-shot models pass
    goal_completion by habitually listing the workflow's target elements
    at the end regardless of whether the screen actually shows them. That
    turns goal_completion into a measure of utterance habit, not screen
    observation.
    """
    if not response:
        return True, []

    claims: List[str] = []
    for pat in _COMPLETION_CLAIM_PATTERNS:
        for m in re.findall(pat, response, flags=re.IGNORECASE):
            token = m if isinstance(m, str) else m[0]
            claims.append(token)
    if not claims:
        return True, []

    vs = (final_step_gt or {}).get("visual_state_gt") or {}
    ci = (final_step_gt or {}).get("capture_instructions") or {}
    haystack_parts: List[str] = []
    for k in ("current_dialog", "active_menu", "data_state", "current_action"):
        v = vs.get(k)
        if isinstance(v, str):
            haystack_parts.append(v)
    for v in (vs.get("visible_elements") or []):
        if isinstance(v, str):
            haystack_parts.append(v)
    for k in ("screen_state", "user_should_have_just"):
        v = ci.get(k)
        if isinstance(v, str):
            haystack_parts.append(v)
    haystack = _canon(" ".join(haystack_parts))

    hallucinated: List[str] = []
    seen_canon = set()
    for raw in claims:
        c = _canon(raw)
        if not c or c in seen_canon:
            continue
        seen_canon.add(c)
        if c not in haystack:
            hallucinated.append(raw)
    return (len(hallucinated) == 0), hallucinated


class ScenarioEvaluator:
    """Runs a labeled scenario through a chosen backend and computes
    per-step + per-scenario metrics. Each backend is a callable:

        backend(scenario_step_index, scenario, prior_responses) -> str

    The backend receives the full scenario + index so it can build the
    appropriate query/context. The framework feeds it screenshots from
    `screenshot_path` (loaded from disk) one at a time.
    """

    def __init__(self, scenario: Dict):
        self.scenario = scenario
        self.steps: List[Dict] = scenario.get("steps", []) or []

    def evaluate_backend(self, backend_name: str, backend_callable) -> Dict:
        import time as _time
        try:
            from api.services.bench_backends import get_last_usage  # type: ignore
        except ImportError:
            get_last_usage = lambda: {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "model": ""}
        try:
            from api.services.guide_pipeline import (
                get_last_localize_meta, reset_last_localize_meta,
            )
        except ImportError:
            get_last_localize_meta = lambda: {}
            reset_last_localize_meta = lambda: None

        per_step: List[Dict] = []
        prior_responses: List[str] = []
        step_latencies: List[float] = []
        step_costs: List[float] = []
        step_input_toks: List[int] = []
        step_output_toks: List[int] = []
        for i, step in enumerate(self.steps):
            reset_last_localize_meta()
            t0 = _time.time()
            try:
                response = backend_callable(i, self.scenario, prior_responses) or ""
            except Exception as e:
                print(f"[EVAL] backend {backend_name} step {i} failed: {e}")
                response = ""
            latency = round(_time.time() - t0, 3)
            usage = get_last_usage()
            loc_meta = get_last_localize_meta()

            matched = step_match(response, step)
            halls = hallucinated_elements(
                response, (step.get("visual_state_gt") or {}).get("visible_elements", [])
            )
            looped = bool(
                prior_responses and
                _normalize_instruction(response) == _normalize_instruction(prior_responses[-1])
            )
            per_step.append({
                "step_index": i,
                "response": response,
                "matched": matched,
                "hallucinated": halls,
                "looped": looped,
                "is_trap": bool(step.get("trap")),
                "is_recovery": bool(step.get("is_error_recovery_test")),
                "latency_sec":   latency,
                "input_tokens":  usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cost_usd":      usage.get("cost_usd", 0.0),
                "model":         usage.get("model", ""),
                # Routing telemetry (only meaningful for backends that call
                # guide_pipeline.process_guide_request or localize_to_graph;
                # zeros for vanilla_vector, no_rag, vision_only, graph_only).
                "route_confidence":   loc_meta.get("confidence", 0.0),
                "picked_node_id":     loc_meta.get("picked_node_id"),
                "picked_workflow_id": loc_meta.get("picked_workflow_id"),
                "route_method":       loc_meta.get("match_method", ""),
                "fallback_activated": bool(loc_meta.get("fallback_activated", False)),
            })
            step_latencies.append(latency)
            step_costs.append(float(usage.get("cost_usd") or 0.0))
            step_input_toks.append(int(usage.get("input_tokens") or 0))
            step_output_toks.append(int(usage.get("output_tokens") or 0))
            prior_responses.append(response)

        # Completion check
        completion = self.scenario.get("completion") or {}
        done_ok = False
        completion_response = ""
        completion_hallucinations: List[str] = []
        completion_grounded: Optional[bool] = None
        if completion.get("expected_done_sentinel"):
            try:
                final_path = completion.get("final_screenshot_path")
                if final_path:
                    completion_response = backend_callable(
                        len(self.steps), self.scenario, prior_responses
                    ) or ""
                    sentinel_ok = has_done_sentinel(completion_response)
                    # Visual-state cross-check has TWO gates:
                    #   (a) the response's named UI elements must be present
                    #       in the final visual_state (no phantom element
                    #       claims — the r2/r4/r5 hallucination pattern)
                    #   (b) the final visual_state must ACTIVELY indicate
                    #       goal-reached (blocks bare-sentinel responses
                    #       that assert "완료" without any screen evidence
                    #       — the r1 pattern)
                    final_step_gt = self.steps[-1] if self.steps else {}
                    completion_grounded, completion_hallucinations = (
                        completion_visually_grounded(
                            completion_response, final_step_gt
                        )
                    )
                    visual_confirms_goal = _visual_state_indicates_goal_reached(final_step_gt)
                    done_ok = sentinel_ok and completion_grounded and visual_confirms_goal
                    if sentinel_ok and not (completion_grounded and visual_confirms_goal):
                        reasons = []
                        if not completion_grounded:
                            reasons.append(f"ungrounded claims={completion_hallucinations}")
                        if not visual_confirms_goal:
                            reasons.append("final visual_state does not indicate goal-reached")
                        print(
                            f"[EVAL] {backend_name} completion sentinel present but "
                            f"rejected — " + "; ".join(reasons)
                        )
            except Exception as e:
                print(f"[EVAL] backend {backend_name} completion check failed: {e}")

        n = max(1, len(per_step))
        trap_steps = [s for s in per_step if s["is_trap"]]
        recovery_steps = [s for s in per_step if s["is_recovery"]]
        hall_rate = sum(1 for s in per_step if s["hallucinated"]) / n
        mean_lat = round(sum(step_latencies) / n, 3) if step_latencies else 0.0
        total_cost = round(sum(step_costs), 6)
        mean_cost = round(total_cost / n, 6) if n else 0.0
        # Route confidence + fallback aggregate. Only meaningful for backends
        # that touch guide_pipeline (full_system, state_path). For others the
        # confidence field stays at zero and fallback_rate reads 0 — that's
        # honest, not fake activation.
        route_steps = [s for s in per_step if s.get("route_method")]
        fallback_rate = (sum(1 for s in per_step if s.get("fallback_activated")) / n) if n else 0.0
        mean_route_conf = (
            round(sum(s.get("route_confidence", 0.0) for s in route_steps) / len(route_steps), 3)
            if route_steps else None
        )
        return {
            "backend": backend_name,
            "n_steps": len(per_step),
            "step_accuracy":        sum(1 for s in per_step if s["matched"]) / n,
            "hallucination_rate":   hall_rate,
            "faithfulness":         round(1.0 - hall_rate, 4),  # higher = better
            "dwell_loop_rate":      sum(1 for s in per_step if s["looped"]) / n,
            "loop_rate":            sum(1 for s in per_step if s["looped"]) / n,  # alias for paper
            "trap_pass_rate":       (sum(1 for s in trap_steps if s["matched"]) / len(trap_steps)) if trap_steps else None,
            "recovery_rate":        (sum(1 for s in recovery_steps if s["matched"]) / len(recovery_steps)) if recovery_steps else None,
            "goal_completion_rate": 1.0 if done_ok else 0.0,
            "mean_latency_sec":     mean_lat,
            "mean_cost_usd":        mean_cost,
            "total_cost_usd":       total_cost,
            "total_input_tokens":   sum(step_input_toks),
            "total_output_tokens":  sum(step_output_toks),
            "fallback_rate":        fallback_rate,
            "mean_route_confidence": mean_route_conf,
            "completion_response":  completion_response,
            "completion_grounded":  completion_grounded,
            "completion_visual_confirms_goal": (
                _visual_state_indicates_goal_reached(self.steps[-1])
                if self.steps and completion.get("expected_done_sentinel") else None
            ),
            "completion_hallucinations": completion_hallucinations,
            "per_step": per_step,
        }


def load_scenario(path: str) -> Optional[Dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get("scenario_id") == "EXAMPLE_PLACEHOLDER":
            return None  # the schema doc file
        return d
    except Exception as e:
        print(f"[EVAL] scenario load failed {path}: {e}")
        return None


def load_all_scenarios(scenarios_dir: Optional[str] = None) -> List[Dict]:
    base = scenarios_dir or os.path.join(EVAL_DIR, "scenarios")
    if not os.path.isdir(base):
        return []
    out = []
    for path in sorted(glob.glob(os.path.join(base, "*.json"))):
        s = load_scenario(path)
        if s:
            out.append(s)
    return out


def aggregate_scenario_results(results: List[Dict]) -> Dict:
    """Average per-backend metrics across many scenarios. Skips None values
    (e.g. trap_pass_rate when no trap steps exist for a scenario)."""
    if not results:
        return {}
    keys = ["step_accuracy", "faithfulness", "hallucination_rate",
            "dwell_loop_rate", "loop_rate",
            "trap_pass_rate", "recovery_rate", "goal_completion_rate",
            "mean_latency_sec", "mean_cost_usd", "total_cost_usd",
            "total_input_tokens", "total_output_tokens",
            "fallback_rate", "mean_route_confidence"]
    out: Dict = {"n_scenarios": len(results)}
    for k in keys:
        vals = [r[k] for r in results if r.get(k) is not None]
        out[k] = (sum(vals) / len(vals)) if vals else None
    return out


def run_full_evaluation(manual_id: str, manual_json_path: str) -> Dict:
    """Top-level entrypoint: runs graph-quality + guide-accuracy + visual-match."""
    out: Dict = {"manual_id": manual_id}

    # 1. Graph quality: each auto workflow for this manual vs the supplied hand-authored one
    manual_graph = _load_workflow_json(manual_json_path)
    if manual_graph:
        gq = GraphQualityEvaluator()
        per_auto = []
        for p in _auto_workflow_paths(manual_id):
            auto_graph = _load_workflow_json(p)
            if not auto_graph:
                continue
            per_auto.append({
                "auto_workflow_id": auto_graph.get("workflow_id"),
                "metrics": gq.evaluate(auto_graph, manual_graph),
            })
        out["graph_quality"] = {"vs": os.path.basename(manual_json_path), "per_workflow": per_auto}
    else:
        out["graph_quality"] = {"error": f"manual graph not found at {manual_json_path}"}

    # 2. Guide accuracy
    questions = load_test_questions()
    out["guide_accuracy"] = GuideAccuracyEvaluator([manual_id]).evaluate_all(questions)

    # 3. Visual match
    screenshots = load_test_screenshots()
    out["visual_match"] = VisualMatchEvaluator(manual_id=manual_id).evaluate(screenshots)

    return out
