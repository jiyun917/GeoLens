# GeoLens PySide6 Migration Design

## Overview

GeoLens를 웹 브라우저 기반(Next.js + FastAPI)에서 PySide6 데스크톱 애플리케이션으로 전환한다. 채팅 인터페이스를 통해 AI 가이드 기능을 제공하며, 특정 윈도우 캡처를 네이티브로 지원한다.

## Motivation

- 브라우저 화면 공유 허용 팝업 제거 → 즉시 캡처
- 특정 윈도우만 정확히 캡처 가능 (pygetwindow)
- PiP/마스킹 우회 로직 불필요
- 단일 exe 배포 가능 (pyinstaller)
- 시스템 트레이, always-on-top 등 네이티브 기능 활용

## Architecture

### Approach: Direct Call (FastAPI 제거)

FastAPI HTTP 레이어를 제거하고 `api/services/` 를 Python 함수로 직접 호출한다. 단일 프로세스.

```
PySide6 App (main.py)
├── QMainWindow (채팅 UI)
├── CaptureThread (mss + pygetwindow, 200ms 주기)
├── core/ (비즈니스 로직, 순수 함수)
│   ├── step.py    → OpenAI 스트리밍 + RAG
│   ├── check.py   → Gemini 비교
│   ├── help.py    → 후속 Q&A
│   └── coordinates.py → 클릭 좌표
└── api/services/  (기존 코드 그대로 재사용)
    ├── rag.py, embedder.py, vectorstore.py
    ├── manual_store.py
    └── parser/ (pdf, url, github)
```

### Why Direct Call over Embedded Server

- 웹 프론트엔드를 버리므로 SSE 프로토콜 유지 이유 없음
- `api/services/`는 이미 HTTP 무관한 순수 Python
- 단일 프로세스로 디버깅/배포 깔끔
- 의존성 감소 (uvicorn/fastapi 불필요)

## UI Layout

```
┌─────────────────────────────────────────────┐
│  GeoLens                           ─  □  ✕  │
├──────────────┬──────────────────────────────┤
│  좌측 패널    │  우측 채팅 영역               │
│  (250px)     │                              │
│              │  [스텝 카드 히스토리]           │
│  매뉴얼 관리  │  [현재 스텝 카드]              │
│  - PDF 업로드 │  [좌표 미리보기]               │
│  - URL 입력  │                              │
│  - GitHub    │  [질문 입력창]                 │
│  - 매뉴얼목록 │  [시작/새로고침 버튼]           │
│              │                              │
│  목표 입력    │                              │
│  캡처 설정    │                              │
│  - 윈도우선택 │                              │
│  - 상태표시  │                              │
├──────────────┴──────────────────────────────┤
│  상태바: Step 2/5 진행 중                     │
└─────────────────────────────────────────────┘
```

- 기본 크기: 900x600
- `Qt.WindowStaysOnTopHint` 토글 가능
- 시스템 트레이 최소화 지원

## Data Flow

1. **매뉴얼 업로드**: ManualWorker(QThread) → parser → embedder → ChromaDB
2. **스텝 생성**: StepWorker(QThread) → RAG 검색 → OpenAI 스트리밍 → Signal(`text_chunk`) → UI
3. **화면 변화 감지**: CaptureThread(200ms) → 픽셀 비교 → CheckWorker → Gemini → 자동 진행
4. **후속 질문**: StepWorker → OpenAI 스트리밍 → Signal → UI

## Threading Model

| Thread | Role | Signals |
|--------|------|---------|
| Main | UI 렌더링 | - |
| StepWorker | OpenAI 스트리밍 | `text_chunk(str)`, `step_complete(dict)`, `error(str)` |
| CheckWorker | Gemini 완료 확인 | `check_result(bool)` |
| CaptureThread | 윈도우 캡처 + 변화 감지 | `frame_captured(bytes)`, `change_detected(bytes, bytes)` |
| ManualWorker | 파싱/임베딩 | `progress(int)`, `complete(str)` |

## State Management

```python
class AppState:
    manuals: list[Manual]
    active_manual_ids: list[str]
    goal: str
    messages: list[dict]
    current_step: int
    capture_window: str | None
    is_capturing: bool
```

## Error Handling

| Scenario | Handling |
|----------|----------|
| API 키 없음/잘못됨 | 시작 시 .env 확인, 설정 다이얼로그에서 입력 |
| Gemini 키 없음 | 자동 감지 비활성화, 수동 "다음" 버튼 |
| 스트리밍 네트워크 오류 | 카드에 에러 표시 + 재시도 버튼 |
| 매뉴얼 파싱 실패 | 목록에서 실패 상태 + 에러 메시지 |
| 캡처 윈도우 닫힘 | 알림 + 윈도우 재선택 유도 |

## Testing

| Level | Target | Tool |
|-------|--------|------|
| Unit | core/, services/ | pytest + mock |
| Widget | UI components | pytest-qt |
| Integration | 매뉴얼→RAG→스텝 플로우 | pytest + fixture |

## Project Structure

```
GeoLens/
├── main.py                    # 앱 엔트리포인트
├── core/
│   ├── step.py
│   ├── check.py
│   ├── help.py
│   └── coordinates.py
├── ui/
│   ├── main_window.py
│   ├── widgets/
│   │   ├── chat_panel.py
│   │   ├── step_card.py
│   │   ├── manual_panel.py
│   │   ├── goal_input.py
│   │   └── capture_control.py
│   ├── workers/
│   │   ├── step_worker.py
│   │   ├── check_worker.py
│   │   ├── capture_thread.py
│   │   └── manual_worker.py
│   └── state.py
├── api/services/              # 기존 코드 유지
├── data/
├── .env
└── requirements.txt
```

### Removed (Web Code)

- `app/` (Next.js frontend)
- `api/routers/` (FastAPI routers)
- `api/utils/stream.py`, `api/utils/gemini.py` (SSE utils)
- `api/index.py` (FastAPI app)
- `package.json`, `next.config.js`, Node.js files

### Retained

- `api/services/*` (RAG, embedder, vectorstore, parsers, manual_store)
- `api/models.py` (Pydantic models)
