# Cost basis documentation

Traces the code path that produces `mean_cost_usd` / `total_cost_usd` in
every `run_*_r*_*.json`, records the pricing constants and their source
date, verifies the reported `$283.45m` per-step cost for Gemini
long_context arithmetically, and flags one assumption the manuscript
should acknowledge (Gemini long-context tier pricing).

## 1. Where cost is computed

`api/services/bench_backends.py:62-91` defines `MODEL_PRICING` and
`_record_usage(model, input_tokens, output_tokens)`:

```python
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gemini":       {"in_per_m": 1.25, "out_per_m": 10.00, "label": "gemini-2.5-pro"},
    "gemini_flash": {"in_per_m": 0.30, "out_per_m":  2.50, "label": "gemini-2.5-flash"},
    "claude":       {"in_per_m": 3.00, "out_per_m": 15.00, "label": "claude-sonnet-4-6"},
    "gpt":          {"in_per_m": 2.50, "out_per_m": 10.00, "label": "gpt-4o"},
    "qwen":         {"in_per_m": 0.00, "out_per_m":  0.00, "label": "qwen3-235b-a22b-instruct (self-hosted)"},
}

def _record_usage(model, input_tokens, output_tokens):
    price = MODEL_PRICING.get(model, {"in_per_m": 0.0, "out_per_m": 0.0})
    cost = (input_tokens / 1_000_000) * price["in_per_m"] \
         + (output_tokens / 1_000_000) * price["out_per_m"]
    _LAST_USAGE["cost_usd"] = round(cost, 6)
```

The bench runner reads `_LAST_USAGE` after each LLM call and attaches
`cost_usd` to that per-step record (`api/services/evaluation.py:708`).
Backend and scenario aggregates then average these per-step costs.

## 2. Price table + date

Per-1M-token USD, as hard-coded in `bench_backends.py`. Source comment
in the file: *"Prices reflect 2026-07 published rates."*

| Model              | Input $/M | Output $/M | Runs against          |
|---|---|---|---|
| gemini-2.5-pro     | 1.25      | 10.00      | 4 model × 6 backend cells + long_context |
| gemini-2.5-flash   | 0.30      | 2.50       | (not used in v2 unified2 matrix) |
| claude-sonnet-4-6  | 3.00      | 15.00      | 4 × 6 cells                              |
| gpt-4o             | 2.50      | 10.00      | 4 × 6 cells                              |
| qwen3-235b-a22b    | 0.00      | 0.00       | 4 × 6 cells; effective cost via §5 below |

**Flat rate.** The `MODEL_PRICING` table has a single input price and
single output price per model — no tier logic. This matters for Gemini
long-context (see §3).

**No prompt caching.** No prompt-caching or cache-hit discount is
applied in the code path above. Every request is priced as fresh input
tokens × the vendor's non-cached rate. This is a conservative choice
(costs reported would be *lower* if we credited the API's actual cache
hit rates), but it needs to be stated so a reader who tries to
reproduce doesn't assume cache-adjusted numbers.

## 3. Gemini long_context ($283.45m / step) — arithmetic check

**Per-step data** (from `run_gemini_longctx_r1_20260723T034253.json`,
step 0 of survey_setup):

```
input_tokens  = 226,621
output_tokens = 21
cost_usd      = 0.283486   ← what the code stored
```

**Reproduce with the flat rate in the code:**

```
(226_621 / 1e6) * 1.25 + (21 / 1e6) * 10.00
= 0.28328 + 0.00021
= 0.28349
```

Rounded to 6 places, this reproduces the stored `0.283486` exactly.
The reported 5-replicate mean `$283.45m / step` therefore matches the
code's arithmetic, and the reported cost ratio to Gemini `full_system`
($2.66m/step) is **283.45 / 2.66 = 106.6×** as stated in the paper.

## 4. Assumption to acknowledge — Gemini long-context tier pricing

The manual used in this benchmark is ~226K input tokens per query, which
exceeds Gemini 2.5 Pro's 200K-token pricing tier boundary (per the
publicly listed schedule, tokens beyond the 200K threshold are billed at
2× the base rate for gemini-2.5-pro: $2.50/M input, $15/M output). The
code applies the base (≤200K) rate uniformly.

**If the tiered schedule is applied** to the same per-step data:

```
(226_621 / 1e6) * 2.50 + (21 / 1e6) * 15.00
= 0.56655 + 0.00032
= 0.56687
```

