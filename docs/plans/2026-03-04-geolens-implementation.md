# GeoLens Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an AI-powered software guide that watches the user's screen and provides step-by-step instructions based on uploaded manuals (PDF/URL/GitHub source code), using RAG to deliver manual-grounded guidance.

**Architecture:** Next.js 13 frontend (ported from screen.vision) + FastAPI backend with a RAG pipeline (ChromaDB + OpenAI embeddings). The frontend handles screen capture, PiP display, and manual upload UI. The backend processes manuals into vector embeddings and injects relevant chunks into AI prompts at runtime.

**Tech Stack:** Next.js 13, React 18, TypeScript, Tailwind CSS, Zustand, FastAPI, ChromaDB, OpenAI API, Gemini API, PyMuPDF, BeautifulSoup

---

## Task 1: Project Scaffolding — Next.js + Config Files

**Files:**
- Create: `package.json`
- Create: `next.config.js`
- Create: `tsconfig.json`
- Create: `tailwind.config.js`
- Create: `postcss.config.js`
- Create: `.eslintrc.json`
- Create: `components.json`
- Create: `.gitignore`
- Create: `.python-version`
- Create: `vercel.json`
- Create: `Procfile`

**Step 1: Initialize git repo**

```bash
cd C:\Users\user\Desktop\workspace\GeoLens
git init
```

**Step 2: Create package.json**

Copy from screen.vision, update name to "geolens" and description. Keep all dependencies identical:

```json
{
  "name": "geolens",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "fastapi-dev": "uv run python -m uvicorn api.index:app --reload",
    "next-dev": "next dev",
    "dev": "concurrently \"npm run next-dev\" \"npm run fastapi-dev\"",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@ai-sdk/openai": "^2.0.68",
    "@ai-sdk/react": "^2.0.76",
    "@geist-ui/icons": "^1.0.2",
    "@next/font": "^14.2.15",
    "@radix-ui/react-slot": "^1.1.0",
    "@types/node": "20.2.4",
    "@types/react": "18.2.7",
    "@types/react-dom": "18.2.4",
    "ai": "^5.0.76",
    "autoprefixer": "10.4.14",
    "axios": "^1.13.2",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "concurrently": "^8.0.1",
    "date-fns": "^4.1.0",
    "eslint": "8.41.0",
    "eslint-config-next": "13.4.4",
    "framer-motion": "^11.11.17",
    "geist": "^1.3.1",
    "lucide-react": "^0.460.0",
    "next": "13.4.4",
    "postcss": "8.4.23",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "react-markdown": "^9.0.1",
    "remark-gfm": "^4.0.0",
    "sonner": "^1.5.0",
    "tailwind-merge": "^2.5.4",
    "tailwindcss": "3.4.15",
    "tailwindcss-animate": "^1.0.7",
    "typescript": "5.0.4",
    "usehooks-ts": "^3.1.0",
    "zod": "^4.0.0",
    "zustand": "^5.0.8"
  }
}
```

**Step 3: Create all config files**

Copy these files exactly from `../screen.vision/`:
- `next.config.js` — remove PostHog rewrites (not needed initially), keep as minimal config
- `tsconfig.json` — identical
- `tailwind.config.js` — identical
- `postcss.config.js` — identical
- `.eslintrc.json` — identical (`{"extends": "next/core-web-vitals"}`)
- `components.json` — identical (shadcn/ui config)
- `.python-version` — identical (`3.12.7`)
- `vercel.json` — identical
- `Procfile` — identical (`web: uvicorn api.index:app --host 0.0.0.0 --port $PORT`)

**Step 4: Create .gitignore**

Copy from screen.vision and add GeoLens-specific entries:

```gitignore
# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# next.js
/.next/
/out/

# python
venv/
.venv/
.env
__pycache__

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local

# vercel
.vercel

# typescript
*.tsbuildinfo
next-env.d.ts

# GeoLens specific
data/chromadb/
data/uploads/
data/repos/
```

**Step 5: Create .env.local template**

Create `.env.example`:

```bash
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
GEMINI_API_KEY=...
CHROMADB_PATH=./data/chromadb
GITHUB_TOKEN=ghp_...
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

**Step 6: Install dependencies**

```bash
pnpm install
```

**Step 7: Commit**

```bash
git add -A
git commit -m "feat: initialize project scaffolding with Next.js + FastAPI config"
```

---

## Task 2: Port Core Frontend from screen.vision — Layout, Styles, Utils

**Files:**
- Create: `app/layout.tsx`
- Create: `app/globals.css`
- Create: `lib/utils.ts`
- Create: `lib/prompts/index.ts`
- Create: `lib/prompts/action.ts`
- Create: `lib/prompts/check.ts`
- Create: `lib/prompts/help.ts`
- Create: `lib/prompts/coordinate.ts`
- Create: `components/ui/button.tsx`
- Create: `components/ui/textarea.tsx`

**Step 1: Copy globals.css from screen.vision**

Copy `app/globals.css` exactly (all CSS variables, keyframe animations, skeleton classes).

**Step 2: Create lib/utils.ts**

Copy from screen.vision: `cn()`, `getSystemInfo()`, `getBrowserInfo()`, `getOSInfo()`, `calculateSimilarity()`, `isSimilarToString()`.

**Step 3: Create prompt files**

Copy all 4 prompt files from screen.vision's `lib/prompts/`. **Modify `action.ts`** to accept an optional `manualContext` parameter:

```typescript
// lib/prompts/action.ts
export function buildActionPrompt(
  goal: string,
  osName?: string,
  completedSteps?: string[],
  manualContext?: string  // NEW: RAG context from manuals
): string {
  let stepsSection = "";
  if (completedSteps && completedSteps.length > 0) {
    const stepsList = completedSteps
      .map((step, i) => `${i + 1}. ${step}`)
      .join("\n");
    stepsSection = `
# Steps Completed So Far
${stepsList}`;
  }

  let manualSection = "";
  if (manualContext) {
    manualSection = `
# Reference Manual Content
The following content is from the software's official documentation/source code. Use it to provide accurate, manual-based guidance:

${manualContext}`;
  }

  return `You are a UI navigation assistant helping a user complete a task by giving ONE instruction at a time.

# User's Operating System
${osName || "Unknown"}

# Goal
${goal}
${stepsSection}
${manualSection}
# What You See
A screenshot of the user's current screen state.

# How to Decide the Next Action
1. Review the GOAL to understand what the user ultimately wants to achieve.
2. If REFERENCE MANUAL CONTENT is provided, use it as your primary knowledge source for the software's features and workflows.
3. Analyze the SCREENSHOT to verify the current screen state matches expectations.
4. Determine what the NEXT logical step should be according to the manual and goal.
5. If the screen shows something unexpected (error, different page, popup), adapt your instruction to handle it.

# Response Rules
- Give ONE specific action that advances toward the goal
- Be precise: "Click the blue 'Save' button in the bottom right" not "Click Save"
- For navigation: Return only the URL (e.g. "https://google.com")
- If something is loading: "Wait"
- If content is off-screen: "Scroll Up" or "Scroll Down"
- If the goal is complete: "Done"
- If the screen shows an unexpected state (error, wrong page), provide an instruction to recover

# Output Format
Single instruction only (no explanations, no numbering, no bolding). If the goal is achieved, return "Done"`;
}
```

Keep `check.ts`, `help.ts`, `coordinate.ts` identical to screen.vision.

Create `lib/prompts/index.ts`:

```typescript
export { buildActionPrompt } from "./action";
export { buildCheckPrompt } from "./check";
export { buildHelpPrompt } from "./help";
export { buildCoordinatePrompt } from "./coordinate";
```

**Step 4: Create layout.tsx**

Simplified version of screen.vision's layout (without PostHog/Analytics initially):

```tsx
// app/layout.tsx
import "./globals.css";
import { GeistSans } from "geist/font/sans";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";
import { TaskProvider } from "./providers/TaskProvider";
import { SettingsProvider } from "./providers/SettingsProvider";
import { ManualProvider } from "./providers/ManualProvider";
import { Inter } from "next/font/google";

