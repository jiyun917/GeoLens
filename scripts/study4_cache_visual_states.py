# -*- coding: utf-8 -*-
"""Study 4 development: dump the Flash vision output (visual_state JSON, prompt v3, temperature 0,
AUX_THINKING_BUDGET=0 - the bench configuration) for every screenshot of the development scenarios
to data/eval/study4/visual_states/<scenario_id>/step_<i>.json, so routing rules can be replayed
offline without API calls. Reads screenshots only; never reads model responses or GT labels.
Usage: .venv/Scripts/python.exe scripts/study4_cache_visual_states.py [--dirs d1,d2,...] [--force]
"""
from __future__ import annotations
import argparse, base64, glob, hashlib, json, os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
try:
    from dotenv import load_dotenv
    for p in (".env.local", ".env"):
        if (ROOT / p).exists():
            load_dotenv(ROOT / p)
except ImportError:
    pass
os.environ.setdefault("AUX_THINKING_BUDGET", "0")
os.environ.setdefault("VISION_PROMPT_VERSION", "v3")
os.environ.setdefault("CHROMADB_PATH", "./data/chromadb_v4")
os.environ.setdefault("EMBED_MODEL", "BAAI/bge-m3")
DEFAULT_DIRS = ["data/eval/scenarios/.dev_opendtect", "data/eval/scenarios/.study2_test",
                "data/eval/scenarios/.study3_test_opendtect", "data/eval/scenarios/.study3_test_qgis"]
EXTRA_FILES = ["data/eval/scenarios/qgis__vector_buffer__01.json"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", default=",".join(DEFAULT_DIRS))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    files = []
    for d in args.dirs.split(","):
        files += sorted(glob.glob(str(ROOT / d / "*.json")))
    files += [str(ROOT / f) for f in EXTRA_FILES if (ROOT / f).exists()]
    from api.services.guide_pipeline import get_guide_pipeline, get_visual_state_cache_stats
    pipe = get_guide_pipeline()
    out_root = ROOT / "data/eval/study4/visual_states"
    n_call = 0; n_skip = 0
    for f in files:
        sc = json.load(open(f, encoding="utf-8"))
        sid = sc["scenario_id"]
        os.environ["GEOLENS_SOFTWARE_ID"] = "qgis" if sid.startswith("qgis") else "opendtect"
        (out_root / sid).mkdir(parents=True, exist_ok=True)
        for st in sc["steps"]:
            i = st["step_index"]; sp = ROOT / st["screenshot_path"]
            out = out_root / sid / f"step_{i}.json"
            if not sp.exists():
                print(f"{sid} s{i}: screenshot missing"); continue
            raw = sp.read_bytes(); sha = hashlib.sha256(raw).hexdigest()
            if out.exists() and not args.force:
                try:
                    if json.load(open(out, encoding="utf-8")).get("sha256") == sha:
                        n_skip += 1; continue
                except Exception:
                    pass
            b64 = "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")
            vs = {}
            for attempt in range(3):
                vs = pipe.recognize_visual_state(b64)
                if vs: break
                time.sleep(3)
            out.write_text(json.dumps({"scenario_id": sid, "step_index": i, "screenshot_path": st["screenshot_path"], "sha256": sha,
                                       "software_id": os.environ["GEOLENS_SOFTWARE_ID"], "vision_prompt": "v3", "visual_state": vs},
                                      ensure_ascii=False, indent=1), encoding="utf-8")
            n_call += 1
            print(f"{sid} s{i}: {'ok' if vs else 'EMPTY'} dialog={str(vs.get('current_dialog'))[:50]!r}", flush=True)
    print(f"done: calls={n_call} skipped={n_skip} cache={get_visual_state_cache_stats()}")


if __name__ == "__main__":
    main()