per step, i.e. **$566.87m / step** instead of $283.45m — a 2× under-
report **if** the tier applies to this workload. Under that alternative
accounting, the cost ratio would be **566.87 / 2.66 ≈ 213×**, not 106.6×.

**Recommendation for the manuscript**:

1. State the flat-rate assumption explicitly ("costs computed at the
   base per-1M rate; no tier surcharge or cache discount applied"), OR
2. Recompute long_context costs at the tier-adjusted rate for the >200K
   tokens portion and re-derive the multiplier. Only long_context is
   affected — no other backend crosses the 200K threshold.

The rest of this note assumes option (1) — code as-is, with a Methods
sentence noting the flat-rate assumption. Neither the 106.6× narrative
nor the 213× narrative weakens the paper's argument (both are large);
this is about accuracy of the accounting, not the qualitative claim.

## 5. Qwen — time-based conversion

Qwen is self-hosted (vLLM on the institution's NAS); the raw `cost_usd`
recorded during benchmarking is $0 because there is no per-token API
fee. To make the row comparable, `scripts/qwen_cost_convert.py` post-
processes each `run_qwen_*_.json` and writes new fields:

- `per_step[i].effective_cost_usd`
- `backend.mean_cost_usd_effective`
- `backend.total_cost_usd_effective`

using:

```
effective_cost_usd = (latency_sec / 3600) * hourly_rate
hourly_rate        = CLOUD_RATES[gpu_type] * num_gpus
```

with `CLOUD_RATES` set to Lambda Labs 2026-07 published on-demand
rates (from the script's constants):

| GPU type       | $/h per GPU |
|---|---|
| a100-80gb      | 1.29        |
| h100-80gb      | 2.49        |
| a6000-48gb     | 0.80        |
| l40s-48gb      | 1.00        |

The v2 unified2 numbers use the default `--gpus 4 --gpu-type a100-80gb
→ hourly_rate = $5.16/h`. `scripts/compute_table1_sd.py` and
`scripts/build_final_table.py` both prefer `mean_cost_usd_effective`
over the raw `mean_cost_usd` for Qwen rows.

**Caveats stamped by the script itself** (from its own preamble):

- Hardware assumption is TENTATIVE — pending confirmation of the actual
  NAS GPU config. Downstream numbers hinge on this.
- The formula treats wall-clock latency as billable time. It therefore
  attributes idle time to cost, which over-estimates the true amortized
  cost when the same node is serving other queries in parallel.

## 6. Methods paragraph draft (English)

> **Cost accounting.** For cloud APIs (Gemini, Claude, GPT-4o), the
> per-step cost is computed as
> `input_tokens × input_rate_per_M + output_tokens × output_rate_per_M`,
> using the vendor's published 2026-07 per-1M-token base rates: Gemini
> 2.5 Pro \$1.25 / \$10.00 (input / output); Claude Sonnet 4.6 \$3.00 /
> \$15.00; GPT-4o \$2.50 / \$10.00. Base rates are applied uniformly;
> no prompt-cache discount is credited, and for the Gemini long-context
> baseline we report costs at the ≤200K-token base rate rather than the
> \>200K tier price — the alternative tier accounting would raise
> long-context per-step cost by 2× (from $0.283 to $0.567) and the cost
> ratio to full_system from 106.6× to ~213×. Qwen3-235B-Instruct is
> self-hosted (vLLM on 4× A100 80GB) and incurs no per-token fee; to
> make it comparable, we report an effective per-step cost of
> `latency × on-demand cloud A100 rate`, using Lambda Labs' 2026-07
> published rate of \$1.29/h per A100 80GB × 4 GPUs = \$5.16/h. This is
> a wall-clock-based upper bound: the same node serving parallel
> queries would prorate this figure downward.

## 7. Summary of findings

| Finding | Status |
|---|---|
| $283.45m / step long_context reproduces from stored token counts × flat $1.25/M input | Confirmed |
| 106.6× ratio is arithmetically consistent with the flat-rate accounting | Confirmed |
| Gemini long-context >200K tier surcharge NOT applied in code | Flagged — needs Methods sentence or recomputation |
| Prompt caching NOT credited on any backend | Flagged — needs Methods sentence |
| Qwen cost via time × hourly rate; hardware config still tentative | Flagged in script preamble; user confirmation pending |