export const metadata = {
  title: "GeoLens",
  description: "AI-powered software guide with manual-based assistance",
};

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-inter",
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={cn(
          GeistSans.className,
          inter.variable,
          "antialiased dark",
          "bg-background"
        )}
      >
        <Toaster position="top-center" richColors />
        <SettingsProvider>
          <ManualProvider>
            <TaskProvider>{children}</TaskProvider>
          </ManualProvider>
        </SettingsProvider>
      </body>
    </html>
  );
}
```

**Step 5: Copy shadcn/ui components**

Copy `components/ui/button.tsx` and `components/ui/textarea.tsx` from screen.vision.

**Step 6: Verify build**

```bash
pnpm run build
```

Expected: Build succeeds (providers don't exist yet, so create empty placeholder files first).

**Step 7: Commit**

```bash
git add -A
git commit -m "feat: port core frontend layout, styles, prompts, and utils from screen.vision"
```

---

## Task 3: Port Screen Share, PiP, and AI Communication Layer

**Files:**
- Create: `hooks/screenshare.tsx` — copy from screen.vision
- Create: `hooks/pip.tsx` — copy from screen.vision
- Create: `lib/ai.ts` — copy from screen.vision, modify to support manual_ids
- Create: `app/providers/SettingsProvider.tsx` — copy from screen.vision

**Step 1: Copy hooks/screenshare.tsx**

Copy exactly from screen.vision. This is the Zustand store for screen capture, change detection, image scaling, PiP masking.

**Step 2: Copy hooks/pip.tsx**

Copy exactly from screen.vision. Document PiP + Safari popup fallback.

**Step 3: Copy and modify lib/ai.ts**

Copy from screen.vision. Modify `generateAction` to accept and pass `manualIds`:

```typescript
// Add to the existing generateAction function signature:
export async function generateAction(
  goal: string,
  base64Image: string,
  settings: ApiSettings,
  completedSteps?: string[],
  osName?: string,
  followUpContext?: FollowUpContext,
  manualIds?: string[]  // NEW: IDs of active manuals for RAG
) {
  // ... same retry logic ...
  // When sending to backend, include manual_ids:
  const body = {
    messages,
    manual_ids: manualIds || [],
  };
  // sendToBackend now passes full body instead of just messages
}
```

Modify `sendToBackend` to accept a generic body object:

```typescript
async function sendToBackend(
  endpoint: string,
  body: Record<string, unknown>,
  onStream?: (message: string) => void
): Promise<string> {
  const response = await fetch(`${aiApiUrl}/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  // ... rest same ...
}
```

**Step 4: Copy SettingsProvider**

Copy from screen.vision exactly.

**Step 5: Commit**

```bash
git add -A
git commit -m "feat: port screen share, PiP hooks, and AI communication layer"
```

---

## Task 4: Port Task Execution UI Components

**Files:**
- Create: `components/task-screen/types.ts` — copy from screen.vision
- Create: `components/task-screen/task-screen.tsx` — copy
- Create: `components/task-screen/task-card.tsx` — copy
- Create: `components/task-screen/task-card-base.tsx` — copy
- Create: `components/task-screen/minimal-task-screen.tsx` — copy
- Create: `components/task-screen/skeleton-content.tsx` — copy
- Create: `components/task-screen/confetti-emoji.tsx` — copy
- Create: `components/task-screen/index.tsx` — copy
- Create: `components/multimodal-input.tsx` — copy
- Create: `components/markdown.tsx` — copy
- Create: `components/icons.tsx` — copy
- Create: `components/screenshare-modal.tsx` — copy
- Create: `components/screenshare-button.tsx` — copy

**Step 1: Copy all task-screen components**

Copy the entire `components/task-screen/` directory from screen.vision. No modifications needed.

**Step 2: Copy supporting components**

Copy `multimodal-input.tsx`, `markdown.tsx`, `icons.tsx`, `screenshare-modal.tsx`, `screenshare-button.tsx` from screen.vision.

**Step 3: Commit**

```bash
git add -A
git commit -m "feat: port task execution UI components from screen.vision"
```

---

## Task 5: Create TaskProvider — Core Task Orchestration

**Files:**
- Create: `app/providers/TaskProvider.tsx` — adapted from screen.vision

**Step 1: Copy and modify TaskProvider**

Copy screen.vision's TaskProvider. Key modification: pass `manualIds` to `generateAction`:

In `triggerGenerateTaskDescription()` and related functions, retrieve `manualIds` from ManualProvider context and pass them to the AI functions:

```typescript
// Inside TaskProvider, access manuals:
// The TaskProvider needs manualIds prop or uses a separate context
// Add manualIds to the context value and pass to generateAction calls

const generateTaskDescription = async () => {
  // ... existing screen capture logic ...
  const result = await generateAction(
    goal,
    imageDataUrl,
    settings,
    completedSteps,
    osName,
    followUpContext,
    manualIds  // NEW: from ManualProvider
  );
  // ... rest same ...
};
```

The TaskProvider should accept `manualIds` via props or read from ManualProvider context. Since TaskProvider is a child of ManualProvider in the layout, it can use `useManuals()` hook.

**Step 2: Commit**

```bash
git add -A
git commit -m "feat: create TaskProvider with manual-aware action generation"
```

---

## Task 6: Backend — Python Requirements and FastAPI Base

**Files:**
- Create: `requirements.txt`
- Create: `api/__init__.py`
- Create: `api/index.py`
- Create: `api/utils/__init__.py`
- Create: `api/utils/stream.py` — copy from screen.vision
- Create: `api/utils/gemini.py` — copy from screen.vision

**Step 1: Create requirements.txt**

Start from screen.vision's requirements and add GeoLens-specific packages:

```
# From screen.vision
annotated-types==0.7.0
anyio==4.11.0
certifi==2025.10.5
charset-normalizer==3.4.4
click==8.3.0
distro==1.9.0
fastapi==0.119.1
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.11
jiter==0.11.1
openai==2.6.0
pydantic==2.12.3
pydantic_core==2.41.4
python-dotenv==1.1.1
requests==2.32.5
slowapi==0.1.9
sniffio==1.3.1
starlette==0.48.0
tqdm==4.67.1
typing-inspection==0.4.2
typing_extensions==4.15.0
urllib3==2.5.0
uvicorn==0.38.0
google-genai==1.3.0

# GeoLens additions
chromadb==1.0.7
PyMuPDF==1.25.3
beautifulsoup4==4.13.4
gitpython==3.1.44
tiktoken==0.9.0
python-multipart==0.0.20
```

**Step 2: Create api/index.py**

Minimal FastAPI app with CORS and router imports:

```python
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from .routers import task, manual

load_dotenv(".env.local")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

is_production = (
    os.getenv("RAILWAY_ENVIRONMENT_NAME") == "production"
    or os.getenv("VERCEL_ENV") == "production"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://geolens.app"]
    if is_production
    else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task.router, prefix="/api")
app.include_router(manual.router, prefix="/api/manual")
```

**Step 3: Copy utils**

Copy `api/utils/stream.py` and `api/utils/gemini.py` exactly from screen.vision. Create empty `api/utils/__init__.py` and `api/__init__.py`.

**Step 4: Create empty router stubs**

Create `api/routers/__init__.py` (empty), `api/routers/task.py` and `api/routers/manual.py` as minimal stubs so the app starts:

```python
# api/routers/task.py
from fastapi import APIRouter
router = APIRouter()

# api/routers/manual.py
from fastapi import APIRouter
router = APIRouter()
```

**Step 5: Verify backend starts**

```bash
uv run python -m uvicorn api.index:app --reload
```

Expected: Server starts on port 8000, no errors.

**Step 6: Commit**

```bash
git add -A
git commit -m "feat: set up FastAPI backend with utils, CORS, and router stubs"
```

---

## Task 7: Backend — Task Router (step/check/help/coordinates)

**Files:**
- Create: `api/routers/task.py`
- Create: `api/services/__init__.py`
- Create: `api/services/rag.py` (stub)

**Step 1: Implement task router**

Adapted from screen.vision's `api/index.py`, extracted into a router. Key change: `/api/step` accepts `manual_ids` and calls RAG before sending to OpenAI:

```python
# api/routers/task.py
from typing import Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Request as FastAPIRequest
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai import OpenAI
from google import genai
from google.genai import types
import os

from ..utils.stream import stream_text
from ..utils.gemini import convert_openai_to_gemini, stream_gemini
from ..services.rag import get_manual_context

types.ThinkingConfig.model_config["extra"] = "allow"
types.ThinkingConfig.model_rebuild(force=True)

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


class StepRequest(BaseModel):
    messages: List[Any]
    manual_ids: Optional[List[str]] = None


class MessagesRequest(BaseModel):
    messages: List[Any]


@router.post("/step")
@limiter.limit("20/minute;300/hour")
async def handle_step(request: FastAPIRequest, body: StepRequest):
    # If manual_ids provided, enrich system prompt with RAG context
    messages = body.messages
    if body.manual_ids:
        # Extract goal from system prompt for RAG query
        system_msg = next((m for m in messages if m.get("role") == "system"), None)
        if system_msg:
            context = await get_manual_context(
                manual_ids=body.manual_ids,
                query=system_msg.get("content", ""),
                top_k=5
            )
            if context:
                # Append manual context to system prompt
                system_msg["content"] += f"\n\n# Reference Manual Content\n{context}"

    client = OpenAI()
    stream = client.chat.completions.create(
        messages=messages,
        model="gpt-5-mini-2025-08-07",
        stream=True,
        reasoning_effort="low",
    )
    return StreamingResponse(
        stream_text(stream, {}),
        media_type="text/event-stream",
    )


@router.post("/help")
@limiter.limit("8/minute;100/hour")
async def handle_help(request: FastAPIRequest, body: MessagesRequest):
    client = OpenAI()
    stream = client.chat.completions.create(
        messages=body.messages,
        model="gpt-5-mini-2025-08-07",
        stream=True,
        reasoning_effort="low",
    )
    return StreamingResponse(
        stream_text(stream, {}),
        media_type="text/event-stream",
    )


@router.post("/check")
@limiter.limit("30/minute;500/hour")
async def handle_check(request: FastAPIRequest, body: MessagesRequest):
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if gemini_api_key:
        client = genai.Client(vertexai=True, api_key=gemini_api_key)
        model = "gemini-3-flash-preview"

        system_instruction_parts = []
        for msg in body.messages:
            if msg.get("role") == "system":
                content = msg.get("content")
                if isinstance(content, str):
                    system_instruction_parts.append(types.Part.from_text(text=content))
                elif isinstance(content, list):
                    for part in content:
                        if part.get("type") == "text":
                            system_instruction_parts.append(
                                types.Part.from_text(text=part.get("text"))
                            )

        system_instruction = (
            types.Content(parts=system_instruction_parts)
            if system_instruction_parts
            else None
        )
        contents = convert_openai_to_gemini(body.messages)
        generate_content_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
        )
        stream = client.models.generate_content_stream(
            model=model, contents=contents, config=generate_content_config,
        )
        return StreamingResponse(
            stream_gemini(stream), media_type="text/event-stream",
        )
    else:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
        )
        stream = client.chat.completions.create(
            messages=body.messages,
            model="google/gemini-3-flash-preview",
            extra_body={
                "provider": {"order": ["Google AI Studio"], "allow_fallbacks": True}
            },
            reasoning_effort="minimal",
            stream=True,
        )

    return StreamingResponse(
        stream_text(stream, {}), media_type="text/event-stream",
    )


@router.post("/coordinates")
@limiter.limit("15/minute;200/hour")
async def handle_coordinates(request: FastAPIRequest, body: MessagesRequest):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
    )
    stream = client.chat.completions.create(
        messages=body.messages,
        model="qwen/qwen3-vl-30b-a3b-instruct",
        extra_body={"provider": {"order": ["Fireworks"], "allow_fallbacks": True}},
        stream=True,
    )
    return StreamingResponse(
        stream_text(stream, {}), media_type="text/event-stream",
    )
```

**Step 2: Create RAG stub**

```python
# api/services/rag.py
from typing import List, Optional


async def get_manual_context(
    manual_ids: List[str],
    query: str,
    top_k: int = 5
) -> Optional[str]:
    """Retrieve relevant manual chunks for a query. Returns formatted context string."""
    # Stub — will be implemented in Task 9
    return None
```

**Step 3: Verify endpoints**

```bash
uv run python -m uvicorn api.index:app --reload
# Test: curl http://localhost:8000/docs
```

Expected: FastAPI Swagger docs show all 4 task endpoints + manual endpoints.

**Step 4: Commit**

```bash
git add -A
git commit -m "feat: implement task router with step/check/help/coordinates endpoints"
```

---

## Task 8: Backend — Manual Data Model and Storage

**Files:**
- Create: `api/models.py`
- Create: `api/services/manual_store.py`
- Create: `data/` directory

**Step 1: Create data models**

```python
# api/models.py
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class Manual(BaseModel):
    id: str
    name: str
    type: Literal["pdf", "url", "github"]
    source: str  # filename, URL, or GitHub URL
    status: Literal["processing", "ready", "error"] = "processing"
    error_message: Optional[str] = None
    chunk_count: int = 0
    created_at: str  # ISO format string

    @staticmethod
    def new(name: str, type: str, source: str) -> "Manual":
        import uuid
        return Manual(
            id=str(uuid.uuid4()),
            name=name,
            type=type,
            source=source,
            status="processing",
            chunk_count=0,
            created_at=datetime.utcnow().isoformat(),
        )


class ManualListResponse(BaseModel):
    manuals: list[Manual]
```

**Step 2: Create manual store (JSON file persistence)**

```python
# api/services/manual_store.py
import json
import os
from typing import List, Optional
from ..models import Manual

DATA_DIR = os.environ.get("DATA_DIR", "./data")
MANUALS_FILE = os.path.join(DATA_DIR, "manuals.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_manuals() -> List[Manual]:
    _ensure_data_dir()
    if not os.path.exists(MANUALS_FILE):
        return []
    with open(MANUALS_FILE, "r") as f:
        data = json.load(f)
    return [Manual(**m) for m in data]


def save_manuals(manuals: List[Manual]):
    _ensure_data_dir()
    with open(MANUALS_FILE, "w") as f:
        json.dump([m.model_dump() for m in manuals], f, indent=2)


def add_manual(manual: Manual):
    manuals = load_manuals()
    manuals.append(manual)
    save_manuals(manuals)


def update_manual(manual_id: str, **kwargs):
    manuals = load_manuals()
    for m in manuals:
        if m.id == manual_id:
            for k, v in kwargs.items():
                setattr(m, k, v)
            break
    save_manuals(manuals)


def get_manual(manual_id: str) -> Optional[Manual]:
    manuals = load_manuals()
    return next((m for m in manuals if m.id == manual_id), None)


def delete_manual(manual_id: str) -> bool:
    manuals = load_manuals()
    filtered = [m for m in manuals if m.id != manual_id]
    if len(filtered) == len(manuals):
        return False
    save_manuals(filtered)
    return True
```

**Step 3: Create data directory**

```bash
mkdir -p data
```

**Step 4: Commit**

```bash
git add -A
git commit -m "feat: add manual data model and JSON file persistence"
```

---

## Task 9: Backend — Vector Store (ChromaDB) and Embedder

**Files:**
- Create: `api/services/vectorstore.py`
- Create: `api/services/embedder.py`
- Update: `api/services/rag.py` — implement real RAG

**Step 1: Create vectorstore module**

```python
# api/services/vectorstore.py
import os
import chromadb
from typing import List, Optional

CHROMADB_PATH = os.environ.get("CHROMADB_PATH", "./data/chromadb")

_client: Optional[chromadb.PersistentClient] = None


def get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        os.makedirs(CHROMADB_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(path=CHROMADB_PATH)
    return _client


def get_collection(manual_id: str):
    client = get_client()
    return client.get_or_create_collection(
        name=f"manual_{manual_id}",
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(
    manual_id: str,
    texts: List[str],
    embeddings: List[List[float]],
    metadatas: List[dict],
    ids: List[str],
):
    collection = get_collection(manual_id)
    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )


def search(
    manual_id: str,
    query_embedding: List[float],
    top_k: int = 5,
) -> dict:
    collection = get_collection(manual_id)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )


def delete_collection(manual_id: str):
    client = get_client()
    try:
        client.delete_collection(f"manual_{manual_id}")
    except Exception:
        pass  # Collection may not exist
```

**Step 2: Create embedder module**

```python
# api/services/embedder.py
import uuid
import tiktoken
from typing import List, Tuple
from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 800  # tokens
CHUNK_OVERLAP = 100  # tokens


def count_tokens(text: str) -> int:
    enc = tiktoken.encoding_for_model("gpt-4")
    return len(enc.encode(text))


def split_into_chunks(
    text: str,
    metadata_base: dict,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[Tuple[str, dict]]:
    """Split text into overlapping chunks with metadata."""
    enc = tiktoken.encoding_for_model("gpt-4")
    tokens = enc.encode(text)

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)

        metadata = {**metadata_base, "chunk_index": len(chunks)}
        chunks.append((chunk_text, metadata))

        if end >= len(tokens):
            break
        start += chunk_size - overlap

    return chunks


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts using OpenAI."""
    client = OpenAI()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def embed_and_store(
    manual_id: str,
    chunks: List[Tuple[str, dict]],
):
    """Embed chunks and store in ChromaDB."""
    from . import vectorstore

    if not chunks:
        return 0

    texts = [c[0] for c in chunks]
    metadatas = [c[1] for c in chunks]
    ids = [f"{manual_id}_{i}_{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]

    # Batch embeddings (max 2048 per request)
    BATCH_SIZE = 2048
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        all_embeddings.extend(generate_embeddings(batch))

    vectorstore.add_chunks(
        manual_id=manual_id,
        texts=texts,
        embeddings=all_embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    return len(chunks)
```

**Step 3: Implement RAG query**

```python
# api/services/rag.py
from typing import List, Optional
from .embedder import generate_embeddings
from . import vectorstore


async def get_manual_context(
    manual_ids: List[str],
    query: str,
    top_k: int = 5,
) -> Optional[str]:
    """Retrieve relevant chunks from manuals and format as context string."""
    if not manual_ids:
        return None

    # Generate query embedding
    query_embeddings = generate_embeddings([query])
    if not query_embeddings:
        return None

    query_embedding = query_embeddings[0]

    # Search across all specified manuals
    all_results = []
    for manual_id in manual_ids:
        try:
            results = vectorstore.search(
                manual_id=manual_id,
                query_embedding=query_embedding,
                top_k=top_k,
            )
            if results and results.get("documents"):
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                distances = results["distances"][0] if results.get("distances") else [0] * len(docs)
                for doc, meta, dist in zip(docs, metas, distances):
                    all_results.append((doc, meta, dist))
        except Exception as e:
            print(f"Error searching manual {manual_id}: {e}")
            continue

    if not all_results:
        return None

    # Sort by distance (ascending = more similar) and take top_k
    all_results.sort(key=lambda x: x[2])
    top_results = all_results[:top_k]

    # Format context
    context_parts = []
    for doc, meta, _ in top_results:
        source_info = []
        if meta.get("section"):
            source_info.append(f"Section: {meta['section']}")
        if meta.get("page"):
            source_info.append(f"Page: {meta['page']}")
        if meta.get("file_path"):
            source_info.append(f"File: {meta['file_path']}")
        if meta.get("language"):
            source_info.append(f"Language: {meta['language']}")

        header = f"[{', '.join(source_info)}]" if source_info else ""
        if meta.get("category") == "code":
            lang = meta.get("language", "")
            context_parts.append(f"{header}\n```{lang}\n{doc}\n```")
        else:
            context_parts.append(f"{header}\n{doc}")

    return "\n\n---\n\n".join(context_parts)
```

**Step 4: Commit**

```bash
git add -A
git commit -m "feat: implement ChromaDB vectorstore, embedder, and RAG query"
```

---

## Task 10: Backend — PDF Parser

**Files:**
- Create: `api/services/parser/__init__.py`
- Create: `api/services/parser/pdf_parser.py`

**Step 1: Implement PDF parser**

```python
# api/services/parser/pdf_parser.py
import fitz  # PyMuPDF
from typing import List, Tuple


def parse_pdf(file_path: str) -> List[Tuple[str, dict]]:
    """Parse PDF and return list of (text, metadata) tuples ready for chunking."""
    doc = fitz.open(file_path)
    results = []

    # Try to extract TOC for section names
    toc = doc.get_toc()
    page_sections = {}
    for level, title, page_num in toc:
        page_sections[page_num - 1] = title  # 0-indexed

    current_section = "Introduction"
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        if not text.strip():
            continue

        if page_num in page_sections:
            current_section = page_sections[page_num]

        metadata = {
            "source_type": "pdf",
            "page": page_num + 1,
            "section": current_section,
            "category": "doc",
        }
        results.append((text, metadata))

    doc.close()
    return results
```

**Step 2: Commit**

```bash
git add -A
git commit -m "feat: implement PDF parser using PyMuPDF"
```

---

## Task 11: Backend — URL Parser

**Files:**
- Create: `api/services/parser/url_parser.py`

**Step 1: Implement URL parser**

```python
# api/services/parser/url_parser.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Tuple, Set


def _fetch_page(url: str) -> str:
    """Fetch page content."""
    headers = {"User-Agent": "GeoLens/1.0 (Documentation Crawler)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def _extract_content(html: str, url: str) -> Tuple[str, List[str]]:
    """Extract main content text and child links from HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove nav, footer, sidebar, script, style
    for tag in soup.find_all(["nav", "footer", "script", "style", "header", "aside"]):
        tag.decompose()

    # Try to find main content area
    main = soup.find("main") or soup.find("article") or soup.find(role="main")
    content_area = main if main else soup.find("body")

    if not content_area:
        return "", []

    # Extract text with heading structure
    text_parts = []
    for element in content_area.find_all(["h1", "h2", "h3", "h4", "p", "li", "pre", "code", "td"]):
        tag_name = element.name
        text = element.get_text(strip=True)
        if not text:
            continue

        if tag_name.startswith("h"):
            level = int(tag_name[1])
            text_parts.append(f"\n{'#' * level} {text}\n")
        elif tag_name in ("pre", "code"):
            text_parts.append(f"\n```\n{text}\n```\n")
        else:
            text_parts.append(text)

    # Extract child links (same domain)
    base_domain = urlparse(url).netloc
    links = []
    for a in content_area.find_all("a", href=True):
        href = urljoin(url, a["href"])
        if urlparse(href).netloc == base_domain and href != url:
            links.append(href.split("#")[0])  # Remove anchors

    return "\n".join(text_parts), list(set(links))


def parse_url(url: str, max_depth: int = 2) -> List[Tuple[str, dict]]:
    """Crawl URL and return list of (text, metadata) tuples."""
    results = []
    visited: Set[str] = set()

    def _crawl(current_url: str, depth: int):
        if depth > max_depth or current_url in visited:
            return
        visited.add(current_url)

        try:
            html = _fetch_page(current_url)
            text, child_links = _extract_content(html, current_url)

            if text.strip():
                metadata = {
                    "source_type": "url",
                    "section": current_url,
                    "category": "doc",
                }
                results.append((text, metadata))

            if depth < max_depth:
                for link in child_links[:20]:  # Limit child pages
                    _crawl(link, depth + 1)

        except Exception as e:
            print(f"Error crawling {current_url}: {e}")

    _crawl(url, 0)
    return results
```

**Step 2: Commit**

```bash
git add -A
git commit -m "feat: implement URL parser with recursive crawling"
```

---

## Task 12: Backend — GitHub Parser

**Files:**
- Create: `api/services/parser/github_parser.py`

**Step 1: Implement GitHub parser**

```python
# api/services/parser/github_parser.py
import os
import shutil
import tempfile
from typing import List, Tuple
from git import Repo


# File extensions to parse
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
    ".rb", ".php", ".cs", ".cpp", ".c", ".h", ".swift", ".kt",
}
DOC_EXTENSIONS = {".md", ".txt", ".rst", ".adoc"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml"}

# Files to skip
SKIP_DIRS = {"node_modules", ".git", "venv", ".venv", "__pycache__", "dist", "build", ".next"}
MAX_FILE_SIZE = 100_000  # 100KB per file


def _get_language(ext: str) -> str:
    """Map file extension to language name."""
    lang_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".tsx": "tsx", ".jsx": "jsx", ".java": "java", ".go": "go",
        ".rs": "rust", ".rb": "ruby", ".php": "php", ".cs": "csharp",
        ".cpp": "cpp", ".c": "c", ".swift": "swift", ".kt": "kotlin",
    }
    return lang_map.get(ext, "")


def _get_category(ext: str) -> str:
    if ext in CODE_EXTENSIONS:
        return "code"
    if ext in DOC_EXTENSIONS:
        return "doc"
    if ext in CONFIG_EXTENSIONS:
        return "config"
    return "doc"


def parse_github(repo_url: str) -> List[Tuple[str, dict]]:
    """Clone repo and parse relevant files. Returns (text, metadata) tuples."""
    results = []
    clone_dir = tempfile.mkdtemp(prefix="geolens_repo_")

    try:
        # Shallow clone
        token = os.environ.get("GITHUB_TOKEN")
        if token and "github.com" in repo_url:
            # Insert token for auth
            repo_url = repo_url.replace(
                "https://github.com",
                f"https://{token}@github.com"
            )
        Repo.clone_from(repo_url, clone_dir, depth=1)

        # Generate directory tree
        tree_lines = []
        all_extensions = CODE_EXTENSIONS | DOC_EXTENSIONS | CONFIG_EXTENSIONS

        for root, dirs, files in os.walk(clone_dir):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            rel_root = os.path.relpath(root, clone_dir)

            for fname in sorted(files):
                ext = os.path.splitext(fname)[1].lower()
                if ext not in all_extensions:
                    continue

                rel_path = os.path.join(rel_root, fname) if rel_root != "." else fname
                file_path = os.path.join(root, fname)

                # Skip large files
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    continue

                tree_lines.append(rel_path)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except Exception:
                    continue

                if not content.strip():
                    continue

                category = _get_category(ext)
                language = _get_language(ext) if category == "code" else None

                # Prioritize README and docs
                is_readme = fname.lower().startswith("readme")

                metadata = {
                    "source_type": "github",
                    "file_path": rel_path,
                    "section": rel_path,
                    "category": category,
                    "language": language,
                    "is_readme": is_readme,
                }
                results.append((content, metadata))

        # Add directory tree as first chunk
        if tree_lines:
            tree_text = "# Repository Structure\n\n" + "\n".join(tree_lines)
            results.insert(0, (tree_text, {
                "source_type": "github",
                "section": "directory_structure",
                "category": "doc",
            }))

    finally:
        shutil.rmtree(clone_dir, ignore_errors=True)

    # Sort: READMEs first, then docs, then config, then code
    priority = {"doc": 0, "config": 1, "code": 2}
    results.sort(key=lambda x: (
        0 if x[1].get("is_readme") else 1,
        priority.get(x[1].get("category", "code"), 2),
    ))

    return results
```

**Step 2: Commit**

```bash
git add -A
git commit -m "feat: implement GitHub repo parser with code analysis"
```

---

## Task 13: Backend — Manual Router (Upload/URL/GitHub/List/Delete)

**Files:**
- Update: `api/routers/manual.py`

**Step 1: Implement manual router**

```python
# api/routers/manual.py
import os
import uuid
import shutil
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Request, BackgroundTasks
from pydantic import BaseModel

from ..models import Manual, ManualListResponse
from ..services.manual_store import (
    load_manuals, add_manual, update_manual, delete_manual as store_delete, get_manual,
)
from ..services.parser.pdf_parser import parse_pdf
from ..services.parser.url_parser import parse_url
from ..services.parser.github_parser import parse_github
from ..services.embedder import split_into_chunks, embed_and_store
from ..services import vectorstore

router = APIRouter()

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "./data/uploads")


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


async def _process_manual(manual_id: str, raw_chunks: list):
    """Background task: split raw text into token chunks, embed, and store."""
    try:
        all_chunks = []
        for text, metadata in raw_chunks:
            metadata["manual_id"] = manual_id
            chunks = split_into_chunks(text, metadata)
            all_chunks.extend(chunks)

        if not all_chunks:
            update_manual(manual_id, status="error", error_message="No content extracted")
            return

        count = embed_and_store(manual_id, all_chunks)
        update_manual(manual_id, status="ready", chunk_count=count)
    except Exception as e:
        update_manual(manual_id, status="error", error_message=str(e))


@router.post("/upload")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
):
    _ensure_upload_dir()

    manual = Manual.new(
        name=name or file.filename or "Untitled PDF",
        type="pdf",
        source=file.filename or "upload.pdf",
    )

    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, f"{manual.id}.pdf")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    add_manual(manual)

    # Parse and embed in background
    try:
        raw_chunks = parse_pdf(file_path)
    except Exception as e:
        update_manual(manual.id, status="error", error_message=str(e))
        return manual

    background_tasks.add_task(_process_manual, manual.id, raw_chunks)
    return manual


class UrlRequest(BaseModel):
    url: str
    name: Optional[str] = None


@router.post("/url")
async def add_url(body: UrlRequest, background_tasks: BackgroundTasks):
    manual = Manual.new(
        name=body.name or body.url,
        type="url",
        source=body.url,
    )
    add_manual(manual)

    try:
        raw_chunks = parse_url(body.url)
    except Exception as e:
        update_manual(manual.id, status="error", error_message=str(e))
        return manual

    background_tasks.add_task(_process_manual, manual.id, raw_chunks)
    return manual


class GithubRequest(BaseModel):
    url: str
    name: Optional[str] = None


@router.post("/github")
async def add_github(body: GithubRequest, background_tasks: BackgroundTasks):
    manual = Manual.new(
        name=body.name or body.url.split("/")[-1],
        type="github",
        source=body.url,
    )
    add_manual(manual)

    try:
        raw_chunks = parse_github(body.url)
    except Exception as e:
        update_manual(manual.id, status="error", error_message=str(e))
        return manual

    background_tasks.add_task(_process_manual, manual.id, raw_chunks)
    return manual


@router.get("/list")
async def list_manuals():
    manuals = load_manuals()
    return ManualListResponse(manuals=manuals)


@router.get("/{manual_id}")
async def get_manual_by_id(manual_id: str):
    manual = get_manual(manual_id)
    if not manual:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Manual not found")
    return manual


@router.delete("/{manual_id}")
async def delete_manual_endpoint(manual_id: str):
    # Delete from ChromaDB
    vectorstore.delete_collection(manual_id)

    # Delete uploaded file if exists
    pdf_path = os.path.join(UPLOAD_DIR, f"{manual_id}.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    # Delete from store
    deleted = store_delete(manual_id)
    if not deleted:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Manual not found")

    return {"status": "deleted"}
```

**Step 2: Verify all endpoints**

```bash
uv run python -m uvicorn api.index:app --reload
# Check: http://localhost:8000/docs — all manual endpoints should appear
```

**Step 3: Commit**

```bash
git add -A
git commit -m "feat: implement manual router with PDF upload, URL crawl, and GitHub clone"
```

---

## Task 14: Frontend — ManualProvider and Manual Hook

**Files:**
- Create: `app/providers/ManualProvider.tsx`
- Create: `hooks/manual.tsx`

**Step 1: Create ManualProvider**

```tsx
// app/providers/ManualProvider.tsx
"use client";

import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import { aiApiUrl } from "@/lib/ai";

export interface Manual {
  id: string;
  name: string;
  type: "pdf" | "url" | "github";
  source: string;
  status: "processing" | "ready" | "error";
  error_message?: string;
  chunk_count: number;
  created_at: string;
}

interface ManualContextType {
  manuals: Manual[];
  activeManualIds: string[];
  isUploading: boolean;
  uploadPdf: (file: File, name?: string) => Promise<void>;
  addUrl: (url: string, name?: string) => Promise<void>;
  addGithub: (url: string, name?: string) => Promise<void>;
  deleteManual: (id: string) => Promise<void>;
  refreshManuals: () => Promise<void>;
}

const ManualContext = createContext<ManualContextType | null>(null);

export function useManuals() {
  const context = useContext(ManualContext);
  if (!context) throw new Error("useManuals must be used within ManualProvider");
  return context;
}

export function ManualProvider({ children }: { children: React.ReactNode }) {
  const [manuals, setManuals] = useState<Manual[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const refreshManuals = useCallback(async () => {
    try {
      const res = await fetch(`${aiApiUrl.replace("/api", "")}/api/manual/list`);
      if (res.ok) {
        const data = await res.json();
        setManuals(data.manuals);
      }
    } catch (e) {
      console.error("Failed to fetch manuals:", e);
    }
  }, []);

  useEffect(() => {
    refreshManuals();
  }, [refreshManuals]);

  // Poll for processing manuals
  useEffect(() => {
    const hasProcessing = manuals.some((m) => m.status === "processing");
    if (!hasProcessing) return;

    const interval = setInterval(refreshManuals, 3000);
    return () => clearInterval(interval);
  }, [manuals, refreshManuals]);

  const activeManualIds = manuals
    .filter((m) => m.status === "ready")
    .map((m) => m.id);

  const uploadPdf = useCallback(async (file: File, name?: string) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      if (name) formData.append("name", name);

      await fetch(`${aiApiUrl.replace("/api", "")}/api/manual/upload`, {
        method: "POST",
        body: formData,
      });
      await refreshManuals();
    } finally {
      setIsUploading(false);
    }
  }, [refreshManuals]);

  const addUrl = useCallback(async (url: string, name?: string) => {
    setIsUploading(true);
    try {
      await fetch(`${aiApiUrl.replace("/api", "")}/api/manual/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, name }),
      });
      await refreshManuals();
    } finally {
      setIsUploading(false);
    }
  }, [refreshManuals]);

  const addGithub = useCallback(async (url: string, name?: string) => {
    setIsUploading(true);
    try {
      await fetch(`${aiApiUrl.replace("/api", "")}/api/manual/github`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, name }),
      });
      await refreshManuals();
    } finally {
      setIsUploading(false);
    }
  }, [refreshManuals]);

  const deleteManual = useCallback(async (id: string) => {
    await fetch(`${aiApiUrl.replace("/api", "")}/api/manual/${id}`, {
      method: "DELETE",
    });
    await refreshManuals();
  }, [refreshManuals]);

  return (
    <ManualContext.Provider
      value={{
        manuals,
        activeManualIds,
        isUploading,
        uploadPdf,
        addUrl,
        addGithub,
        deleteManual,
        refreshManuals,
      }}
    >
      {children}
    </ManualContext.Provider>
  );
}
```

**Step 2: Commit**

```bash
git add -A
git commit -m "feat: create ManualProvider with upload, URL, GitHub, and delete support"
```

---

## Task 15: Frontend — Manual Upload Components

**Files:**
- Create: `components/manual/manual-upload.tsx`
- Create: `components/manual/manual-list.tsx`
- Create: `components/manual/manual-status.tsx`

**Step 1: Create manual-upload component**

PDF drag-and-drop + URL input + GitHub URL input. Uses tabs/sections for each input type. Calls ManualProvider methods on submit.

Key structure:
```tsx
// components/manual/manual-upload.tsx
"use client";

