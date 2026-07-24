"""Pre-bench screenshot validator.

For each captured step_N.jpg/png under data/eval/screenshots/<scenario_id>/,
run visual_state extraction (via the same guide_pipeline the runtime uses),
then check that the step's expected_action_keywords (or any allowed_alternatives
keywords) are present somewhere in the extracted visual_state text.

Reports mismatches BEFORE bench_runner is invoked so we don't waste a run on
screenshots that describe the wrong workflow.

Usage:
    .venv/Scripts/python.exe scripts/validate_screenshots.py \
        [--scenario opendtect__3d_visualization__01] \
        [--fail-on-mismatch]

Exit codes:
    0  all matches OK
    1  at least one mismatch (only when --fail-on-mismatch is set)
"""

from __future__ import annotations

import argparse
import base64
import glob
import json
import os
import sys
from pathlib import Path

# Make importable as `python scripts/validate_screenshots.py`
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if (ROOT / p).exists():
            load_dotenv(ROOT / p)
except ImportError:
    pass


def _load_screenshot_b64(path: Path) -> str | None:
    if not path.exists():
        return None
    with path.open("rb") as f:
        data = f.read()
    ext = path.suffix.lower().lstrip(".")
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def _flatten_visual_state(vs: dict) -> str:
    """Turn the extracted visual_state dict into a single searchable string."""
    parts: list[str] = []
    for k, v in (vs or {}).items():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            parts.extend(str(x) for x in v)
        elif isinstance(v, dict):
            parts.append(_flatten_visual_state(v))
    return " | ".join(p for p in parts if p)


def _keywords_of_step(step: dict) -> list[str]:
    kws = list(step.get("expected_action_keywords") or [])
    for alt in step.get("allowed_alternatives") or []:
        pat = alt.get("pattern") or alt.get("note")
        if pat:
            kws.append(pat)
    return kws


def _match_check(keywords: list[str], hay: str) -> tuple[bool, list[str]]:
    """Return (any_match, matched_keywords). Case-insensitive substring."""
    hay_lc = hay.lower()
    matched = [k for k in keywords if k and k.lower() in hay_lc]
    return (len(matched) > 0), matched


def validate_scenario(scenario_path: Path) -> list[dict]:
    """Return list of per-step validation results."""
    from api.services.guide_pipeline import get_guide_pipeline  # lazy import

    scen = json.loads(scenario_path.read_text(encoding="utf-8"))
    scenario_id = scen["scenario_id"]
    pipeline = get_guide_pipeline()

    results: list[dict] = []
    for step in scen.get("steps", []):
        idx = step["step_index"]
        shot_field = step.get("screenshot_path", "")
        shot_path = ROOT / shot_field if not os.path.isabs(shot_field) else Path(shot_field)
        # fall back to convention if missing
        if not shot_path.exists():
            for ext in ("jpg", "png", "jpeg"):
                cand = ROOT / "data" / "eval" / "screenshots" / scenario_id / f"step_{idx}.{ext}"
                if cand.exists():
                    shot_path = cand
                    break

        entry: dict = {
            "scenario_id": scenario_id,
            "step_index": idx,
            "screenshot_path": str(shot_path.relative_to(ROOT)) if shot_path.exists() else str(shot_path),
            "screenshot_exists": shot_path.exists(),
            "keywords": _keywords_of_step(step),
        }

        if not shot_path.exists():
            entry["status"] = "MISSING_SCREENSHOT"
            entry["message"] = "screenshot file not found on disk"
            results.append(entry)
            continue

        b64 = _load_screenshot_b64(shot_path)
        if not b64:
            entry["status"] = "READ_ERROR"
            entry["message"] = "could not read screenshot bytes"
            results.append(entry)
            continue

        try:
            visual_state = pipeline.recognize_visual_state(b64)
        except Exception as e:
            entry["status"] = "EXTRACT_ERROR"
            entry["message"] = f"visual_state extraction failed: {e!r}"
            results.append(entry)
            continue

        entry["visual_state"] = visual_state
        entry["visual_state_flat"] = _flatten_visual_state(visual_state)

        ok, matched = _match_check(entry["keywords"], entry["visual_state_flat"])
        entry["matched_keywords"] = matched
        entry["status"] = "OK" if ok else "MISMATCH"
        if not ok:
            entry["message"] = (
                f"none of expected keywords {entry['keywords']!r} "
                f"appear in extracted visual_state: {entry['visual_state_flat'][:200]!r}"
            )
        results.append(entry)

    return results


def format_report(results: list[dict]) -> str:
    lines: list[str] = ["# Pre-Bench Validation Report", ""]
    n_ok = sum(1 for r in results if r["status"] == "OK")
    lines.append(f"Total steps: {len(results)}  |  OK: {n_ok}  |  Issues: {len(results) - n_ok}")
    lines.append("")
    for r in results:
        marker = "OK  " if r["status"] == "OK" else "FAIL"
        lines.append(f"[{marker}] {r['scenario_id']} step_{r['step_index']}  ({r['status']})")
        lines.append(f"       shot: {r.get('screenshot_path')}")
        lines.append(f"       expected: {r['keywords']}")
        if r.get("visual_state_flat"):
            lines.append(f"       visual_state: {r['visual_state_flat'][:180]}")
        if r["status"] != "OK":
            lines.append(f"       note: {r.get('message', '')}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=None, help="Scenario id to validate (default: all under data/eval/scenarios/)")
    ap.add_argument("--fail-on-mismatch", action="store_true", help="Exit code 1 if any mismatch")
    ap.add_argument("--json-out", default=None, help="Optional path to write full JSON report")
    args = ap.parse_args()

    scen_dir = ROOT / "data" / "eval" / "scenarios"
    if args.scenario:
        paths = [scen_dir / f"{args.scenario}.json"]
    else:
        paths = sorted(scen_dir.glob("opendtect__*.json"))

    all_results: list[dict] = []
    for p in paths:
        if not p.exists():
            print(f"[SKIP] {p} does not exist")
            continue
        all_results.extend(validate_scenario(p))

    report = format_report(all_results)
    print(report)

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nJSON report: {args.json_out}")

    if args.fail_on_mismatch and any(r["status"] != "OK" for r in all_results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
