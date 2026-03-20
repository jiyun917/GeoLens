# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GeoLens is an AI-powered software guide. Users upload manuals (PDF/URL/GitHub source code), describe a goal, share their screen, and AI provides step-by-step instructions grounded in the manual content via RAG. Based on [screen.vision](../screen.vision/) architecture.

## Tech Stack

- **Frontend**: Next.js 13.4, React 18, TypeScript, Tailwind CSS 3.4, Zustand, shadcn/ui
- **Backend**: FastAPI (Python 3.12), ChromaDB, OpenAI API, Gemini API
- **Package Manager**: npm (frontend), uv (Python)

## Commands

```bash
# Development (runs both Next.js on :3000 and FastAPI on :8000)
npm run dev

# Frontend only
npm run next-dev

# Backend only
npm run fastapi-dev
# or: uv run python -m uvicorn api.index:app --reload

# Build
npm run build

# Lint
npm run lint
```

## Architecture

### Data Flow

1. User uploads manual (PDF/URL/GitHub) → `POST /api/manual/{upload,url,github}`
2. Backend parses content → splits into chunks → generates OpenAI embeddings → stores in ChromaDB
3. User enters goal + shares screen → frontend captures screen as base64 JPEG every 200ms
4. `POST /api/step` with `{messages, manual_ids}` → backend does RAG search (top-5 chunks) → injects into system prompt → streams OpenAI response via SSE
5. Frontend detects screen pixel changes → `POST /api/check` with before/after images → auto-advances

### Frontend Architecture

- `app/providers/TaskProvider.tsx` — Core orchestration: manages task state, calls AI, handles screen change detection loop
- `app/providers/ManualProvider.tsx` — Manual CRUD state, polls processing status, exposes `activeManualIds`
- `app/providers/SettingsProvider.tsx` — Local LLM settings (Ollama/LM Studio support)
- `hooks/screenshare.tsx` — Zustand store: screen capture, 200ms pixel-diff change detection, PiP masking
- `hooks/pip.tsx` — Document Picture-in-Picture window (Chrome) with Safari popup fallback
- `lib/ai.ts` — SSE stream parsing (`readStream`), retry logic, `generateAction` sends `manual_ids` to backend
- `lib/prompts/action.ts` — System prompt builder; accepts `manualContext` string from RAG

### Backend Architecture

- `api/routers/task.py` — `/step` (OpenAI + RAG), `/check` (Gemini), `/help` (OpenAI), `/coordinates` (Qwen via OpenRouter)
- `api/routers/manual.py` — CRUD endpoints for PDF upload, URL crawl, GitHub clone; uses BackgroundTasks
- `api/services/parser/` — `pdf_parser.py` (PyMuPDF), `url_parser.py` (BeautifulSoup, depth-2 crawl), `github_parser.py` (GitPython shallow clone)
- `api/services/embedder.py` — Chunk splitting (800 tokens, 100 overlap via tiktoken) + OpenAI text-embedding-3-small
- `api/services/vectorstore.py` — ChromaDB PersistentClient wrapper
- `api/services/rag.py` — `get_manual_context()`: multi-manual search, distance-sorted, formatted with source metadata
- `api/services/manual_store.py` — JSON file persistence at `data/manuals.json`

### SSE Streaming Protocol

Backend streams as Server-Sent Events: `start → text-start → text-delta (repeated) → text-end → finish → [DONE]`

Frontend parses via `readStream()` in `lib/ai.ts`.

### Data Storage

- Manual metadata: `data/manuals.json`
- Vector embeddings: `data/chromadb/` (ChromaDB persistent)
- Uploaded PDFs: `data/uploads/`

## Environment Variables (.env.local)

```
OPENAI_API_KEY          — OpenAI API (step generation + embeddings)
OPENROUTER_API_KEY      — OpenRouter (Qwen coordinates, Gemini fallback)
GEMINI_API_KEY          — Google Gemini (step completion check)
CHROMADB_PATH           — ChromaDB path (default: ./data/chromadb)
GITHUB_TOKEN            — Optional, for private repo cloning
NEXT_PUBLIC_API_URL     — Backend URL (default: http://127.0.0.1:8000/api)
```

## AI Models Used

| Endpoint | Model | Purpose |
|----------|-------|---------|
| /step | gpt-5-mini | Generate next instruction (with RAG context) |
| /check | gemini-3-flash | Verify step completion (before/after images) |
| /help | gpt-5-mini | Answer follow-up questions |
| /coordinates | qwen3-vl-30b | Locate UI elements for click targets |