import { useState, useCallback, useRef } from "react";
import { useManuals } from "@/app/providers/ManualProvider";
import { Upload, Globe, Github, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ManualUpload() {
  const { uploadPdf, addUrl, addGithub, isUploading } = useManuals();
  const [activeTab, setActiveTab] = useState<"pdf" | "url" | "github">("pdf");
  const [urlInput, setUrlInput] = useState("");
  const [githubInput, setGithubInput] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === "application/pdf") {
      await uploadPdf(file);
    }
  }, [uploadPdf]);

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) await uploadPdf(file);
  }, [uploadPdf]);

  // Render tab buttons + content for each type
  // PDF: drag zone + file picker
  // URL: text input + submit button
  // GitHub: text input + submit button
  // ... (full JSX implementation)
}
```

**Step 2: Create manual-list component**

Shows list of registered manuals with status badges and delete buttons:

```tsx
// components/manual/manual-list.tsx
"use client";

import { useManuals, Manual } from "@/app/providers/ManualProvider";
import { FileText, Globe, Github, Trash2, Loader2, CheckCircle, XCircle } from "lucide-react";

export function ManualList() {
  const { manuals, deleteManual } = useManuals();

  if (manuals.length === 0) return null;

  // Render list of manuals with:
  // - Icon based on type (FileText for PDF, Globe for URL, Github for GitHub)
  // - Name and source
  // - Status badge (processing=spinner, ready=green check, error=red x)
  // - Delete button
  // ... (full JSX implementation)
}
```

**Step 3: Create manual-status component**

Processing progress indicator:

```tsx
// components/manual/manual-status.tsx
"use client";

