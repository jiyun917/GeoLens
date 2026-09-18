"""Find which Qwen replicate has empty responses + inspect context."""
import json, glob, os

for f in sorted(glob.glob("data/eval/results/run_qwen_unified3_r*_*.json")):
    d = json.load(open(f, encoding="utf-8"))
    fname = os.path.basename(f)
    empties = []
    for scen in d.get("scenarios", []):
        sid = scen.get("scenario_id", "?")
        for bname, b in scen.get("backends", {}).items():
            for i, ps in enumerate(b.get("per_step", [])):
                if not (ps.get("response") or "").strip():
                    empties.append({
                        "scenario": sid,
                        "backend": bname,
                        "step_index": ps.get("step_index", i),
                        "latency_sec": ps.get("latency_sec"),
                        "cost_usd": ps.get("cost_usd"),
                        "input_tokens": ps.get("input_tokens"),
                        "output_tokens": ps.get("output_tokens"),
                    })
    if empties:
        print(f"=== {fname} ===")
        for e in empties:
            print(f"  scenario={e['scenario']}, backend={e['backend']}, step={e['step_index']}")
            print(f"  latency={e['latency_sec']}s, cost=${e['cost_usd']}, in={e['input_tokens']}, out={e['output_tokens']}")
