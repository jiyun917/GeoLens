"""Qwen effective cost conversion — hardware confirmed 2026-07-27.

Confirmed hardware at the vLLM endpoint (168.131.141.77:28000):
    4× NVIDIA RTX 6000 Ada 48GB, TP=4, GPTQ int4, max-model-len=32,768.
The earlier "A100 80GB × 4" placeholder was an over-estimate of the GPU
tier and has been retired. Ratios between backends are unaffected by the
tier choice (cost = latency × constant hourly rate); absolute values
scale linearly.

Cloud rental rate reference: RunPod Secure Cloud, RTX 6000 Ada 48GB
    $0.84/hr per GPU (queried 2026-07-27 from https://www.runpod.io/pricing).
Hourly rate for the 4-GPU node: $0.84 × 4 = $3.36/h.

Per-step effective cost formula:
    effective_cost_usd = (latency_sec / 3600) × hourly_rate

For each per_step row in Qwen result files, we compute:
    ps["effective_cost_usd"] = (ps["latency_sec"] / 3600) * HOURLY_RATE

This is written into a new field alongside the original cost_usd=0.0
(which correctly reflects the self-hosted per-token marginal). Backend-
level aggregates 'mean_cost_usd_effective' and 'total_cost_usd_effective'
are also recomputed so the final table can source from these fields.

Primary reporting recommendation: use GPU-time/step (latency × N_GPU)
as the primary Qwen cost unit, with the RunPod-derived USD figure as a
comparability secondary. See data/eval/results/cost_basis.md §5 for the
manuscript-ready phrasing.

Usage:
    .venv/Scripts/python.exe scripts/qwen_cost_convert.py \\
        --tag unified2 --gpus 4 --gpu-type rtx-6000-ada-48gb
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path
from statistics import fmean

ROOT = Path(__file__).resolve().parent.parent

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# Cloud rental rate reference (USD/h per GPU).
# rtx-6000-ada-48gb rate is the confirmed benchmark-time hardware; source
# is RunPod Secure Cloud (https://www.runpod.io/pricing, queried 2026-07-27).
# Others retained as reference for alternative reporting.
CLOUD_RATES = {
    "rtx-6000-ada-48gb": 0.84,   # RunPod Secure Cloud, queried 2026-07-27
    "a100-80gb":         1.29,   # Lambda Labs 2026-07 (legacy default)
    "h100-80gb":         2.49,   # Lambda Labs 2026-07
    "a6000-48gb":        0.80,   # Lambda Labs 2026-07
    "l40s-48gb":         1.00,   # Lambda Labs 2026-07
}


def convert_file(path: Path, hourly_rate: float, dry_run: bool = False) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    stats = {"file": path.name, "cells_updated": 0, "steps_touched": 0}
    for scen in d.get("scenarios", []) or []:
        for bname, b in (scen.get("backends") or {}).items():
            if not b or "error" in b:
                continue
            per = b.get("per_step") or []
            eff_costs = []
            for ps in per:
                lat = ps.get("latency_sec")
                if lat is None:
                    continue
                eff = (lat / 3600.0) * hourly_rate
                ps["effective_cost_usd"] = round(eff, 6)
                eff_costs.append(eff)
                stats["steps_touched"] += 1
            if eff_costs:
                b["mean_cost_usd_effective"] = round(fmean(eff_costs), 6)
                b["total_cost_usd_effective"] = round(sum(eff_costs), 6)
                stats["cells_updated"] += 1
    # Also recompute aggregate section if present
    if "aggregate" in d:
        for bname, agg in (d["aggregate"] or {}).items():
            # collect from scenarios
            eff_vals = []
            for scen in d["scenarios"]:
                b = (scen.get("backends") or {}).get(bname)
                if b and b.get("mean_cost_usd_effective") is not None:
                    eff_vals.append(b["mean_cost_usd_effective"])
            if eff_vals:
                agg["mean_cost_usd_effective"] = round(fmean(eff_vals), 6)
    if not dry_run:
        path.write_text(json.dumps(d, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="unified2")
    ap.add_argument("--gpus", type=int, default=4,
                    help="Number of GPUs assumed (default 4)")
    ap.add_argument("--gpu-type", default="rtx-6000-ada-48gb",
                    choices=list(CLOUD_RATES.keys()),
                    help="GPU model (default rtx-6000-ada-48gb — confirmed hardware)")
    ap.add_argument("--hourly-rate", type=float, default=None,
                    help="Override hourly rate (else derived from --gpu-type × --gpus)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.hourly_rate is None:
        per_gpu = CLOUD_RATES[args.gpu_type]
        args.hourly_rate = per_gpu * args.gpus

    print(f"Conversion parameters:")
    print(f"  GPU type:     {args.gpu_type}")
    print(f"  GPU count:    {args.gpus}")
    print(f"  Hourly rate:  ${args.hourly_rate:.2f}/h (= ${CLOUD_RATES.get(args.gpu_type, 0):.2f} × {args.gpus})")
    print(f"  Rate source:  RunPod Secure Cloud (https://www.runpod.io/pricing, queried 2026-07-27)")
    print(f"  Formula:      cost_per_step = (latency_sec / 3600) × hourly_rate")
    print()

    files = sorted(glob.glob(
        str(ROOT / f"data/eval/results/run_qwen_{args.tag}_r*_*.json")
    ))
    print(f"Files matched: {len(files)}")
    total_cells = 0
    total_steps = 0
    for f in files:
        s = convert_file(Path(f), args.hourly_rate, dry_run=args.dry_run)
        total_cells += s["cells_updated"]
        total_steps += s["steps_touched"]
        print(f"  {s['file']}: cells={s['cells_updated']} steps={s['steps_touched']}")
    print(f"\nTotal: {total_cells} backend cells, {total_steps} per_step rows updated.")

    if not args.dry_run and files:
        print("\nField 'effective_cost_usd' added to per_step and 'mean_cost_usd_effective' to backend aggregates.")


if __name__ == "__main__":
    main()