import { useManuals } from "@/app/providers/ManualProvider";
import { Loader2 } from "lucide-react";

export function ManualStatus() {
  const { manuals } = useManuals();
  const processing = manuals.filter((m) => m.status === "processing");

  if (processing.length === 0) return null;

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <Loader2 className="w-4 h-4 animate-spin" />
      <span>Processing {processing.length} manual(s)...</span>
    </div>
  );
}
```

**Step 4: Commit**

```bash
git add -A
git commit -m "feat: create manual upload, list, and status components"
```

---

## Task 16: Frontend — Home Page (Manual Upload + Goal Input)

**Files:**
- Create: `app/(home)/page.tsx`
- Create: `components/goal-input.tsx`

**Step 1: Create home page**

The landing page combines manual upload area with goal input. When the user has uploaded at least one manual and enters a goal, they can start the task session.

```tsx
// app/(home)/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ManualUpload } from "@/components/manual/manual-upload";
import { ManualList } from "@/components/manual/manual-list";
import { ManualStatus } from "@/components/manual/manual-status";
import { GoalInput } from "@/components/goal-input";
import { useManuals } from "@/app/providers/ManualProvider";

export default function HomePage() {
  const router = useRouter();
  const { activeManualIds } = useManuals();

  const handleStart = (goal: string) => {
    // Store goal in sessionStorage and navigate to task page
    sessionStorage.setItem("geolens_goal", goal);
    router.push("/task");
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold">GeoLens</h1>
          <p className="text-muted-foreground">
            Upload a manual, describe your goal, and let AI guide you step by step.
          </p>
        </div>

        <ManualUpload />
        <ManualList />
        <ManualStatus />

        <GoalInput
          onSubmit={handleStart}
          hasManuals={activeManualIds.length > 0}
        />
      </div>
    </div>
  );
}
```

**Step 2: Create goal-input component**

Text input with suggested examples:

```tsx
// components/goal-input.tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowRight } from "lucide-react";

