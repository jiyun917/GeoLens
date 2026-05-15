"""
Validate labeled scenario JSONs before running the benchmark.

Checks:
  - Required top-level fields present
  - Steps are non-empty and step_index is contiguous from 0
  - Each step has either expected_action_text_pattern OR expected_action_keywords
  - All regex patterns compile
  - screenshot_path files exist on disk
  - No `[TODO` placeholders remain in critical fields
  - visited / completion structure valid

CLI:
    python -m api.services.scenario_validator data/eval/scenarios/*.json
    python -m api.services.scenario_validator --strict <files>
"""

import argparse
import glob
import json
import os
import re
import sys
from typing import Dict, List, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

REQUIRED_TOP = ["scenario_id", "manual_id", "goal", "steps", "completion"]
REQUIRED_STEP = ["step_index", "screenshot_path", "visual_state_gt"]


def _resolve(p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(PROJECT_ROOT, p)


def validate_scenario(path: str, strict: bool = False) -> Tuple[bool, List[str], List[str]]:
    """Return (ok, errors, warnings)."""
    errors: List[str] = []
    warnings: List[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            scen = json.load(f)
    except Exception as e:
        return False, [f"JSON parse failed: {e}"], []

    # Skip the schema doc file
    if scen.get("scenario_id") == "EXAMPLE_PLACEHOLDER":
        return True, [], ["schema doc — skipped"]

    # Top-level fields
    for k in REQUIRED_TOP:
        if k not in scen:
            errors.append(f"missing top-level field: {k}")

    # Steps
    steps = scen.get("steps") or []
    if not steps:
        errors.append("steps list is empty")
    for i, st in enumerate(steps):
        prefix = f"steps[{i}]"
        if st.get("step_index") != i:
            errors.append(f"{prefix} step_index expected {i}, got {st.get('step_index')}")
        for k in REQUIRED_STEP:
            if k not in st:
                errors.append(f"{prefix} missing field: {k}")

        # at least one of pattern or keywords
        pat = st.get("expected_action_text_pattern")
        kws = st.get("expected_action_keywords")
        if not pat and not kws:
            errors.append(f"{prefix} needs expected_action_text_pattern OR expected_action_keywords")
        if pat:
            try:
                re.compile(pat)
            except re.error as e:
                errors.append(f"{prefix} pattern compile failed: {e}")

        # screenshot existence
        sp = st.get("screenshot_path") or ""
        if "[TODO" in sp:
            (errors if strict else warnings).append(f"{prefix} screenshot_path still placeholder: {sp}")
        elif sp and not os.path.exists(_resolve(sp)):
            (errors if strict else warnings).append(f"{prefix} screenshot file not found: {sp}")

        # visual_state_gt TODOs
        vs = st.get("visual_state_gt") or {}
        if any("[TODO" in str(v) for v in vs.values() if v is not None):
            (errors if strict else warnings).append(f"{prefix} visual_state_gt has [TODO] placeholders")

        # alternatives patterns
        for j, alt in enumerate(st.get("allowed_alternatives") or []):
            ap = alt.get("pattern")
            if ap:
                try:
                    re.compile(ap)
                except re.error as e:
                    errors.append(f"{prefix} allowed_alternatives[{j}] pattern compile failed: {e}")

        # trap consistency
        if st.get("trap") and not st.get("is_error_recovery_test") and not st.get("expected_action_keywords"):
            warnings.append(f"{prefix} has trap but no expected_action — what does pass look like?")

    # Goal placeholder
    if "[TODO" in (scen.get("goal") or ""):
        (errors if strict else warnings).append("goal still contains [TODO] placeholder")

    # Completion
    comp = scen.get("completion") or {}
    cp = comp.get("final_screenshot_path") or ""
    if cp and "[TODO" in cp:
        warnings.append(f"completion.final_screenshot_path placeholder: {cp}")
    elif cp and not os.path.exists(_resolve(cp)):
        warnings.append(f"completion.final_screenshot_path not found: {cp}")

    return (not errors), errors, warnings


def main():
    p = argparse.ArgumentParser()
    p.add_argument("paths", nargs="+", help="scenario JSON files or globs")
    p.add_argument("--strict", action="store_true",
                   help="treat missing screenshots / TODO placeholders as errors")
    args = p.parse_args()

    files: List[str] = []
    for pat in args.paths:
        files.extend(sorted(glob.glob(pat)))
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        print("no files matched")
        sys.exit(2)

    total_ok = 0
    for f in files:
        ok, errs, warns = validate_scenario(f, strict=args.strict)
        bn = os.path.basename(f)
        if ok and not warns:
            print(f"  OK   {bn}")
            total_ok += 1
        elif ok:
            print(f"  WARN {bn}")
            for w in warns:
                print(f"        ⚠ {w}")
            total_ok += 1
        else:
            print(f"  FAIL {bn}")
            for e in errs:
                print(f"        ✗ {e}")
            for w in warns:
                print(f"        ⚠ {w}")

    print(f"\n{total_ok}/{len(files)} scenarios valid")
    sys.exit(0 if total_ok == len(files) else 1)


if __name__ == "__main__":
    main()
