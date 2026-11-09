# GeoLens

GeoLens is a screen-aware guidance assistant for geoscience desktop software.
The user types a goal sentence and shares the screen; at every step a
vision–language model reads the screenshot, a workflow graph built from the
software manual locates the step the user is at, and a language model returns
the single next action in the user's language. Only the knowledge store
(vector index and workflow graphs) is software-specific: the same code and
settings ran on OpendTect 7.0.9 and QGIS 3.44.

This repository accompanies the manuscript

> Yu J, Yoon D. *GeoLens: a screen-aware guidance assistant for geoscience
> desktop software built from manual-derived workflow graphs.*
> Department of Energy and Resources Engineering, Chonnam National University.

It contains the code, the 13 workflow graphs, the benchmark scenarios and
screenshots, the pre-registration document and the raw run logs behind every
number in the paper.

## Contents

1. [What is released](#1-what-is-released)
2. [How GeoLens works](#2-how-geolens-works)
3. [Provenance: Screen Vision](#3-provenance-screen-vision)
4. [Installation](#4-installation)
5. [Configuration](#5-configuration)
6. [Running the desktop application](#6-running-the-desktop-application)
7. [Building a knowledge store](#7-building-a-knowledge-store)
8. [Benchmark](#8-benchmark)
9. [Repository structure](#9-repository-structure)
10. [Superseded material kept for provenance](#10-superseded-material-kept-for-provenance)
11. [Data and licences](#11-data-and-licences)
12. [Citation](#12-citation)

---

## 1. What is released

| Item | Location | Notes |
|---|---|---|
| Step pipeline, desktop app, benchmark harness | `api/`, `app/`, `components/`, `hooks/`, `lib/`, `scripts/` | Python 3.12 + Next.js 13 |
| 13 workflow graphs (93 nodes, 82 edges) | `data/workflows/*.json` | OpendTect 7 (4 evaluated + 3 distractors), QGIS 6 (4 + 2) |
| 8 benchmark scenarios of the paper (5 development, 3 test) | `data/eval/scenarios/*.json` | see §8.1; four further legacy scenarios are explained in §10 |
| Benchmark screenshots | `data/eval/screenshots/<scenario>/` (JPEG used by the harness), `data/eval/study4/originals_png/` (24 unmodified test-set PNGs) | window captures, about 1920×1030 px |
| Screen ground truth and its review | `data/eval/study4/gt_review_session/`, `data/eval/study4/GT5_final_applied_log.md` | drafted by gemini-2.5-pro, reviewed, frozen before the tag |
| Identifier alignment log (K1) | `data/eval/study4/K1_signature_log.md` | 8 of 24 test-set nodes, strings only |
| Pre-registration | `data/eval/study4/study5_pre_registration_DRAFT.md` | frozen by tag `study5-prereg-signed`; the file name is the one it had when written |
| Main benchmark run logs (60 sessions) | `data/eval/results/run_<gen>_study5_<software>_r<rep>_<timestamp>.json` | `gen` ∈ gemini, claude, gpt; `software` ∈ opendtect, qgis |
| Exploratory `linked_chunks` run logs (60) | `data/eval/results/run_<gen>_study5x_<software>_r<rep>_<timestamp>.json` | |
| Verdicts and re-scorings | `data/eval/results/verdict_study5.md`, `verdict_study5x.md`, `rescore_strict_study5.md` | |
| Methodology audit trail | `data/eval/results/methodology_audit_trail.md` | chronological record of every deviation and decision |

Not included: the manual PDFs, the ChromaDB indexes and the manual-figure
cache (see §7 and §11).

## 2. How GeoLens works

**Knowledge store** (built once per software package)

- *Vector index.* The manual PDF is split into 800-token chunks with a
  100-token overlap, embedded with `BAAI/bge-m3` and stored in ChromaDB
  (OpendTect manual: 467 chunks; QGIS Training Manual: 745 chunks).
- *Workflow graphs.* One JSON graph per manual procedure. Nodes are the
  screen states the user sees, edges are the actions that move between them.
  Each node carries screen identifiers (`visual_signature`: expected dialog
  title, UI elements, keywords) and the ids of the three manual chunks closest
  to it (`linked_chunks`). Drafts are written by an LLM from the section text
  and figure OCR; only identifier wording is corrected afterwards.

**Step pipeline** (runs for every screenshot; `api/services/guide_pipeline.py`)

1. *Screen reading.* `gemini-2.5-flash` extracts window title, menus, buttons,
   field labels and values verbatim into a structured list.
2. *Routing.* Candidates = the 5 nodes with the highest embedding similarity
   to the screen text + up to 3 nodes whose manual figures `open-clip ViT-B/32`
   matches to the screenshot + graph neighbours of the previous node (2 hops).
   The same VLM reranks them; below confidence 0.7 no node is chosen. Three
   model-free rules then correct the pick from session history: R1 (stay in
   the procedure in progress on identical dialog titles), R2 (advance when the
   previous instruction covered the outgoing edge and the screen changed),
   R3 (advance up to 3 hops when a successor-only keyword or dialog is visible).
3. *Context assembly* (`CONTEXT_ASSEMBLY=v8`). 3,900 characters of manual
   text (3 × 800 from the node's linked chunks + 1,500 from a vector search
   with the goal sentence) plus the structure block: the current screen state,
   the one incoming and three following edges written as
   "action → resulting screen", and a usage rule. If routing chose no node,
   the 3,900 characters are filled by vector search alone (fallback).
4. *Instruction generation.* Context + screenshot + goal + up to six previous
   instructions go to the generator (`gemini-2.5-pro` by default;
   `claude-sonnet-4-6` and `gpt-4o` were benchmarked), which outputs one action.

All routing and assembly knobs are environment variables; their defaults are
the values frozen for the benchmark (`scripts/study2_env.sh`,
`scripts/study4_env.sh`).

## 3. Provenance: Screen Vision

The desktop front end started from [Screen Vision](https://github.com/r-muresan/screen.vision)
(MIT), an open-source web application in which a VLM reads the shared screen
and a language model shows step-by-step instructions from the goal and the
previous instructions. GeoLens keeps its screen-sharing hook, pixel-diff
change detection, picture-in-picture instruction panel, SSE stream reader and
the `step` / `check` / `help` / `coordinates` request structure. Screen Vision
has no software knowledge beyond the model's prior knowledge and does not
track the user's position in a procedure; everything in §2 (knowledge store,
routing, context assembly) and §8 (benchmark harness) is new. The derived
files and the original licence text are listed in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## 4. Installation

Requires **Python 3.12** and **Node.js 18+**. Developed and evaluated on
Windows 11; the servers also run on macOS/Linux.

```bash
git clone https://github.com/jiyun917/GeoLens.git
cd GeoLens

python -m venv .venv
.venv/Scripts/activate            # Windows (Git Bash / PowerShell)
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
pip install PySide6               # only for the desktop window (launcher_desktop.py)

npm install
```

First use downloads the `BAAI/bge-m3` weights (about 2.3 GB) and the
open-clip ViT-B/32 weights. No GPU is required; all generators are API models.

## 5. Configuration

```bash
cp .env.example .env.local        # then fill in the keys
```

`.env.local` must exist **before** the servers start; the pipeline reads its
knobs at import time and `uvicorn --reload` does not watch `.env` files.

| Variable | Needed for |
|---|---|
| `GEMINI_API_KEY` | required: screen reading, reranking, default generator, target coordinates |
| `ANTHROPIC_API_KEY` | Claude Sonnet 4.6 generator (benchmark; desktop fallback), claude-haiku judge |
| `OPENAI_API_KEY` | GPT-4o generator (benchmark only) |
| `CHROMADB_PATH` | ChromaDB directory; the paper's index is `./data/chromadb_v4` |
| `EMBED_MODEL` | `BAAI/bge-m3` (paper); any sentence-transformers model works for a new index |
| `GEOLENS_SOFTWARE_ID` | `opendtect` or `qgis`: which software's graphs routing searches |
| `NEXT_PUBLIC_API_URL` | backend URL for the frontend (default `http://127.0.0.1:8000/api`) |

Embeddings are computed locally, so ingestion needs no API key.

## 6. Running the desktop application

```bash
npm run dev                       # Next.js on http://localhost:3010 + FastAPI on :8000
# or
python launcher_desktop.py        # PySide6 window; starts both servers itself (frontend on :3000)
```

In the app: upload the manual PDF once (§7), type a goal sentence, start
screen sharing, and the GeoLens panel shows the first instruction. The panel is
an always-on-top window excluded from capture. Under the instruction is a crop
of the screenshot around the predicted target (a separate `gemini-2.5-pro`
call; its accuracy was not measured). When the screen changes (pixel
differences checked every 200 ms) the next screenshot is captured and the next
instruction requested; **Done** advances manually and **Pause** suspends
detection. Typing a question answers it on the basis of the current screen and
the manual without advancing the step. The session ends when the generator
declares completion.

Endpoints: `POST /api/step` (instruction, SSE), `/api/check` (step completion),
`/api/help` (follow-up question), `/api/coordinates` (target location),
`/api/manual/*` (ingestion), `/api/workflow/*` (graphs), `/api/rag/route`
(routing only).

## 7. Building a knowledge store

The manuals are not redistributed (§11). To rebuild the OpendTect or QGIS
store, or to add a new software package:

**7.1 Vector index (bge-m3, as in the paper)**

```bash
CHROMADB_PATH=./data/chromadb_v4 EMBED_MODEL=BAAI/bge-m3 OCR_FIGURES=1 \
  .venv/Scripts/python.exe scripts/reindex_v4.py --manual-id <manual_id> --pdf <manual.pdf>
```

`OCR_FIGURES=1` runs Gemini Vision OCR on figure-heavy pages (about 15–25 min
for the 454-page OpendTect manual on a 4-core CPU). The manual ids used by the
released graphs are `645b7cdf2690408da843b9ce63c52d5b` (OpendTect) and
`bf2804feea57434bb79b749134ed1df0` (QGIS).

**7.2 Manual-figure cache (vision candidate source)**

`scripts/reindex_v4.py` builds the text index only. The figure cache
(`data/manual_images/`, gitignored, about 160 MB) and its open-clip index are
produced by the standard ingestion path, i.e. uploading the PDF in the UI
(`POST /api/manual/upload`) or `scripts/reindex_manual.py`. That path needs
`pip install pymupdf` (AGPL-3.0; see `requirements.txt`). Without the cache,
routing still runs with the embedding and graph-neighbour candidates.

**7.3 Workflow graphs**

Graphs are JSON files in `data/workflows/` (schema: `workflow_id`, `name`,
`software_id`, `manual_reference`, `authoring`, `nodes[]`, `edges[]`; see any
released graph). The three test-set graphs were drafted from manual text only
by `scripts/study4_author.py`, before any screenshot was captured. After a
graph is written or an index rebuilt, link each node to its chunks
(`api/services/chunk_mapper.py`; `scripts/relink_chunks_v4.py` shows the
batch form) — the released `linked_chunks` ids resolve only against the
authors' `chromadb_v4` collections, so a rebuilt index requires re-linking.
`scripts/preflight_check.py` verifies that every node has resolvable links,
every edge is well-formed and the scenario files are complete.

## 8. Benchmark

### 8.1 Design (as reported)

- **Harness.** `api/services/bench_runner.py` replays pre-captured
  screenshots through the same routing and context-assembly code as the
  desktop app, with the same session history (last confirmed node,
  instructions issued, previous screen reading), and scores the instructions
  automatically. It does not measure recovery after a wrong instruction or
  user completion time.
- **Scenarios (Table 2 of the paper).** Development set, used while designing
  the system: `opendtect__fault_sticks__01` (9 steps),
  `opendtect__horizon_autotrack__01` (7), `opendtect__horizon_2dviewer__01` (9),
  `qgis__rule_classification__01` (10), `qgis__reclassify_raster__01` (9).
  Test set, written from the manual after the system was frozen:
  `opendtect__spectral_decomp__01` (9), `qgis__custom_projection__01` (9),
  `qgis__aspect_north__01` (6). The test-set files used by the run scripts are
  the copies in `data/eval/scenarios/.study5_test_opendtect/` and
  `.study5_test_qgis/`.
- **Conditions** (`api/services/bench_backends.py`). Prespecified:
  `full_system` (GeoLens), `vanilla_budget` (vector search with the goal
  sentence, same 3,900 characters, no graph), `no_rag` (goal + screenshot
  only). Exploratory, run after the main results were seen: `vanilla_vector`
  (all vector results, no character limit) and `linked_chunks` (GeoLens
  routing and manual text, structure block removed).
- **Generators.** `gemini-2.5-pro`, `claude-sonnet-4-6`, `gpt-4o`;
  temperature 0.2; 10 replicates of every scenario session per generator and
  condition.
- **Metrics.** Step accuracy (model-free keyword/pattern match, scorer v6,
  `api/services/evaluation.py`), hallucination rate (label found neither in the
  screen ground truth nor in the relevant manual section), cost and latency per
  step. Two re-scorings: a strict all-keywords criterion
  (`scripts/rescore_strict_study5.py`) and two LLM judges (`claude-haiku-4-5`,
  `gemini-2.5-flash`; `api/services/bench_judge.py`), whose per-backend
  `judge_step_accuracy` is stored inside each run JSON.
- **Statistics.** Permutation test stratified by generator (10,000
  permutations), Holm correction over the two prespecified comparisons;
  `scripts/stats_stratified.py`.
- **Pre-registration.** Analysis plan, scoring rules, predictions, code and
  graphs were fixed in `data/eval/study4/study5_pre_registration_DRAFT.md` and
  frozen by the annotated tag `study5-prereg-signed` (commit `5be5a78`,
  2026-09-28T19:14:20Z) before the first main-run log
  (`run_claude_study5_opendtect_r1_20260928T191425.json`). Later tags:
  `study5-complete` (`72cb171`, main run and verdict), `study5x-complete`
  (`030fc71`, exploratory `linked_chunks` run). The tags are annotated, not
  GPG-signed; "signed" refers to the pre-registration document.

### 8.2 Results (test set, mean of 10 replicates; Table 3 of the paper)

| Generator | GeoLens | vanilla_budget | vanilla_vector | no_rag | linked_chunks |
|---|---|---|---|---|---|
| Gemini 2.5 Pro | **0.963** | 0.780 | 0.859 | 0.835 | 0.819 |
| Claude Sonnet 4.6 | **1.000** | 0.922 | 0.967 | 0.848 | 0.928 |
| GPT-4o | **0.959** | 0.889 | 0.867 | 0.752 | 0.896 |

GeoLens vs vanilla_budget: direction 3/3, stratified Δ = +0.11, raw p = 0.0001,
Holm-adjusted p = 0.0002. Latency with GeoLens was 14–25 s per step after the
first step (two auxiliary calls + candidate selection + generation); GPT-4o
under GeoLens mentioned an off-screen label at 32 of 240 steps (hallucination
rate 0.137). Full tables, per-scenario breakdowns and routing statistics:
`data/eval/results/verdict_study5.md`, `verdict_study5x.md`,
`rescore_strict_study5.md`.

### 8.3 Reproduction

Prerequisites: both indexes built as in §7 at `./data/chromadb_v4` with the
graphs re-linked, `.env.local` with the three generator keys, and a clean
working tree for `api/`, `scripts/`, `data/workflows/`, `data/eval/scenarios/`
(the preflight check enforces this).

```bash
source scripts/study2_env.sh && source scripts/study4_env.sh   # benchmark pins

# Pre-run integrity check (read-only; the run scripts call it themselves)
.venv/Scripts/python.exe scripts/preflight_check.py \
  --scenarios data/eval/scenarios/.study5_test_opendtect \
  --expect GEOLENS_SCORER=v6 CONTEXT_ASSEMBLY=v8 ROUTER_SESSION_STICKY=1 \
           ROUTER_HISTORY_ADVANCE=1 ROUTER_SCREEN_ADVANCE=1 GEN_PROMPT_VERSION=v3

# Main matrix: 3 generators x {no_rag, vanilla_budget, vanilla_vector, full_system}
#              x 3 test scenarios x 10 replicates (two passes: OpendTect, QGIS)
MODELS=gemini,claude,gpt REPS=10 bash scripts/run_study5.sh
.venv/Scripts/python.exe scripts/verdict_study5.py          # -> verdict_study5.md

# Exploratory linked_chunks condition on the same test set
MODELS=gemini,claude,gpt REPS=10 bash scripts/run_study5x.sh
.venv/Scripts/python.exe scripts/verdict_study5x.py         # -> verdict_study5x.md

# Strict re-scoring of the existing run logs (no API calls)
.venv/Scripts/python.exe scripts/rescore_strict_study5.py   # -> rescore_strict_study5.md
```

The main run cost about USD 32 in API fees at 2026-09 prices (Claude 13,
Gemini 11, GPT 8; actual billing about 1.5× the recorded estimate) and took one
night with the three generators running in parallel. A smoke test on one
generator and one replicate is `MODELS=gemini REPS=1 bash scripts/run_study5.sh`.

Reviewers without the manuals can exercise the pipeline mechanics on the
synthetic corpus in `data/eval/dummy_manuals/`:

```bash
.venv/Scripts/python.exe scripts/verify_dummy_pipeline.py --skip-generate   # no API key
.venv/Scripts/python.exe scripts/verify_dummy_pipeline.py                   # needs GEMINI_API_KEY
```

### 8.4 Language

The benchmark scenarios are authored in Korean (`"language": "ko"` in the
scenario JSON) and the generators answered in Korean; the completion sentinel
is the Korean word for "Done". The scorer is language-neutral (labels are
matched as written on screen) and the desktop app has a language selector.

## 9. Repository structure

```
GeoLens/
├── api/
│   ├── index.py                 # FastAPI app
│   ├── routers/                 # task.py (/api/step, /check, /help, /coordinates), manual.py, workflow.py
│   └── services/
│       ├── embedder.py          # chunking (800/100), bge-m3 embeddings, figure cache hook
│       ├── vectorstore.py       # ChromaDB client
│       ├── parser/              # PDF (pdfplumber + pypdf), URL, GitHub ingestion
│       ├── image_extractor.py   # manual figures (PyMuPDF, optional)
│       ├── visual_matcher.py    # open-clip ViT-B/32 screenshot-to-figure matching
│       ├── workflow_graph.py    # graph loader (WORKFLOW_DATA_PATH)
│       ├── chunk_mapper.py      # node -> top-3 chunk linking
│       ├── guide_pipeline.py    # screen reading, routing (R1-R3), context assembly
│       ├── bench_backends.py    # benchmark conditions
│       ├── bench_runner.py      # screenshot replay harness
│       ├── evaluation.py        # scorer (v6), hallucination check
│       └── bench_judge.py       # LLM judges
├── app/, components/, hooks/, lib/   # Next.js front end (see THIRD_PARTY_NOTICES.md)
├── launcher_desktop.py          # PySide6 desktop window
├── data/
│   ├── workflows/               # 13 workflow graphs (the routing pool)
│   ├── eval/
│   │   ├── scenarios/           # scenario JSONs (+ SCHEMA.json; .study5_test_* = test-set copies)
│   │   ├── screenshots/         # per-scenario step JPEGs used by the harness
│   │   ├── study4/              # test-set originals (PNG), GT review, K1 log, pre-registration
│   │   ├── study2/, study3/     # earlier development-set GT reviews
│   │   ├── dummy_manuals/       # synthetic corpus for the pipeline check
│   │   └── results/             # run logs, verdicts, re-scorings, audit trail
│   ├── chromadb_v4/             # (gitignored) bge-m3 index; build with scripts/reindex_v4.py
│   ├── manual_images/           # (gitignored) manual-figure cache
│   └── uploads/                 # (gitignored) manual PDFs
├── scripts/
│   ├── study2_env.sh, study4_env.sh   # benchmark pins
│   ├── preflight_check.py             # pre-run integrity check
│   ├── run_study5.sh, verdict_study5.py
│   ├── run_study5x.sh, verdict_study5x.py
│   ├── rescore_strict_study5.py, stats_stratified.py
│   ├── reindex_v4.py, relink_chunks_v4.py, study4_author.py
│   ├── verify_dummy_pipeline.py
│   └── secret_scan.py                 # pre-push credential scan
├── THIRD_PARTY_NOTICES.md
├── LICENSE                      # MIT
├── requirements.txt, package.json
└── .env.example
```

## 10. Superseded material kept for provenance

The repository also holds earlier development cycles whose numbers are **not**
the ones reported in the paper. They are kept so that the audit trail stays
complete, and should not be cited as results:

- `unified`, `unified2`, `unified3`, `unified4` and `v3` run logs
  (`data/eval/results/run_*_unified*`, `run_*_v3*`, `.archive_unified2/`,
  `archive_unified3_longctx/`): earlier matrices with a 4-generator ×
  7-backend design, a self-hosted Qwen backend (`QWEN_BASE_URL`,
  `scripts/qwen_cost_convert.py`), `graph_only` / `vision_only` /
  `state_path` / `long_context` conditions, and the `qgis__vector_buffer__01`
  portability pilot (`scripts/run_qgis_pilot.py`).
- `study2`, `study3`, `study4` runs and verdicts: the pre-registered
  development-set studies that fixed rules R1, R2 and R3 and the scorer.
- The four legacy scenarios `opendtect__survey_setup__01`,
  `opendtect__3d_visualization__01`, `opendtect__attribute_computation__01`
  and `qgis__vector_buffer__01`, and `data/eval/scenarios/excluded/`.
- `data/eval/results/pypdf_migration_audit.md` and
  `data/chromadb_pymupdf_reference/` (gitignored): the 2026-07 migration of the
  text parser from PyMuPDF to pdfplumber + pypdf, verified before the current
  index was built.
- `data/eval/results/_stale_*`, `discarded/`: replicates discarded during
  recovery from API outages, with the reason recorded in the audit trail.

## 11. Data and licences

- **Code**: MIT, see [`LICENSE`](LICENSE). Front-end files derived from
  Screen Vision carry its MIT notice, see
  [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
- **OpendTect manual** (*Introduction to OpendTect and OpendTect Pro Training
  Manual 7.0*, dGB Earth Sciences): not redistributed. Obtain it from dGB
  (<https://dgbes.com>); short excerpts appear in the run logs as retrieved
  context. The F3 Demo 2023 dataset and OpendTect 7.0.9 are free downloads.
- **QGIS Training Manual 3.44** (QGIS project,
  <https://docs.qgis.org/3.44/en/docs/training_manual/>): provided by the
  QGIS project under the GNU Free Documentation License 1.3 or later; the PDF
  is not redistributed here. QGIS 3.44 and the QGIS Training Data are free.
- **Screenshots, graphs, scenarios, screen ground truth, run logs**: released
  under the repository licence.
- Before pushing, run `.venv/Scripts/python.exe scripts/secret_scan.py`; it
  must report CLEAN.

## 12. Citation

```
Yu J, Yoon D. GeoLens: a screen-aware guidance assistant for geoscience
desktop software built from manual-derived workflow graphs. Manuscript.
Code: https://github.com/jiyun917/GeoLens
```

A DOI and BibTeX entry will be added on publication.
