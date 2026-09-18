"""QGIS Pilot bench runner — Gemini × {no_rag, vanilla_vector, full_system} × 5 reps × 1 scenario.

Recovery-aware (rc=4 credit-depletion immediate abort inherited from
unified3/4 recovery wrapper).

Isolation via temporary file state (no core code changes):
  1. Move all non-QGIS workflow JSONs to data/workflows/.pilot_backup/
     (survey_setup, d3_visualization, seismic_attribute, fault_interpretation,
     horizon_tracking) — keep only qgis_vector_buffer.json and any
     auto_bf2804feea57__* workflows in the loader path.
  2. Create data/eval/scenarios/.qgis_pilot_only/ with only qgis__vector_buffer__01.
  3. Run bench_runner with --scenarios pointing to that subdir.
  4. Restore workflow files on exit (try/finally).

Checkpoint after replicate 1: empty-response count check.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(str(Path(__file__).resolve().parent.parent))
WORKFLOWS_DIR = ROOT / "data" / "workflows"
WORKFLOWS_BACKUP = WORKFLOWS_DIR / ".pilot_backup"
QGIS_SCENARIO_DIR = ROOT / "data" / "eval" / "scenarios" / ".qgis_pilot_only"
SOURCE_SCENARIO = ROOT / "data" / "eval" / "scenarios" / "qgis__vector_buffer__01.json"
RESULTS_DIR = ROOT / "data" / "eval" / "results"
LOG = RESULTS_DIR / "qgis_pilot_bench.log"

OPENDTECT_WORKFLOWS = [
    "survey_setup.json",
    "d3_visualization.json",
    "seismic_attribute.json",
    "fault_interpretation.json",
    "horizon_tracking.json",
]

import argparse

_ap = argparse.ArgumentParser()
_ap.add_argument("--reps", type=int, default=5)
_ap.add_argument("--tag", default="qgis_pilot")
_ap.add_argument("--models", default="gemini,claude,gpt",
                 help="v3: every generator runs the QGIS test set (v2 pilot was Gemini only)")
_ap.add_argument("--isolate", action="store_true",
                 help="v2 behaviour: move OpendTect workflow JSONs out of the loader path "
                      "for the run. v3 default keeps all workflows loaded so the router "
                      "must pick the QGIS workflow among OpendTect distractors.")
_ARGS, _ = _ap.parse_known_args()

TOTAL_REPS = _ARGS.reps
INTER_SLEEP = 30            # seconds between replicates
PROBE_WAIT_MAX = 1800
PROBE_WAIT_INTERVAL = 60


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(msg: str):
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def gemini_probe() -> int:
    """Return: 0=OK, 1=throttled, 2=no key, 3=other, 4=credit_depleted (from recovery wrapper)."""
    code = subprocess.run(
        [str(ROOT / ".venv/Scripts/python.exe"), "-c", '''
import os, sys
try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if os.path.exists(p): load_dotenv(p)
except: pass
key = os.environ.get("GEMINI_API_KEY")
if not key: sys.exit(2)
try:
    from google import genai
    from google.genai import types as t
    client = genai.Client(api_key=key)
    r = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=[t.Part.from_text(text="ok")],
        config=t.GenerateContentConfig(temperature=0, max_output_tokens=5))
    sys.exit(0)
except Exception as e:
    m = str(e)
    if "prepayment credits are depleted" in m or "credits are depleted" in m.lower(): sys.exit(4)
    if "429" in m or "RESOURCE_EXHAUSTED" in m or "rate limit" in m.lower(): sys.exit(1)
    sys.exit(3)
'''], cwd=str(ROOT), capture_output=True, text=True)
    return code.returncode


def wait_for_quota() -> int:
    """0=proceed, 2=CREDIT_DEPLETED abort, 1=other timeout abort."""
    elapsed = 0
    while elapsed < PROBE_WAIT_MAX:
        rc = gemini_probe()
        if rc == 0:
            log(f"probe OK — proceed")
            return 0
        if rc == 4:
            log(f"probe CREDIT_DEPLETED — ABORT (recharge needed)")
            return 2
        log(f"probe rc={rc} — wait {PROBE_WAIT_INTERVAL}s")
        time.sleep(PROBE_WAIT_INTERVAL)
        elapsed += PROBE_WAIT_INTERVAL
    log(f"probe timeout {PROBE_WAIT_MAX}s")
    return 1


def isolate_workflows():
    """Move OpendTect workflow JSONs to backup subdir."""
    WORKFLOWS_BACKUP.mkdir(exist_ok=True)
    moved = []
    for fname in OPENDTECT_WORKFLOWS:
        src = WORKFLOWS_DIR / fname
        if src.exists():
            dst = WORKFLOWS_BACKUP / fname
            shutil.move(str(src), str(dst))
            moved.append(fname)
    log(f"isolated {len(moved)} OpendTect workflows → .pilot_backup/: {moved}")
    remaining = sorted(f.name for f in WORKFLOWS_DIR.glob("*.json"))
    log(f"active workflow set for pilot: {remaining}")


def restore_workflows():
    """Restore OpendTect workflow JSONs from backup."""
    if not WORKFLOWS_BACKUP.exists():
        return
    restored = []
    for fname in OPENDTECT_WORKFLOWS:
        src = WORKFLOWS_BACKUP / fname
        if src.exists():
            dst = WORKFLOWS_DIR / fname
            shutil.move(str(src), str(dst))
            restored.append(fname)
    # Only remove backup dir if empty
    try:
        WORKFLOWS_BACKUP.rmdir()
    except OSError:
        pass
    log(f"restored {len(restored)} OpendTect workflows: {restored}")


def prepare_scenario_dir():
    QGIS_SCENARIO_DIR.mkdir(exist_ok=True)
    dst = QGIS_SCENARIO_DIR / SOURCE_SCENARIO.name
    shutil.copy2(str(SOURCE_SCENARIO), str(dst))
    log(f"scenarios subdir prepared: {QGIS_SCENARIO_DIR.relative_to(ROOT)}/{dst.name}")


def cleanup_scenario_dir():
    if QGIS_SCENARIO_DIR.exists():
        shutil.rmtree(str(QGIS_SCENARIO_DIR))
        log(f"cleaned up scenarios subdir: {QGIS_SCENARIO_DIR.relative_to(ROOT)}")


def run_replicate(r: int, model: str = "gemini") -> tuple[int, str]:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_file = RESULTS_DIR / f"run_{model}_{_ARGS.tag}_r{r}_{ts}.json"
    log(f"replicate {r}/{TOTAL_REPS} [{model}] starting → {out_file.name}")
    proc = subprocess.run(
        [str(ROOT / ".venv/Scripts/python.exe"), "-m", "api.services.bench_runner",
         "--model", model,
         "--out", str(out_file),
         "--scenarios", str(QGIS_SCENARIO_DIR)],   # v3: all 7 backends (default BACKENDS), same as the dev set
        cwd=str(ROOT),
        env={**os.environ, "GEOLENS_SOFTWARE_ID": "qgis"},
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    log(f"replicate {r} exit={proc.returncode}")
    if proc.returncode != 0:
        log(f"stderr tail: {proc.stderr[-500:]}")
    return proc.returncode, str(out_file)


def check_empty(out_file: str) -> tuple[int, int]:
    """Return (total_steps, empty_steps) from a bench output JSON."""
    d = json.loads(Path(out_file).read_text(encoding="utf-8"))
    total = 0
    empty = 0
    for scen in d.get("scenarios", []):
        for bname, b in (scen.get("backends") or {}).items():
            if not b or "per_step" not in b: continue
            for st in b["per_step"]:
                total += 1
                resp = st.get("response") or ""
                if not resp.strip():
                    empty += 1
    return total, empty


def check_depletion_in_log():
    try:
        tail = Path(LOG).read_text(encoding="utf-8").splitlines()[-200:]
    except Exception:
        return False
    return any("credits are depleted" in line.lower() for line in tail)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    log("=" * 70)
    log("QGIS Pilot bench kickoff")
    log("=" * 70)

    # Pre-flight probe
    log("pre-flight Gemini quota probe")
    if (rc := wait_for_quota()) != 0:
        log(f"pre-flight ABORT (rc={rc})")
        return 1

    outputs = []
    try:
        if _ARGS.isolate:
            isolate_workflows()
        else:
            active = sorted(f.name for f in WORKFLOWS_DIR.glob("*.json"))
            log(f"no isolation (v3): active workflow set = {active}")
        prepare_scenario_dir()

        for r in range(1, TOTAL_REPS + 1):
            log(f"--- replicate {r}/{TOTAL_REPS} pre-run probe ---")
            if (rc := wait_for_quota()) != 0:
                log(f"replicate {r} ABORT pre-probe (rc={rc}) — stop")
                break

            failed = False
            for model in [m.strip() for m in _ARGS.models.split(",") if m.strip()]:
                code, out_file = run_replicate(r, model)
                outputs.append(out_file)
                if code != 0:
                    log(f"replicate {r} [{model}] FAILED (exit {code}) — stop")
                    failed = True
                    break
            if failed:
                break

            if check_depletion_in_log():
                log(f"post-replicate depletion detected — stop")
                break

            # Post-replicate checkpoint
            total, empty = check_empty(out_file)
            log(f"replicate {r} empty audit: {empty}/{total}")
            if empty > 0:
                log(f"replicate {r} has empty responses — flagging for review")

            # Checkpoint after replicate 1 (user request: backend/replicate 1 clean check)
            if r == 1:
                log(f"CHECKPOINT after replicate 1: {empty}/{total} empty")
                if empty > 0:
                    log(f"CHECKPOINT WARNING: rep 1 has empty responses. Continuing (stop rule allows 1 discard-and-rerun if needed).")

            if r < TOTAL_REPS:
                log(f"inter-replicate cooldown {INTER_SLEEP}s")
                time.sleep(INTER_SLEEP)

    finally:
        cleanup_scenario_dir()
        if _ARGS.isolate:
            restore_workflows()

    log("=" * 70)
    log(f"QGIS Pilot bench complete — {len(outputs)} replicate files")
    for f in outputs:
        log(f"  {Path(f).name}")
    log("=" * 70)

    # Final summary
    log("Final empty audit across all pilot replicates:")
    total_all = 0
    empty_all = 0
    for f in outputs:
        try:
            t, e = check_empty(f)
            total_all += t
            empty_all += e
            log(f"  {Path(f).name}: empty={e}/{t}")
        except Exception as ex:
            log(f"  {Path(f).name}: parse error {ex}")
    log(f"TOTAL: empty={empty_all}/{total_all}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
