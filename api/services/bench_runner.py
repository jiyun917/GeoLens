"""
Benchmark runner — loads every labeled scenario under data/eval/scenarios/,
runs all four backends against each scenario, and writes a JSON result
file plus a Markdown summary table for the paper.

Usage (from project root):

    .venv/Scripts/python.exe -m api.services.bench_runner \
        --out data/eval/results/run_$(date +%Y%m%d).json

The output file contains per-scenario + aggregate metrics for each
backend. The Markdown table is printed to stdout AND saved next to the
JSON for easy paste into the paper.
"""

import argparse
import datetime
import json
import os
import sys
import time
from typing import Dict, List

# Force UTF-8 stdout/stderr. Without this, ANY print containing an em-dash
# (U+2014), Korean text, or common Unicode punctuation crashes on Windows'
# cp949 default with `UnicodeEncodeError`. That error propagates up through
# `_call_gemini_variant` → the evaluator's try/except catches it and stores
# response="" — producing the "EMPTY response at step 3" phantom bug we
# spent hours chasing. Set the encoding once here so no subprocess ever
# has to worry about it again.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Make this runnable as `python -m api.services.bench_runner`
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load .env.local so GEMINI_API_KEY / ANTHROPIC_API_KEY are visible to the
# backends. When bench_runner is invoked as a bare subprocess (not via
# uvicorn), the environment is otherwise empty and every LLM call silently
# returns an empty string.
try:
    from dotenv import load_dotenv  # noqa: E402
    for _p in (".env.local", ".env"):
        if os.path.exists(_p):
            load_dotenv(_p)
except ImportError:
    pass

from api.services.evaluation import (  # noqa: E402
    BACKENDS,
    ScenarioEvaluator,
    aggregate_scenario_results,
    load_all_scenarios,
)
from api.services.bench_backends import BACKEND_REGISTRY  # noqa: E402


def run_all(out_path: str, scenarios_dir: str = None, backends: List[str] = None,
            judge_mode: str = None) -> Dict:
    scenarios = load_all_scenarios(scenarios_dir)
    if not scenarios:
        print(f"No scenarios found under {scenarios_dir or 'data/eval/scenarios'}")
        return {}
    backend_names = list(backends or BACKENDS)

    results: Dict = {
        "started_at": datetime.datetime.utcnow().isoformat() + "Z",
        "scenarios": [],
        "aggregate": {},
    }

    for scen in scenarios:
        sid = scen.get("scenario_id", "?")
        print(f"\n=== {sid} ({len(scen.get('steps', []))} steps) ===")
        evaluator = ScenarioEvaluator(scen)
        scen_result = {"scenario_id": sid, "manual_id": scen.get("manual_id"),
                       "category": scen.get("category"), "difficulty": scen.get("difficulty"),
                       "backends": {}}
        for bname in backend_names:
            backend = BACKEND_REGISTRY.get(bname)
            if not backend:
                print(f"  - {bname}: SKIP (not registered)")
                continue
            t0 = time.time()
            try:
                metrics = evaluator.evaluate_backend(bname, backend)
            except Exception as e:
                print(f"  - {bname}: FAIL ({e})")
                metrics = {"backend": bname, "error": str(e)}
            metrics["latency_sec"] = round(time.time() - t0, 2)

            # Optional: re-score with LLM-as-judge (semantic, lenient)
            if judge_mode and metrics.get("per_step"):
                try:
                    from api.services.bench_judge import annotate_with_judge
                    judge_result = annotate_with_judge(
                        metrics["per_step"], scen.get("steps", []), mode=judge_mode
                    )
                    metrics["judge"] = judge_result
                except Exception as e:
                    print(f"  - {bname}: judge failed ({e})")

            scen_result["backends"][bname] = metrics
            def _f(v):
                return f"{v:.2f}" if isinstance(v, (int, float)) else "—"
            print(
                f"  - {bname:<14} "
                f"step_acc={_f(metrics.get('step_accuracy'))} "
                f"hall={_f(metrics.get('hallucination_rate'))} "
                f"loop={_f(metrics.get('dwell_loop_rate'))} "
                f"latency={metrics['latency_sec']}s"
            )
        results["scenarios"].append(scen_result)

    # Aggregate per-backend across scenarios
    for bname in backend_names:
        per_scen_metrics = [
            s["backends"].get(bname) for s in results["scenarios"]
            if s["backends"].get(bname) and "error" not in s["backends"][bname]
        ]
        results["aggregate"][bname] = aggregate_scenario_results(per_scen_metrics)

    # Write JSON
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Print + save markdown table
    md = _render_markdown_table(results, backend_names)
    md_path = out_path.rsplit(".", 1)[0] + ".md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print("\n" + md)
    print(f"\nResults written: {out_path}\nMarkdown:        {md_path}")
    return results


def _render_markdown_table(results: Dict, backend_names: List[str]) -> str:
    lines: List[str] = ["# Benchmark Results", ""]
    lines.append(f"Started: {results.get('started_at')}")
    lines.append(f"Scenarios: {len(results.get('scenarios', []))}")
    lines.append("")
    lines.append("## Aggregate (mean across scenarios)")
    lines.append("")
    cols = ["step_accuracy", "hallucination_rate", "dwell_loop_rate",
            "trap_pass_rate", "recovery_rate", "goal_completion_rate"]
    lines.append("| backend | " + " | ".join(cols) + " |")
    lines.append("|" + "|".join(["---"] * (len(cols) + 1)) + "|")
    for bname in backend_names:
        agg = results.get("aggregate", {}).get(bname, {})
        row = [bname]
        for c in cols:
            v = agg.get(c)
            row.append(f"{v:.3f}" if isinstance(v, (int, float)) else "—")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", default=None)
    parser.add_argument("--out", default=None,
                        help="Output path. If omitted, defaults to run_<model>_<timestamp>.json.")
    parser.add_argument("--backends", nargs="*", default=None,
                        help="Subset of backend names to run (default: all 5)")
    parser.add_argument("--judge", default=None,
                        choices=["claude", "gemini", "consensus", "strict"],
                        help="Optionally re-score with LLM-as-judge (more lenient than regex match)")
    parser.add_argument("--model", default=None,
                        choices=["gemini", "gemini_flash", "claude", "qwen", "gpt"],
                        help="Generator model for all backends. Sets BENCH_MODEL env var. "
                             "Defaults to whatever BENCH_MODEL is already set to (or 'gemini').")
    args = parser.parse_args()

    if args.model:
        os.environ["BENCH_MODEL"] = args.model

    model_tag = os.environ.get("BENCH_MODEL", "gemini")
    if args.out is None:
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        args.out = os.path.join("data", "eval", "results", f"run_{model_tag}_{ts}.json")

    run_all(args.out, scenarios_dir=args.scenarios, backends=args.backends,
            judge_mode=args.judge)


if __name__ == "__main__":
    main()
