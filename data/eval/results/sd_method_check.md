# SD-computation-method audit

**Claim being checked** (from the manuscript / narrative doc):

> "Step Acc·Hall·Loop의 SD는 반복별 비율 5개(n=5) 기준 sample SD.
> Latency·Cost는 각 반복 내 8스텝 평균을 먼저 구한 뒤 반복 간 sample SD."

**Verdict**: **CONSISTENT with the code** — the two clauses describe
the same computation in different words. The unified computation is
correctly summarized as: *"per-replicate value = mean over the 8
evaluated steps in that replicate; sample SD (n-1) across the 5
replicate values."* This holds for all five core metrics uniformly.

## Actual logic (traced through the code)

### Where the per-step values come from

Each scenario runs 4 evaluated steps. For each step, the bench harness
records:

- `matched` (bool) — step_accuracy contribution
- `hallucinated` (list; non-empty = 1) — hallucination_rate contribution
- `looped` (bool) — loop_rate / dwell_loop_rate contribution
- `latency_sec` (float)
- `cost_usd` (float)

(from `api/services/evaluation.py:697-708`, one `per_step` dict per step.)

### Where the per-scenario aggregate comes from

`api/services/evaluation.py:785-800` computes for each `(scenario,
backend)`:

```python
n = max(1, len(per_step))                        # = 4 for our scenarios
step_accuracy      = sum(1 for s in per_step if s["matched"])       / n
hallucination_rate = sum(1 for s in per_step if s["hallucinated"])  / n
loop_rate          = sum(1 for s in per_step if s["looped"])        / n
mean_latency_sec   = round(sum(step_latencies) / n, 3)
mean_cost_usd      = round(total_cost / n, 6)
```

Every metric — rate or continuous — is `sum(per_step) / n`, i.e. the
per-scenario value is already an **8-step-in-2-scenarios**-style mean,
just computed at the 4-step-per-scenario granularity.

### Where the per-replicate value comes from

`scripts/compute_table1_sd.py:per_replicate_values` reads one run JSON
per replicate and, for each `(model, backend, metric)`:

```python
per_scen = []
for scen in d.get("scenarios", []) or []:
    b = (scen.get("backends") or {}).get(backend)
    v = b.get(mkey)   # scenario-level aggregate (already 4-step mean)
    if v is not None:
        per_scen.append(v)
if per_scen:
    out.append(sum(per_scen) / len(per_scen))     # ← per-replicate value
```

So the per-replicate value is `(scen1_agg + scen2_agg) / 2`.

### Why this equals "mean across 8 steps"

Both scenarios use `n=4` steps in this benchmark. Let scen_i_agg =
`hits_i / 4` (or `total_lat_i / 4`, etc.). Then:

```
(scen1_agg + scen2_agg) / 2
= (hits1/4 + hits2/4) / 2
= (hits1 + hits2) / 8
= sum over all 8 steps in the replicate, divided by 8
```

The equivalence relies on both scenarios having the same step count.
This is currently true for the v2 unified2 matrix (both scenarios have
exactly 4 steps). If a future scenario had a different step count, the
"mean of scenario means" formulation would silently weight steps
unequally, so the docstring in `compute_table1_sd.py` should note this
constraint if scenario diversity ever grows.

### Where the SD comes from

`scripts/compute_table1_sd.py:fmt`:

```python
sd = statistics.stdev(vals) if len(vals) >= 2 else 0.0
```

`statistics.stdev` in the Python stdlib uses the sample SD formula
(divisor `n-1`), so with `n=5` the divisor is 4. This matches the
manuscript's stated "sample SD" convention and matches
`scripts/stats_unified.py:welch_t` which also uses `statistics.variance`
(same n-1 basis).

## Point-by-point verdict on the claim

| Claim clause | Code reality | Match? |
|---|---|---|
| "Step Acc·Hall·Loop의 SD는 반복별 비율 5개(n=5) 기준 sample SD" | Per-replicate rate = (hits1+hits2)/8; sample SD across 5 replicates. | Match (5 replicates × per-replicate rate over 8 steps). |
| "Latency·Cost는 각 반복 내 8스텝 평균을 먼저 구한 뒤 반복 간 sample SD" | Per-scenario `mean_latency_sec` = sum(4 latencies)/4; per-replicate = mean of 2 scenarios = sum(8)/8; sample SD across 5 replicates. | Exact match. |
| Uniform treatment across rate and continuous metrics | Yes — the aggregation formula in `compute_table1_sd.py` is the same for every metric key. | Match (uniform, not per-metric-specific). |

## Cross-check with existing tables

The recomputed cells in `scripts/compute_table1_sd.py` were compared
against `data/eval/results/final_unified2_table.md` (see the
`crosscheck()` function in `compute_table1_sd.py`, and the
`0 mismatches` report in the commit message of `01eacd7`). Both
documents use the same per-replicate-value → sample-SD pipeline.

## Not investigated (not required by the claim)

- Bootstrap-based CI on the mean (used in `scripts/statistical_analysis.py`
  for a different purpose — model-level bootstrapping, not backend-level
  SD reporting).
- Whether the raw per-step values would be a defensible alternative
  unit for SD. **They would not**, in this design: per-step values
  inside a replicate are non-independent (same LLM instance, adjacent
  timing, shared cache warmth), so per-step SD would understate the
  replicate-to-replicate variability that the confidence claim
  actually cares about.

## Conclusion

The stated SD method is a faithful description of the code. No
recomputation of Table 1 numbers is required on this axis.
