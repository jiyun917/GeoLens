"""Eval-capture helper.

Walks you through the 8 active scenarios, sets the backend's runtime
capture-scenario before each, shows the goal text to paste into GeoLens,
and reports how many screenshots got saved.

Usage:

    1. Start the dev server in another terminal:
         npm run dev

    2. Run this script:
         .venv/Scripts/python.exe scripts/eval_capture_helper.py

    3. For each scenario, the script:
         - Sets the capture target on the backend
         - Prints the goal text (paste into GeoLens)
         - Waits for you to finish the workflow in OpenDtect
         - Reports captured step count

Re-runnable: pre-existing screenshots in data/eval/screenshots/{id}/
get overwritten on re-capture.
"""

import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = ROOT / "data" / "eval" / "scenarios"
SCREENSHOTS_DIR = ROOT / "data" / "eval" / "screenshots"
API_BASE = "http://127.0.0.1:8000/api"


def list_scenarios():
    return sorted(SCENARIOS_DIR.glob("opendtect__*.json"))


def count_captured(scenario_id: str) -> int:
    d = SCREENSHOTS_DIR / scenario_id
    if not d.exists():
        return 0
    return len(list(d.glob("step_*.png"))) + len(list(d.glob("step_*.jpg")))


def server_alive() -> bool:
    try:
        r = requests.get(f"{API_BASE}/eval/capture-scenario", timeout=2)
        return r.ok
    except Exception:
        return False


def set_scenario(scenario_id):
    r = requests.post(
        f"{API_BASE}/eval/capture-scenario",
        json={"scenario_id": scenario_id},
        timeout=5,
    )
    r.raise_for_status()
    return r.json()


def print_overview(scenarios):
    print(f"\n=== {len(scenarios)} active scenarios ===\n")
    for i, p in enumerate(scenarios, 1):
        scen = json.loads(p.read_text(encoding="utf-8"))
        sid = scen["scenario_id"]
        n_cap = count_captured(sid)
        n_exp = len(scen.get("steps", []))
        marker = "[DONE]" if n_cap >= n_exp and n_exp > 0 else "[    ]"
        diff = scen.get("difficulty", "?")
        cat = scen.get("category", "?")
        print(f"  {marker} {i:>2}. {sid:<55} {cat:<14} {diff:<7} {n_cap}/{n_exp}")
        goal = scen.get("goal", "")
        if len(goal) > 100:
            goal = goal[:97] + "..."
        print(f"          Goal: {goal}")
    print()


def run_one(scenario_path: Path):
    scen = json.loads(scenario_path.read_text(encoding="utf-8"))
    sid = scen["scenario_id"]
    goal = scen.get("goal", "")
    n_expected = len(scen.get("steps", []))

    try:
        set_scenario(sid)
    except Exception as e:
        print(f"[ERROR] could not set scenario on backend: {e}")
        return

    print("\n" + "=" * 70)
    print(f"  CAPTURING: {sid}")
    print(f"  Category : {scen.get('category', '?')} | Difficulty: {scen.get('difficulty', '?')}")
    print(f"  Expected : {n_expected} steps")
    print("=" * 70)
    print(f"\nGoal text to paste into GeoLens:\n")
    print(f"    {goal}\n")
    print("Now do the workflow in OpenDtect while GeoLens guides you.")
    print("Each /step call auto-saves the inbound screenshot.")
    print("\nPress Enter when this scenario is DONE (or 's' to skip)...")

    resp = input().strip().lower()
    if resp == "s":
        print("Skipped.")
        return

    # Clear scenario so subsequent calls don't accidentally save
    try:
        set_scenario(None)
    except Exception:
        pass

    n = count_captured(sid)
    status = "OK" if n >= n_expected else "INCOMPLETE"
    print(f"\n  [{status}] {n}/{n_expected} screenshots saved to:")
    print(f"     data/eval/screenshots/{sid}/\n")


def main():
    if not server_alive():
        print(
            "[ERROR] dev server not reachable at http://127.0.0.1:8000/api\n"
            "Start it first with `npm run dev` (or python -m uvicorn api.index:app --reload)."
        )
        sys.exit(1)

    scenarios = list_scenarios()
    if not scenarios:
        print(f"No scenarios found under {SCENARIOS_DIR}")
        sys.exit(1)

    print_overview(scenarios)

    while True:
        choice = input("Pick scenario # (l=list, a=all sequentially, q=quit): ").strip().lower()
        if choice == "q":
            break
        if choice == "l":
            print_overview(scenarios)
            continue
        if choice == "a":
            for p in scenarios:
                run_one(p)
                print_overview(scenarios)
            continue
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(scenarios):
                run_one(scenarios[idx])
                print_overview(scenarios)
            else:
                print("out of range")
        except ValueError:
            print("invalid input")


if __name__ == "__main__":
    main()
