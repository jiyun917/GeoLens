# Cost basis documentation

Traces the code path that produces `mean_cost_usd` / `total_cost_usd` in
every `run_*_r*_*.json`, records the pricing constants and their source
date, verifies the reported `$283.45m` per-step cost for Gemini
long_context arithmetically, documents the confirmed Qwen serving
hardware and its per-step GPU-time-based cost conversion, and flags one
remaining assumption the manuscript should acknowledge (Gemini
long-context tier pricing).

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

## 5. Qwen — confirmed hardware and time-based conversion

### 5.1 Confirmed serving hardware (2026-07-27)

The vLLM endpoint used for all Qwen benchmark runs is:

| Item | Value |
|---|---|
| Model                | Qwen3-235B-A22B-Instruct |
| Quantization         | GPTQ int4 |
| Serving engine       | vLLM, TP=4 |
| Max model length     | 32,768 tokens (vLLM `--max-model-len` at bench time) |
| Hardware             | **4× NVIDIA RTX 6000 Ada 48GB** |
| Endpoint             | `http://168.131.141.77:28000/v1` |

The earlier working assumption of `A100 80GB × 4` was an over-estimate of
the GPU tier and has been retired.

**Consequence for the long-context evaluation.** The 32,768-token serving
cap is well below the ~226K-token OpenDtect manual, so Qwen cannot host
the long_context ablation regardless of the model's advertised 128K
theoretical maximum. Long_context is Gemini-only for this reason (in
addition to Claude/GPT-4o windows also falling short of 226K).

### 5.2 Primary reporting unit — GPU-time / step

The natural, deployment-neutral cost unit for a self-hosted model is
`latency × N_GPU` (GPU-seconds per step). This is what the benchmark
actually measures and what would be paid by a reproducer regardless of
whether they rent, own, or borrow the GPUs.

The 5-replicate per-backend Qwen numbers (latency mean ± sample SD
carried over from `table1_full_sd.md`, converted to 4-GPU-seconds):

| Backend        | Latency/step (s) | GPU-time/step (4-GPU-s) | GPU-hours/step (4-GPU) |
|---|---|---|---|
| no_rag         |  7.3±1.1         |  29.2±4.4               | 0.00811 |
| vanilla_vector | 42.2±71.4        | 168.8±285.6             | 0.04689 |
| graph_only     | 13.9±2.1         |  55.6±8.4               | 0.01544 |
| vision_only    | 11.0±1.5         |  44.0±6.0               | 0.01222 |
| full_system    | 30.9±2.1         | 123.6±8.4               | 0.03433 |
| state_path     | 29.9±1.5         | 119.6±6.0               | 0.03322 |

Ratios between backends are preserved under any linear time→dollar
conversion (verified in §5.4 below).

### 5.3 Dollar conversion — RunPod RTX 6000 Ada Secure Cloud

Conversion is done by `scripts/qwen_cost_convert.py` using:

```
effective_cost_usd = (latency_sec / 3600) × hourly_rate
hourly_rate        = CLOUD_RATES[gpu_type] × num_gpus
```

**Rate**: $0.84 per GPU-hour for RTX 6000 Ada 48GB (Secure Cloud tier).
**Source**: RunPod public pricing page, https://www.runpod.io/pricing
(queried 2026-07-27). **Node rate at TP=4**: $0.84 × 4 = **$3.36/hr**.

Applied to the latency table above:

| Backend        | Effective cost/step (mean ± SD) |
|---|---|
| no_rag         |  $6.86 ± 0.99 m  |
| vanilla_vector | $39.36 ± 66.64 m |
| graph_only     | $12.98 ± 1.95 m  |
| vision_only    | $10.29 ± 1.40 m  |
| full_system    | $28.85 ± 1.96 m  |
| state_path     | $27.94 ± 1.43 m  |

*(m = milli-USD per step, e.g. `6.86m` = $0.00686.)*

### 5.4 Old vs new Qwen Cost table (ratio-invariance check)