interface GoalInputProps {
  onSubmit: (goal: string) => void;
  hasManuals: boolean;
}

export function GoalInput({ onSubmit, hasManuals }: GoalInputProps) {
  const [goal, setGoal] = useState("");

  return (
    <div className="space-y-4">
      <Textarea
        placeholder="Describe what you want to do with the software..."
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        className="min-h-[80px]"
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey && goal.trim()) {
            e.preventDefault();
            onSubmit(goal.trim());
          }
        }}
      />
      {!hasManuals && (
        <p className="text-sm text-yellow-500">
          No manuals uploaded. AI will guide you without manual reference.
        </p>
      )}
      <Button
        onClick={() => onSubmit(goal.trim())}
        disabled={!goal.trim()}
        className="w-full"
      >
        Start Guide <ArrowRight className="w-4 h-4 ml-2" />
      </Button>
    </div>
  );
}
```

**Step 3: Commit**

```bash
git add -A
git commit -m "feat: create home page with manual upload and goal input"
```

---

## Task 17: Frontend — Task Page (Screen Share + Task Execution)

**Files:**
- Create: `app/(task)/page.tsx`

**Step 1: Create task page**

Adapted from screen.vision's `(chat)/page.tsx`. Reads goal from sessionStorage, initiates screen share, shows task execution UI.

The key integration point: pass `manualIds` from ManualProvider into TaskProvider's action generation.

```tsx
// app/(task)/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTasks } from "@/app/providers/TaskProvider";
import { useManuals } from "@/app/providers/ManualProvider";
import { ScreenshareModal } from "@/components/screenshare-modal";
import { MinimalTaskScreen } from "@/components/task-screen";
import { useScreenShare } from "@/hooks/screenshare";
import { useTaskPip } from "@/hooks/pip";

