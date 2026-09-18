"""Quick empty-response audit for unified3 files."""
import json, glob, os

files = sorted(glob.glob("data/eval/results/run_gemini_longctx_r*_*.json"))
print(f"Long_context files: {len(files)}")
print()
total_steps = 0
total_empty = 0
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    fname = os.path.basename(f)
    empty = 0
    steps = 0
    for scen in d.get("scenarios", []):
        lc = scen.get("backends", {}).get("long_context", {})
        for ps in lc.get("per_step", []):
            steps += 1
            if not (ps.get("response") or "").strip():
                empty += 1
    total_steps += steps
    total_empty += empty
    lc_agg = d.get("aggregate", {}).get("long_context", {})
    sa = lc_agg.get("step_accuracy", 0)
    hr = lc_agg.get("hallucination_rate", 0)
    print(f"{fname}")
    print(f"  steps={steps}, empty={empty} ({100*empty/max(steps,1):.1f}%), step_acc={sa:.3f}, hall={hr:.3f}")

print()
pct = 100 * total_empty / max(total_steps, 1)
print(f"=== TOTAL longctx: {total_steps} steps, {total_empty} empty ({pct:.1f}%) ===")
print()

print("=== Main matrix empty check ===")
for model in ["gemini", "claude", "gpt", "qwen"]:
    mfiles = sorted(glob.glob(f"data/eval/results/run_{model}_unified3_r*_*.json"))
    empty = 0
    steps = 0
    for f in mfiles:
        d = json.load(open(f, encoding="utf-8"))
        for scen in d.get("scenarios", []):
            for bname, b in scen.get("backends", {}).items():
                for ps in b.get("per_step", []):
                    steps += 1
                    if not (ps.get("response") or "").strip():
                        empty += 1
    pct = 100 * empty / max(steps, 1)
    print(f"  {model}: {steps} steps, {empty} empty ({pct:.1f}%), files={len(mfiles)}")
