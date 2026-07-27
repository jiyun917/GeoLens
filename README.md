# GeoLens

GeoLens is an AI-powered, manual-grounded software guide for geoscience
software. A user uploads a technical manual (PDF), describes a goal,
shares their screen, and the system streams step-by-step instructions
grounded in the manual via hybrid retrieval (workflow-graph + vision +
vector RAG). The system was evaluated on the OpenDtect seismic-
interpretation package.

This repository accompanies the manuscript "GeoLens: hybrid retrieval
for manual-grounded software guidance in geoscience workflows"
(*Computers & Geosciences*, in submission). Its purpose is to make the
benchmark numbers, data, and pipeline reproducible from the README
alone.

## Table of contents

1. [Overview](#1-overview)
2. [Installation](#2-installation)
3. [API keys and configuration](#3-api-keys-and-configuration)
4. [Usage — guide mode](#4-usage--guide-mode)
5. [Benchmark reproduction](#5-benchmark-reproduction)
6. [Data availability and manual ingestion](#6-data-availability-and-manual-ingestion)
7. [Language policy](#7-language-policy)
8. [Parser migration note (PyMuPDF → pdfplumber + pypdf)](#8-parser-migration-note-pymupdf--pdfplumber--pypdf)
9. [Qwen self-hosted deployment](#9-qwen-self-hosted-deployment)
10. [Repository structure](#10-repository-structure)
11. [Citation](#11-citation)
12. [License](#12-license)

---

## 1. Overview

GeoLens exposes a single mode — **guide** — that walks a user through
a software workflow one step at a time. On each iteration the frontend
captures the user's screen, sends it with the goal and conversation
history to the backend, and the backend:

1. Routes the request to the closest workflow node in the hybrid graph
   (built at manual-ingest time from workflow-shape headings).
2. Retrieves manual context (vector similarity + graph-neighbor
   expansion + optional vision matching against manual figures).
3. Feeds the context and the current screenshot to the chosen LLM
   generator (Gemini 2.5 Pro by default; Claude / GPT-4o / Qwen
   selectable for benchmarking).
4. Streams the next instruction back as Server-Sent Events.

The system's contribution is the hybrid retrieval pipeline (workflow
graph + vector + vision) evaluated against the same LLM backbones with
weaker retrieval variants and a long-context zero-retrieval baseline.

Report and image-labeling modes present in other branches
(`conference`, `develop`) are **not part of the paper's scope**. Only
guide mode is retained on the `paper` and (post-merge) `main` branches.

## 2. Installation

Requires **Python 3.12** and **Node.js 18+**.

```bash
git clone https://github.com/jiyun917/GeoLens.git
cd GeoLens
git checkout main

# Backend (Python)
python -m venv .venv
.venv/Scripts/activate            # Windows PowerShell / Git Bash
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt

# Frontend (Next.js)
npm install
```

Approximate size of the Python + JS dependency tree: ~2.5 GB
installed. First-time embedding calls download the sentence-
transformers weights lazily (~600 MB, cached).

**Compute requirements**

- Development / interactive use: any modern CPU. No GPU required for
  the API-backed generators (Gemini, Claude, GPT-4o).
- Local Qwen benchmarking: see §9. The paper's Qwen numbers used
  4× RTX 6000 Ada 48 GB; smaller configurations are possible but not
  the ones we benchmarked.
- Disk: the chromadb index for the OpenDtect manual is ~1 GB. CLIP
  image cache adds ~160 MB. Synthetic-corpus scratch index is <5 MB.

## 3. API keys and configuration

Copy `.env.example` to `.env.local` and fill in real values:

```bash
cp .env.example .env.local
```

| Variable | Required for | Notes |
|---|---|---|
| `GEMINI_API_KEY`     | routing + vision + default generator | Required for both interactive use and benchmarking. |
| `OPENAI_API_KEY`     | embeddings + optional GPT-4o benchmark | Embeddings use `text-embedding-3-small`. |
| `ANTHROPIC_API_KEY`  | optional Claude benchmark             | Model: `claude-sonnet-4-6`. |
| `OPENROUTER_API_KEY` | optional Qwen-via-OpenRouter route    | Only if not using a self-hosted vLLM endpoint. |
| `CHROMADB_PATH`      | vector store location                 | Default `./data/chromadb`. |
| `GITHUB_TOKEN`       | optional private-repo ingest          | Required only for `POST /api/manual/github` with a private URL. |

`.env.local` is gitignored. The placeholder values in `.env.example`
match `scripts/secret_scan.py`'s allowlist so a clean clone scans
cleanly.

## 4. Usage — guide mode

Start both servers with:

```bash
npm run dev
```

This launches the FastAPI backend on port 8000 and the Next.js
frontend on port 3000. Open <http://localhost:3000>, upload a PDF
manual, enter a goal (e.g. *"Create a new 3D seismic survey"*),
start screen sharing, and the assistant will stream the next step at
each iteration.

Guide mode is the only mode exposed by this build. There is no report
route and no image-labeling UI.

## 5. Benchmark reproduction

The paper reports a **4 LLM generators × 7 backends (long_context on
Gemini only, yielding 25 model–backend cells) × 2 scenarios × 5
replicates = 1,000 evaluated step responses** matrix.

The four LLM generators are Gemini 2.5 Pro, Claude Sonnet 4.6, GPT-4o,
and Qwen3-235B-A22B-Instruct. The seven backends are `no_rag`,
`vanilla_vector`, `graph_only`, `vision_only`, `full_system` (the
proposed hybrid), `state_path`, and `long_context` (the last is
Gemini-only because the manual at ~226K tokens exceeds Claude Sonnet
4.6's 200K window, GPT-4o's 128K window, and the Qwen deployment's
vLLM `--max-model-len 32768` cap; see §9).

The two scenarios are `opendtect__survey_setup` and
`opendtect__3d_visualization`, each 4 steps.

### 5.1 Prepare the index

You need a chromadb index built from a real manual to reproduce the
paper numbers. Two paths:

- **Recommended**: build your own index from an OpendTect manual PDF
  (see §6.2). Building takes ~15–25 minutes on a 4-core CPU (dominated
  by Gemini Vision OCR calls for the manual's screenshot-heavy pages).
- **Byte-exact reference**: download the AGPL-licensed
  `chromadb_pymupdf_reference/` snapshot linked in the release
  description and mount it at `data/chromadb/`. This snapshot uses
  PyMuPDF 1.25.3 and reproduces the paper's numbers exactly. See §8
  for why the public code path uses the MIT-compatible parser instead.

### 5.2 Run the matrix

```bash
# Full v2 matrix — 4 models × 6 core backends × 2 scenarios × 5 reps
.venv/Scripts/python.exe scripts/run_all_models.py \
    --models gemini,claude,gpt,qwen --repeats 5 --tag unified2 \
    --backends no_rag vanilla_vector graph_only vision_only full_system state_path

# Long_context (Gemini only) — 5 replicates
bash scripts/longctx_r5_rerun.sh

# Aggregation and analysis
.venv/Scripts/python.exe scripts/build_final_table.py --tag unified2
.venv/Scripts/python.exe scripts/direction_consistency.py --tag unified2
.venv/Scripts/python.exe scripts/stats_unified.py --tag unified2

# Compact 25-cell Table 1 with sample SD on all 5 core metrics
.venv/Scripts/python.exe scripts/compute_table1_sd.py

# Pre-manuscript audits: stats corrections, cost basis, faithfulness
.venv/Scripts/python.exe scripts/stats_audit.py
.venv/Scripts/python.exe scripts/faithfulness_audit.py
```

Wall time: full matrix takes ~6–8 hours end-to-end, dominated by
Qwen wall-clock latency and API rate limits. Approximate cost at
2026-07 rates: ~USD $40 for the API portion (Qwen self-hosted; see
§9 for GPU-time accounting).

### 5.3 Sanity check without the real manual

For reviewers who cannot obtain the OpenDtect manual, `scripts/
verify_dummy_pipeline.py` runs the full pipeline (chunk → embed →
retrieve → generate) against a synthetic corpus committed under
`data/eval/dummy_manuals/`:

```bash
# Retrieval only (no LLM key required)
.venv/Scripts/python.exe scripts/verify_dummy_pipeline.py --skip-generate

# End-to-end (needs GEMINI_API_KEY)
.venv/Scripts/python.exe scripts/verify_dummy_pipeline.py
```

The script exits 0 on success and prints details of the retrieval and
generation steps on stderr for auditing.

## 6. Data availability and manual ingestion

### 6.1 OpenDtect manual

The OpenDtect manual is authored by dGB Earth Sciences and is not
redistributable here. Obtain it from the official OpenDtect
distribution channel (<https://dgbes.com>) and place the PDF at
`data/uploads/`.

### 6.2 Build your own index

```bash
.venv/Scripts/python.exe scripts/reindex_manual.py \
    --manual-id opendtect_v7 \
    --pdf data/uploads/OpendTect_User_Documentation_v7.pdf
```

Timing on the OpendTect 454-page manual, MIT-compatible pipeline:

- pdfplumber text extraction: ~3 minutes
- Gemini Vision OCR pass (279 image-heavy pages, 5 parallel workers):
  ~15 minutes wall time
- Chunking + `text-embedding-3-small` on 521 chunks: ~2 minutes
- Total end-to-end: **~20–25 minutes** on a 4-core CPU with a stable
  Gemini API connection

The resulting index (521 chunks, ~1 GB) is what the pdfplumber column
in the paper's benchmark was measured against.

### 6.3 Synthetic corpus

`data/eval/dummy_manuals/` contains three original short markdown
files intended for review-time reproducibility checks (see §5.3). They
are not a substitute for a real manual — they exercise the pipeline
mechanics, not the benchmark's ecological validity.

## 7. Language policy

All benchmark results were measured with **Korean-language prompts and
Korean scenario tags**, reflecting the target user population
(Korean geoscience practitioners). Both the interactive guide flow and
the benchmark harness feed Korean strings to the generator; the
underlying backend code is language-neutral, only the prompt templates
under `lib/prompts/` and the scenario JSONs under `data/eval/
scenarios/` are language-specific. An English-language extension is
left as future work.

## 8. Parser migration note (PyMuPDF → pdfplumber + pypdf)

**The paper's headline numbers were computed against a chromadb index
built with PyMuPDF 1.25.3.** PyMuPDF is licensed under AGPL-3.0, which
is incompatible with this repository's MIT distribution. The public
reproduction pipeline therefore uses **pdfplumber 0.11.10 (MIT)** for
text extraction and rendering, and **pypdf 6.14.2 (BSD-3-Clause)** for
the outline / table-of-contents traversal that pdfplumber does not
expose.

Full equivalence between the two indexes was audited before adopting
the migration. Summary:

- Chunk-boundary identity was rejected as structurally unmeetable
  (byte-non-identical parser outputs feed a fixed-size splitter — no
  amount of splitter tuning converges the two chunk sets).
- Instead, pre-registered end-to-end criteria: full_system Step Acc
  within reference ±1 SD; ablation ordering preserved
  (full_system ≥ vanilla on Step Acc and ≤ vanilla on Hall Rate);
  no pathological reversals (Loop Rate stays 0, Hall Rate < 2× ref).
- **Result on the pdfplumber index (Gemini × 5 replicates)**:
  full_system Step Acc **57.5±11.2%** (reference 60.0±10.5,
  within 1 SD); vanilla Step Acc **45.0±6.8%** — a 15pp drop from the
  reference 60.0, driven by vanilla_vector's greater sensitivity to
  chunk-boundary shifts than hybrid retrieval (which stabilises the
  choice via workflow-graph routing before vector similarity). Hall
  rate ordering preserved (full 2.5% < vanilla 5.0%). Loop Rate 0.
- **All pre-registered criteria PASS.** The paper's headline numbers
  stand as measured on the PyMuPDF reference; the MIT-distributed
  pdfplumber pipeline is statistically equivalent on the ablation-
  critical dimensions.

Full audit trail: `data/eval/results/pypdf_migration_audit.md`.

If you require byte-exact reproduction of the paper's numbers, mount
the released `chromadb_pymupdf_reference/` snapshot at
`data/chromadb/`; that route retains PyMuPDF as a build-time
dependency and is not the recommended reproduction path.

## 9. Qwen self-hosted deployment

Qwen3-235B-A22B-Instruct (INT4 GPTQ) was served for the benchmark on
an institution-hosted node:

- Hardware: **4× NVIDIA RTX 6000 Ada 48GB**
- Serving engine: vLLM, tensor-parallel 4
- `--max-model-len 32768`
- Endpoint pattern: `http://<host>:28000/v1` (OpenAI-compatible)

**Qwen cost accounting.** Because there is no per-token API fee,
`scripts/qwen_cost_convert.py` reports Qwen cost primarily as
**GPU-time per step** (`latency × N_GPU`), with a dollar conversion
provided for comparability against the API models:

- Reference rate: **$0.84 per GPU-hour for RTX 6000 Ada 48GB** on
  RunPod Secure Cloud (<https://www.runpod.io/pricing>, queried
  2026-07-27). Node rate at TP=4: `$0.84 × 4 = $3.36/hr`.
- Per-step cost = `(latency_sec / 3600) × $3.36/hr`.
- Backend-to-backend Qwen cost **ratios are invariant** to the chosen
  hourly rate; only absolute scale depends on it.

The 32,768-token serving cap is the reason Qwen is excluded from the
`long_context` ablation (the OpenDtect manual is ~226K tokens, well
above the deployment's context budget). Detailed cost derivation and
the reproduction script are in `data/eval/results/cost_basis.md` §5.

## 10. Repository structure

```
GeoLens/
├── api/                        # FastAPI backend (Python 3.12)
│   ├── routers/                # /api/{step,check,help,coordinates,manual}
│   └── services/
│       ├── parser/             # PDF/URL/GitHub ingest (pdfplumber + pypdf)
│       ├── embedder.py         # chunking + text-embedding-3-small
│       ├── vectorstore.py      # ChromaDB PersistentClient wrapper
│       ├── rag.py              # hybrid retrieval (vector + graph + vision)
│       ├── guide_pipeline.py   # request routing (workflow graph)
│       └── bench_backends.py   # 7 backend implementations + pricing table
├── app/, components/, lib/     # Next.js frontend (guide mode only)
├── data/
│   ├── uploads/                # (gitignored) user-supplied PDFs
│   ├── chromadb/               # (gitignored) vector index
│   ├── manual_images/          # (gitignored) CLIP cache; regenerate with scripts/
│   ├── workflows/              # hand-authored + auto-mapped workflow graphs
│   └── eval/
│       ├── scenarios/          # labeled scenario JSONs (survey_setup, 3d_visualization, ...)
│       ├── dummy_manuals/      # synthetic corpus for review-time reproducibility check
│       └── results/            # benchmark run logs, aggregated tables, audit docs
├── scripts/                    # bench runners, aggregators, migration audits
│   ├── run_all_models.py       # main matrix driver
│   ├── build_final_table.py    # per-model tables
│   ├── compute_table1_sd.py    # compact 25-cell Table 1
│   ├── stats_audit.py          # Table 2 corrections (Bonferroni/Holm/CI)
│   ├── faithfulness_audit.py   # Table 3 direction-consistency reproduction
│   ├── qwen_cost_convert.py    # Qwen effective-cost conversion
│   ├── secret_scan.py          # pre-push credential scanner
│   ├── reindex_manual.py       # full production reindex path
│   └── verify_dummy_pipeline.py # review-time end-to-end sanity check
├── LICENSE                     # MIT
├── README.md                   # (this file)
├── .env.example                # documented placeholder keys
├── requirements.txt            # pinned Python deps
└── package.json                # Next.js deps + npm run dev scripts
```

### Pre-push secret scan

Before pushing, run:

```bash
.venv/Scripts/python.exe scripts/secret_scan.py
# or, if installed:
gitleaks git . --log-opts="--all"
```

Both should report `CLEAN` on the current tree.

## 11. Citation

```
[Citation placeholder — to be updated on acceptance with DOI and
BibTeX entry.]
```

## 12. License

MIT — see [`LICENSE`](LICENSE).