export default function TaskPage() {
  const router = useRouter();
  const [goal, setGoal] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(true);
  const { activeManualIds } = useManuals();
  const { startSession, isSharing } = useTasks();
  const screenShare = useScreenShare();

  useEffect(() => {
    const stored = sessionStorage.getItem("geolens_goal");
    if (!stored) {
      router.push("/");
      return;
    }
    setGoal(stored);
  }, [router]);

  const handleAcceptScreenShare = async () => {
    setShowModal(false);
    await screenShare.requestScreenShare();
    if (goal) {
      startSession(goal, activeManualIds);
    }
  };

  if (!goal) return null;

  return (
    <div className="min-h-screen">
      {showModal && (
        <ScreenshareModal
          onAccept={handleAcceptScreenShare}
          onDecline={() => router.push("/")}
        />
      )}
      {isSharing && <MinimalTaskScreen />}
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add -A
git commit -m "feat: create task page with screen share and manual-aware execution"
```

---

## Task 18: Integration — Wire ManualIds Through Task Flow

**Files:**
- Modify: `app/providers/TaskProvider.tsx`
- Modify: `lib/ai.ts`

**Step 1: Update TaskProvider to accept and use manualIds**

In TaskProvider, add `manualIds` to the session state. When calling `generateAction`, pass `manualIds`:

```typescript
// In TaskProvider:
const [manualIds, setManualIds] = useState<string[]>([]);

const startSession = (goal: string, manualIds: string[]) => {
  setGoal(goal);
  setManualIds(manualIds);
  triggerFirstTask();
};

// In generateTaskDescription:
const result = await generateAction(
  goal,
  imageDataUrl,
  settings,
  completedSteps,
  osName,
  followUpContext,
  manualIds  // Pass through to backend
);
```

**Step 2: Update lib/ai.ts sendToBackend calls**

Ensure `generateAction` passes `manual_ids` in the request body to `/api/step`:

```typescript
// In generateAction:
if (shouldUseDirectApi(settings)) {
  return await sendDirectToApi(messages, settings);
} else {
  return await sendToBackend("step", {
    messages,
    manual_ids: manualIds || [],
  });
}
```

All other endpoints (`check`, `help`, `coordinates`) continue sending `{ messages }` only.

**Step 3: End-to-end test**

```bash
pnpm run dev
# 1. Upload a PDF manual
# 2. Enter a goal
# 3. Share screen
# 4. Verify the AI response references manual content
```

**Step 4: Commit**

```bash
git add -A
git commit -m "feat: wire manual IDs through task flow for RAG-enhanced guidance"
```

---

## Task 19: Public Assets and Final Polish

**Files:**
- Create: `public/icon.png` — GeoLens app icon
- Create: `public/cursor.png` — copy from screen.vision (used for coordinate snapshots)
- Create: `app/error.tsx` — error boundary (copy from screen.vision)

**Step 1: Copy public assets**

Copy `cursor.png` from screen.vision's `public/` directory. Create or generate a simple `icon.png` for GeoLens.

**Step 2: Create error boundary**

Copy `app/error.tsx` from screen.vision (handles chunk load errors with auto-reload).

**Step 3: Create .env.local from .env.example**

```bash
cp .env.example .env.local
# Fill in actual API keys
```

**Step 4: Full build test**

```bash
pnpm run build
```

Expected: Build succeeds with no errors.

**Step 5: Dev mode test**

```bash
pnpm run dev
```

Expected: Both Next.js and FastAPI start, home page loads, manual upload works.

**Step 6: Commit**

```bash
git add -A
git commit -m "feat: add public assets, error boundary, and finalize project setup"
```

---

## Task 20: Create CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

**Step 1: Write CLAUDE.md**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GeoLens is an AI-powered software guide. Users upload manuals (PDF/URL/GitHub), describe a goal, share their screen, and AI provides step-by-step instructions grounded in the manual content. Based on screen.vision architecture.

## Tech Stack

- **Frontend**: Next.js 13.4, React 18, TypeScript, Tailwind CSS 3.4, Zustand, shadcn/ui
- **Backend**: FastAPI (Python 3.12), ChromaDB, OpenAI API, Gemini API
- **Package Manager**: pnpm
- **Python**: uv (package manager)

## Commands

```bash
# Development (runs both Next.js and FastAPI concurrently)
pnpm run dev

# Frontend only
pnpm run next-dev

# Backend only
pnpm run fastapi-dev
# or: uv run python -m uvicorn api.index:app --reload

# Build
pnpm run build

# Lint
pnpm run lint
```

## Architecture

### Frontend → Backend Flow

1. User uploads manual (PDF/URL/GitHub) → `POST /api/manual/{upload,url,github}`
2. Backend parses → chunks → embeds → stores in ChromaDB
3. User enters goal + shares screen → frontend captures screen as base64 JPEG
4. `POST /api/step` with messages + manual_ids → backend does RAG search → injects relevant chunks into system prompt → streams OpenAI response via SSE
5. Frontend detects screen changes (pixel diff every 200ms) → `POST /api/check` (before/after images) → auto-advances to next step

### Key Directories

- `app/providers/` — React context providers (TaskProvider orchestrates the task loop, ManualProvider manages manual state)
- `hooks/` — Zustand stores: `screenshare.tsx` (capture + change detection), `pip.tsx` (Picture-in-Picture)
- `lib/ai.ts` — Frontend AI communication (SSE stream parsing, retry logic)
- `lib/prompts/` — System prompt builders; `action.ts` accepts `manualContext` for RAG
- `api/routers/` — FastAPI route handlers
- `api/services/parser/` — PDF (PyMuPDF), URL (BeautifulSoup), GitHub (GitPython) parsers
- `api/services/embedder.py` — Chunk splitting + OpenAI embedding generation
- `api/services/vectorstore.py` — ChromaDB operations
- `api/services/rag.py` — RAG query: searches ChromaDB, formats context string

### Data Storage

- Manual metadata: `data/manuals.json` (JSON file)
- Vector embeddings: `data/chromadb/` (ChromaDB persistent storage)
- Uploaded PDFs: `data/uploads/`

## Environment Variables (.env.local)

```
OPENAI_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY — AI model access
CHROMADB_PATH — ChromaDB storage path (default: ./data/chromadb)
GITHUB_TOKEN — Optional, for private repo cloning
NEXT_PUBLIC_API_URL — Backend URL (default: http://127.0.0.1:8000/api)
```

## SSE Streaming Protocol

Backend streams responses as Server-Sent Events with JSON payloads:
`start → text-start → text-delta (repeated) → text-end → finish → [DONE]`

Frontend parses via `readStream()` in `lib/ai.ts`.
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: create CLAUDE.md with project guidance"
```

---

## Summary of Tasks

| Task | Description | Key Files |
|------|-------------|-----------|
| 1 | Project scaffolding | package.json, configs, .gitignore |
| 2 | Core frontend (layout, styles, prompts, utils) | app/layout.tsx, globals.css, lib/ |
| 3 | Screen share, PiP, AI communication | hooks/, lib/ai.ts |
| 4 | Task execution UI components | components/task-screen/, multimodal-input |
| 5 | TaskProvider (core orchestration) | app/providers/TaskProvider.tsx |
| 6 | Backend scaffolding (FastAPI + utils) | api/index.py, api/utils/ |
| 7 | Task router (step/check/help/coordinates) | api/routers/task.py |
| 8 | Manual data model + storage | api/models.py, api/services/manual_store.py |
| 9 | ChromaDB vectorstore + embedder + RAG | api/services/vectorstore.py, embedder.py, rag.py |
| 10 | PDF parser | api/services/parser/pdf_parser.py |
| 11 | URL parser | api/services/parser/url_parser.py |
| 12 | GitHub parser | api/services/parser/github_parser.py |
| 13 | Manual router (CRUD endpoints) | api/routers/manual.py |
| 14 | ManualProvider frontend | app/providers/ManualProvider.tsx |
| 15 | Manual upload UI components | components/manual/ |
| 16 | Home page (manual + goal) | app/(home)/page.tsx |
| 17 | Task page (screen share + execution) | app/(task)/page.tsx |
| 18 | Wire manualIds through task flow | TaskProvider + ai.ts integration |
| 19 | Public assets + polish | public/, error boundary |
| 20 | CLAUDE.md | CLAUDE.md |
