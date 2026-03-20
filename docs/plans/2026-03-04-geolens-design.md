# GeoLens Design Document

## Overview

GeoLens는 AI가 화면을 실시간으로 보면서 소프트웨어 사용법을 단계별로 안내하는 도구이다. screen.vision과 동일한 핵심 동작(화면공유 → AI 화면 분석 → 단계별 안내 → 자동 진행 감지)을 기반으로, **매뉴얼(PDF/URL) 및 GitHub 소스코드를 지식 소스로 활용하는 RAG 파이프라인**이 추가된다.

핵심 차별점: 매뉴얼/코드를 제공하면 AI가 이를 학습하여 매뉴얼 기반의 정확한 안내를 제공한다.

## Tech Stack

- **Frontend**: Next.js 13, React 18, Tailwind CSS, Zustand, Framer Motion
- **Backend**: FastAPI (Python)
- **AI Models**: GPT (OpenAI) - 단계 생성, Gemini (Google) - 완료 확인, Qwen (OpenRouter) - 좌표 감지
- **Vector DB**: ChromaDB (로컬)
- **Embedding**: OpenAI text-embedding-3-small
- **Deployment**: Vercel (프론트엔드) + Railway (백엔드)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                     │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐ │
│  │ 매뉴얼    │  │ 화면공유  │  │ 태스크 실행 화면       │ │
│  │ 업로드    │  │ + PiP    │  │ (screen.vision 동일)   │ │
│  └────┬─────┘  └────┬─────┘  └───────────┬────────────┘ │
│       │              │                    │               │
│       ▼              ▼                    ▼               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Zustand + Context Providers             │ │
│  │  ManualStore / ScreenShareStore / TaskProvider       │ │
│  └──────────────────────┬──────────────────────────────┘ │
└─────────────────────────┼────────────────────────────────┘
                          │ HTTP + SSE
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                       │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │
│  │ /api/manual │  │ /api/step  │  │ /api/check       │  │
│  │ (업로드/    │  │ (단계 생성) │  │ (완료 확인)      │  │
│  │  파싱/임베딩)│  │            │  │                  │  │
│  └─────┬──────┘  └─────┬──────┘  └────────┬─────────┘  │
│        │               │                   │             │
│        ▼               ▼                   ▼             │
│  ┌──────────┐   ┌──────────────────────────────────┐    │
│  │ ChromaDB  │   │         AI Models (OpenAI)       │    │
│  │ (Vector)  │──▶│  시스템 프롬프트 + 매뉴얼 청크   │    │
│  └──────────┘   │  + 화면 이미지 → 단계별 안내      │    │
│                  └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Manual Processing Pipeline (RAG)

### 3가지 지식 소스

1. **PDF 매뉴얼**: PyMuPDF(fitz)로 텍스트+이미지 추출
2. **URL (웹 문서)**: BeautifulSoup/Playwright로 크롤링, 하위 페이지 depth 2
3. **GitHub 리포지토리**: shallow clone → README/문서 우선 → AST 기반 코드 청크 분할

### 파이프라인

```
지식 소스 (PDF / URL / GitHub)
    ↓ 파싱
텍스트 추출 (+ 메타데이터: 섹션명, 페이지, 파일경로, 언어)
    ↓ 청크 분할
섹션/함수 기반 분할 (500~1000 토큰, 100 토큰 오버랩)
    ↓ 임베딩
OpenAI text-embedding-3-small
    ↓ 저장
ChromaDB (매뉴얼 ID별 컬렉션)
```

### 런타임 RAG

```
사용자 목표 + 현재 단계 → 쿼리 임베딩 → ChromaDB 유사도 검색 (top-k=5)
    ↓
관련 청크를 시스템 프롬프트에 삽입:
  - 매뉴얼/문서 청크: "## 참고 매뉴얼 내용" 섹션
  - 코드 청크: "## 참고 소스코드" 섹션 (파일경로, 언어 포함)
```

## Backend API Structure

```
api/
├── index.py                  # 메인 앱, CORS, 라우터 등록
├── routers/
│   ├── manual.py             # 매뉴얼 CRUD 엔드포인트
│   └── task.py               # step/check/help/coordinates
├── services/
│   ├── parser/
│   │   ├── pdf_parser.py     # PyMuPDF PDF 파싱
│   │   ├── url_parser.py     # BeautifulSoup 웹 크롤링
│   │   └── github_parser.py  # Git clone + 코드 분석
│   ├── embedder.py           # 청크 분할 + OpenAI 임베딩
│   ├── vectorstore.py        # ChromaDB 연동
│   └── rag.py                # RAG 쿼리 로직
├── utils/
│   ├── stream.py             # SSE 스트리밍
│   └── gemini.py             # Gemini API 변환
└── prompts/
    ├── action.py             # 단계 생성 (매뉴얼 컨텍스트 포함)
    ├── check.py              # 완료 확인
    └── help.py               # 팔로업 질문
```

