# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project overview

GeoLens is a screen-aware guidance assistant for geoscience desktop software
(OpendTect, QGIS). The user types a goal and shares the screen; at every
step a VLM reads the screenshot, the workflow graph built from the software
manual locates the user's current step, and a generator LLM returns the
single next action. The desktop front end started from
[Screen Vision](https://github.com/r-muresan/screen.vision) (MIT; see
`THIRD_PARTY_NOTICES.md`). Only guide mode exists on this branch.

## Tech stack

- Frontend: Next.js 13.4, React 18, TypeScript, Tailwind, Zustand
- Backend: FastAPI (Python 3.12), ChromaDB, sentence-transformers (bge-m3),
  open-clip, google-genai, anthropic, openai
- Desktop wrapper: PySide6 (`launcher_desktop.py`)

## Commands

```bash
npm run dev                  # Next.js on :3010 + FastAPI on :8000 (.env.local must exist first)
npm run next-dev             # frontend only (:3010)
npm run fastapi-dev          # backend only (:8000, --reload on api/)
python launcher_desktop.py   # PySide6 window; starts both servers itself (frontend on :3000)
```

`uvicorn --reload` watches `.py` files only; restart `npm run dev` after
editing `.env.local`.

## Architecture (api/services)

- `embedder.py` — 800-token / 100-overlap chunking, bge-m3 embeddings
  (`EMBED_MODEL`), manual-figure cache via `image_extractor.py` (PyMuPDF)
- `vectorstore.py` — ChromaDB client; `CHROMADB_PATH` (benchmark index: `./data/chromadb_v4`)
- `workflow_graph.py` — loads `data/workflows/*.json` (`WORKFLOW_DATA_PATH`)
- `chunk_mapper.py` — links graph nodes to their top-3 manual chunks
- `visual_matcher.py` — open-clip ViT-B/32 screenshot-to-manual-figure matching
- `guide_pipeline.py` — step pipeline: screen reading (gemini-2.5-flash),
  routing (candidate pool, rerank, rules R1/R2/R3), context assembly (v8:
  3,900 characters of manual text plus the structure block)
- `bench_backends.py` / `bench_runner.py` / `evaluation.py` / `bench_judge.py` —
  benchmark harness, conditions, scorer (v6), LLM judges
- `api/routers/task.py` — `/api/step` (gemini-2.5-pro, Claude Sonnet 4.6 fallback),
  `/api/check`, `/api/help`, `/api/coordinates`

Routing and assembly knobs are environment variables whose defaults are the
study-5 pins (`scripts/study2_env.sh`, `scripts/study4_env.sh`).

## Rules

- Never start a paid benchmark run without `scripts/preflight_check.py` passing.
- `data/workflows/` must keep all 13 graphs (93 nodes, 82 edges).
- Do not edit scenarios, screen ground truth, or graphs that a tag froze
  (`study5-prereg-signed`, `study5-complete`, `study5x-complete`).
- Run `scripts/secret_scan.py` before any push.