The prior report used the A100 80GB × 4 assumption ($5.16/hr node).
Corrected to RTX 6000 Ada × 4 ($3.36/hr node), all absolute Qwen cost
values scale by 3.36/5.16 = **0.6512**. Backend-to-backend ratios are
unchanged.

| Backend        | Old cost/step ($m) | New cost/step ($m) | Ratio to full_system (old / new) |
|---|---|---|---|
| no_rag         | 10.53±1.52   |  6.86±0.99   | 0.238 / 0.238 |
| vanilla_vector | 60.45±102.33 | 39.36±66.64  | 1.365 / 1.364 |
| graph_only     | 19.94±3.00   | 12.98±1.95   | 0.450 / 0.450 |
| vision_only    | 15.80±2.15   | 10.29±1.40   | 0.357 / 0.357 |
| full_system    | 44.30±3.00   | 28.85±1.96   | 1.000 / 1.000 |
| state_path    | 42.90±2.20   | 27.94±1.43   | 0.969 / 0.968 |

Full_system-to-vanilla, full_system-to-no_rag, and all other pairwise
Qwen cost ratios reproduce to the third decimal — the ratio-invariance
is arithmetically exact and any 3rd-decimal drift is rounding on the
`round(_, 6)` step.

**Consequence for the paper's Qwen narrative** (in §Results and
Discussion of the manuscript, where the current text reads
`no_rag $10.53m 최저, full $44.30m`): update to the new absolute
figures (`$6.86m` and `$28.85m` respectively). All directional
conclusions ("cost tracks latency", "auxiliary calls add cost")
carry over unchanged. Table 1 Qwen Cost row and the narrative doc
paragraphs P19 (vanilla outlier note: `$60.45m` → `$39.36m` and
`$14.4m` → `$9.4m`) and P31 (`$10.53` / `$44.30`
→ `$6.86` / `$28.85`) have been re-generated by
`scripts/compute_table1_sd.py` and `scripts/update_docx_with_sd.py`.

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
> long-context per-step cost by 2× (from \$0.283 to \$0.567) and the
> cost ratio to full_system from 106.6× to ~213×.
>
> **Qwen self-hosted cost accounting.** Qwen3-235B-A22B-Instruct
> (GPTQ int4) was served via vLLM on **4× NVIDIA RTX 6000 Ada 48GB**
> (tensor-parallel 4, `max-model-len` 32,768). Because there is no
> per-token API fee, we report the effective cost per step as
> `latency_sec × node_hourly_rate`, using RunPod's published Secure
> Cloud rate for the same GPU model queried 2026-07-27
> (\$0.84 per GPU-hour × 4 GPUs = \$3.36/hr for the node). Backend-to-
> backend Qwen cost ratios are invariant to this hourly rate; only the
> absolute scale depends on it. The 32,768-token serving limit is why
> Qwen is excluded from the long_context ablation — the manual is
> ~226K tokens, well above the deployment's context budget.

## 7. Summary of findings

| Finding | Status |
|---|---|
| $283.45m / step long_context reproduces from stored token counts × flat $1.25/M input | Confirmed |
| 106.6× ratio is arithmetically consistent with the flat-rate accounting | Confirmed |
| Gemini long-context >200K tier surcharge NOT applied in code | Flagged — needs Methods sentence or recomputation |
| Prompt caching NOT credited on any backend | Flagged — needs Methods sentence |
| Qwen serving hardware confirmed: 4× RTX 6000 Ada 48GB, TP=4, GPTQ int4, max-model-len 32,768 | Confirmed (previously TENTATIVE assumption of A100×4 retired) |
| Qwen cost primary unit = GPU-time/step; USD via RunPod RTX 6000 Ada Secure Cloud $0.84/GPU-hr | Confirmed |
| Qwen 32K served context is the reason long_context is Gemini-only (Qwen 이론 128K 표기는 서빙 실측과 다름) | Confirmed |