### API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/manual/upload` | POST | PDF 업로드 → 파싱 → 임베딩 |
| `/api/manual/url` | POST | URL 크롤링 → 파싱 → 임베딩 |
| `/api/manual/github` | POST | GitHub 리포 → 코드 분석 → 임베딩 |
| `/api/manual/list` | GET | 등록된 지식 소스 목록 |
| `/api/manual/{id}` | DELETE | 지식 소스 삭제 |
| `/api/step` | POST | 단계 생성 (화면 + RAG) |
| `/api/check` | POST | 완료 확인 (before/after 이미지) |
| `/api/help` | POST | 팔로업 질문 응답 |
| `/api/coordinates` | POST | UI 요소 좌표 감지 |

## Frontend Structure

### Pages

```
app/
├── (home)/page.tsx           # 랜딩: 매뉴얼 등록 + 목표 입력
├── (task)/page.tsx           # 태스크 실행 (screen.vision 기반)
├── layout.tsx
└── providers/
    ├── TaskProvider.tsx       # 태스크 상태 관리
    ├── ManualProvider.tsx     # 매뉴얼 상태 관리
    └── SettingsProvider.tsx   # 설정
```

### Components

```
components/
├── manual/
│   ├── manual-upload.tsx     # PDF 드래그앤드롭 + URL/GitHub 입력
│   ├── manual-list.tsx       # 등록된 지식 소스 목록
│   └── manual-status.tsx     # 파싱/임베딩 진행률
├── task-screen/              # screen.vision 기반
│   ├── task-screen.tsx
│   ├── task-card.tsx
│   └── minimal-task-screen.tsx
├── multimodal-input.tsx
└── goal-input.tsx

hooks/
├── screenshare.tsx           # 화면 캡처 + 변화 감지
├── pip.tsx                   # Picture-in-Picture 윈도우
└── manual.tsx                # 매뉴얼 업로드/관리
```

## Data Models

```python
# 매뉴얼 (지식 소스) — data/manuals.json에 저장
Manual:
  id: str (UUID)
  name: str              # 매뉴얼 이름
  type: "pdf" | "url" | "github"
  source: str            # 원본 파일명, URL, GitHub URL
  status: "processing" | "ready" | "error"
  chunk_count: int
  created_at: datetime

# ChromaDB 청크 메타데이터
ChunkMetadata:
  manual_id: str
  source_type: "pdf" | "url" | "github"
  section: str           # 섹션명 / 파일경로
  page: int | None       # PDF 페이지
  language: str | None   # 코드 언어 (github)
  category: str          # "doc" | "code" | "config"
```

## Error Handling

| 시나리오 | 처리 |
|---|---|
| PDF 파싱 실패 | status="error", 프론트에 에러 메시지 |
| URL 크롤링 실패 | 재시도 1회, 실패 시 에러 |
| GitHub clone 실패 | public만 지원 안내 |
| 매뉴얼 없이 태스크 시작 | 경고 표시, screen.vision 모드로 폴백 |
| RAG 검색 결과 없음 | 매뉴얼 컨텍스트 없이 진행 |

## Environment Variables

```bash
# AI Models
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
GEMINI_API_KEY=...

# GeoLens 고유
CHROMADB_PATH=./data/chromadb
GITHUB_TOKEN=ghp_...              # optional, for private repos

# Frontend
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

## screen.vision에서 재사용하는 부분

- 화면 공유 (screenshare hook): 캡처, 스케일링, PiP 마스킹, 변화 감지
- PiP 윈도우 (pip hook): Document PiP + Safari 폴백
- 태스크 실행 UI: task-screen, task-card, multimodal-input
- SSE 스트리밍: stream.py, ai.ts의 readStream
- AI 프롬프트 구조: action/check/help (매뉴얼 컨텍스트 섹션 추가)
- 배포 구조: Vercel + Railway, Procfile

## GeoLens 고유 추가 부분

- 매뉴얼 업로드/관리 UI (manual/ 컴포넌트)
- ManualProvider (매뉴얼 상태 관리)
- 파서 모듈 (PDF, URL, GitHub)
- 임베딩/벡터스토어 모듈 (ChromaDB)
- RAG 검색 모듈
- 프롬프트에 매뉴얼 컨텍스트 삽입 로직
