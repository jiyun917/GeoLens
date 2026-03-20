# PySide6 Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate GeoLens from a web app (Next.js + FastAPI) to a PySide6 desktop application with native window capture and direct Python service calls.

**Architecture:** Single-process PySide6 app. FastAPI/SSE layer removed. `api/services/` reused as-is. New `core/` layer wraps services into streaming generators. QThread workers emit Qt Signals for UI updates. `mss` + `pygetwindow` for native window capture.

**Tech Stack:** PySide6, mss, pygetwindow, OpenAI Python SDK, google-genai, ChromaDB, PyMuPDF, tiktoken

---

## Pre-requisites

- Python 3.12 with `uv` installed
- `.env` file with `OPENAI_API_KEY`, `GEMINI_API_KEY`
- Existing `data/` directory with ChromaDB data (or empty for fresh start)

---

### Task 1: Update dependencies and create directory structure

**Files:**
- Modify: `requirements.txt`
- Create: `core/__init__.py`
- Create: `ui/__init__.py`
- Create: `ui/widgets/__init__.py`
- Create: `ui/workers/__init__.py`

**Step 1: Update requirements.txt**

Remove web-only dependencies, add PySide6 and capture libraries:

```
# Remove these lines:
fastapi==0.115.9
slowapi==0.1.9
starlette==0.45.3
uvicorn==0.38.0
python-multipart==0.0.20
h11==0.16.0

# Add these lines:
PySide6==6.8.3
mss==10.0.0
pygetwindow==0.0.9
Pillow==11.1.0
```

Final `requirements.txt`:
```
annotated-types==0.7.0
anyio==4.11.0
certifi==2025.10.5
charset-normalizer==3.4.4
click==8.3.0
distro==1.9.0
httpcore==1.0.9
httpx==0.28.1
idna==3.11
jiter==0.11.1
openai==2.6.0
pydantic==2.12.3
pydantic_core==2.41.4
python-dotenv==1.1.1
requests==2.32.5
sniffio==1.3.1
tqdm==4.67.1
typing-inspection==0.4.2
typing_extensions==4.15.0
urllib3==2.5.0
google-genai==1.3.0
chromadb==1.0.7
PyMuPDF==1.25.3
beautifulsoup4==4.13.4
gitpython==3.1.44
tiktoken==0.9.0
PySide6==6.8.3
mss==10.0.0
pygetwindow==0.0.9
Pillow==11.1.0
```

**Step 2: Create directory structure**

```bash
mkdir -p core ui/widgets ui/workers
touch core/__init__.py ui/__init__.py ui/widgets/__init__.py ui/workers/__init__.py
```

**Step 3: Install dependencies**

```bash
uv pip install -r requirements.txt
```

**Step 4: Verify PySide6 imports**

```bash
uv run python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
uv run python -c "import mss; print('mss OK')"
uv run python -c "import pygetwindow; print('pygetwindow OK')"
```

Expected: All print OK.

**Step 5: Commit**

```bash
git add requirements.txt core/ ui/
git commit -m "chore: update deps for PySide6 migration, add directory structure"
```

---

### Task 2: Create core layer — step generation

Extract `/api/step` logic from `api/routers/task.py` into a pure generator function.

**Files:**
- Create: `core/step.py`
- Create: `tests/test_core_step.py`

**Step 1: Write the failing test**

```python
# tests/test_core_step.py
from unittest.mock import patch, MagicMock
from core.step import generate_step, extract_query_from_messages


def test_extract_query_from_messages_text():
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Click the save button"},
    ]
    assert extract_query_from_messages(messages) == "Click the save button"


def test_extract_query_from_messages_multipart():
    messages = [
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,abc"}},
            {"type": "text", "text": "What do I see?"},
        ]},
    ]
    assert extract_query_from_messages(messages) == "What do I see?"


def test_extract_query_no_user_message():
    messages = [{"role": "system", "content": "system"}]
    assert extract_query_from_messages(messages) == ""


@patch("core.step.get_manual_context")
@patch("core.step.OpenAI")
def test_generate_step_yields_text(mock_openai_cls, mock_rag):
    mock_rag.return_value = "[Source: test]\nSome manual content"

    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Click here"
    mock_chunk.choices[0].finish_reason = None

    mock_done = MagicMock()
    mock_done.choices = [MagicMock()]
    mock_done.choices[0].delta.content = None
    mock_done.choices[0].finish_reason = "stop"

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = iter([mock_chunk, mock_done])
    mock_openai_cls.return_value = mock_client

    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "How to save?"},
    ]
    chunks = list(generate_step(messages, manual_ids=["m1"]))
    assert "Click here" in chunks
    mock_rag.assert_called_once_with(["m1"], "How to save?")


@patch("core.step.OpenAI")
def test_generate_step_no_manuals(mock_openai_cls):
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Hello"
    mock_chunk.choices[0].finish_reason = None

    mock_done = MagicMock()
    mock_done.choices = [MagicMock()]
    mock_done.choices[0].delta.content = None
    mock_done.choices[0].finish_reason = "stop"

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = iter([mock_chunk, mock_done])
    mock_openai_cls.return_value = mock_client

    chunks = list(generate_step([{"role": "user", "content": "Hi"}]))
    assert "Hello" in chunks
```

**Step 2: Run test to verify it fails**

```bash
uv run python -m pytest tests/test_core_step.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'core.step'`

**Step 3: Write minimal implementation**

```python
# core/step.py
"""Step generation: OpenAI streaming with optional RAG context."""
import copy
from typing import Generator, List, Optional

from openai import OpenAI

from api.services.rag import get_manual_context


def extract_query_from_messages(messages: list) -> str:
    """Extract the last user message text for RAG query."""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        return part.get("text", "")
            return ""
    return ""


def _inject_rag_context(messages: list, manual_ids: List[str]) -> list:
    """Inject RAG context into the system message. Returns a new list."""
    messages = copy.deepcopy(messages)
    query = extract_query_from_messages(messages)
    if not query:
        return messages

    context = get_manual_context(manual_ids, query)
    if not context:
        return messages

    context_block = (
        "\n\n--- Reference Manual Context ---\n"
        f"{context}\n"
        "--- End Reference Manual Context ---\n"
    )

    for msg in messages:
        if msg.get("role") == "system":
            if isinstance(msg["content"], str):
                msg["content"] += context_block
            elif isinstance(msg["content"], list):
                msg["content"].append({"type": "text", "text": context_block})
            return messages

    messages.insert(0, {"role": "system", "content": context_block})
    return messages


def generate_step(
    messages: list,
    manual_ids: Optional[List[str]] = None,
) -> Generator[str, None, None]:
    """
    Generate a step instruction via OpenAI streaming.
    Yields text chunks as they arrive.
    """
    if manual_ids:
        messages = _inject_rag_context(messages, manual_ids)

    client = OpenAI()
    stream = client.chat.completions.create(
        messages=messages,
        model="gpt-5-mini-2025-08-07",
        stream=True,
        reasoning_effort="low",
    )

    for chunk in stream:
        for choice in chunk.choices:
            if choice.delta and choice.delta.content:
                yield choice.delta.content
```

**Step 4: Run test to verify it passes**

```bash
uv run python -m pytest tests/test_core_step.py -v
```

Expected: All 5 tests PASS.

**Step 5: Commit**

```bash
git add core/step.py tests/test_core_step.py
git commit -m "feat: add core/step.py — step generation with RAG"
```

---

### Task 3: Create core layer — check, help, coordinates

**Files:**
- Create: `core/check.py`
- Create: `core/help.py`
- Create: `core/coordinates.py`
- Create: `tests/test_core_check.py`

**Step 1: Write the failing test for check**

```python
# tests/test_core_check.py
from unittest.mock import patch, MagicMock
from core.check import check_step_completion


@patch("core.check._get_gemini_client")
def test_check_returns_bool(mock_get_client):
    mock_chunk = MagicMock()
    mock_chunk.text = "Yes"
    mock_stream = iter([mock_chunk])

    mock_client = MagicMock()
    mock_client.models.generate_content_stream.return_value = mock_stream
    mock_get_client.return_value = mock_client

    messages = [
        {"role": "system", "content": "Check if the step is done."},
        {"role": "user", "content": [
            {"type": "text", "text": "Is it done?"},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,abc"}},
        ]},
    ]
    result = check_step_completion(messages)
    assert result is True


@patch("core.check._get_gemini_client")
def test_check_returns_false_for_no(mock_get_client):
    mock_chunk = MagicMock()
    mock_chunk.text = "No"
    mock_stream = iter([mock_chunk])

    mock_client = MagicMock()
    mock_client.models.generate_content_stream.return_value = mock_stream
    mock_get_client.return_value = mock_client

    messages = [{"role": "user", "content": "Check"}]
    result = check_step_completion(messages)
    assert result is False
```

**Step 2: Run test to verify it fails**

```bash
uv run python -m pytest tests/test_core_check.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement core/check.py, core/help.py, core/coordinates.py**

```python
# core/check.py
"""Step completion check via Gemini."""
import os
from typing import List, Optional

from google import genai
from google.genai import types

from api.utils.gemini import convert_openai_to_gemini


def _get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required")
    return genai.Client(vertexai=True, api_key=api_key)


def _extract_system_instruction(messages: list) -> Optional[types.Content]:
    parts = []
    for msg in messages:
        if msg.get("role") == "system":
            content = msg.get("content")
            if isinstance(content, str):
                parts.append(types.Part.from_text(text=content))
            elif isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        parts.append(types.Part.from_text(text=part.get("text")))
    return types.Content(parts=parts) if parts else None


def check_step_completion(messages: list) -> bool:
    """
    Send before/after screenshots to Gemini and return True if step is complete.
    """
    client = _get_gemini_client()
    system_instruction = _extract_system_instruction(messages)
    contents = convert_openai_to_gemini(messages)

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
    )

    stream = client.models.generate_content_stream(
        model="gemini-3-flash-preview",
        contents=contents,
        config=config,
    )

    full_text = ""
    for chunk in stream:
        if chunk.text:
            full_text += chunk.text

    return full_text.strip().lower().startswith("yes")
```

```python
# core/help.py
"""Follow-up Q&A via OpenAI streaming."""
from typing import Generator

from openai import OpenAI


def generate_help(messages: list) -> Generator[str, None, None]:
    """Stream a help response. Yields text chunks."""
    client = OpenAI()
    stream = client.chat.completions.create(
        messages=messages,
        model="gpt-5-mini-2025-08-07",
        stream=True,
        reasoning_effort="low",
    )

    for chunk in stream:
        for choice in chunk.choices:
            if choice.delta and choice.delta.content:
                yield choice.delta.content
```

```python
# core/coordinates.py
"""Click target coordinate detection via Gemini."""
import os
from typing import Optional, Tuple

from google import genai
from google.genai import types

from api.utils.gemini import convert_openai_to_gemini


def _get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required")
    return genai.Client(vertexai=True, api_key=api_key)


def _extract_system_instruction(messages: list) -> Optional[types.Content]:
    parts = []
    for msg in messages:
        if msg.get("role") == "system":
            content = msg.get("content")
            if isinstance(content, str):
                parts.append(types.Part.from_text(text=content))
            elif isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        parts.append(types.Part.from_text(text=part.get("text")))
    return types.Content(parts=parts) if parts else None


def detect_coordinates(messages: list) -> Optional[Tuple[int, int]]:
    """
    Detect click target coordinates from screenshot.
    Returns (x, y) tuple or None if not found.
    """
    client = _get_gemini_client()
    system_instruction = _extract_system_instruction(messages)
    contents = convert_openai_to_gemini(messages)

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
    )

    stream = client.models.generate_content_stream(
        model="gemini-3-flash-preview",
        contents=contents,
        config=config,
    )

    full_text = ""
    for chunk in stream:
        if chunk.text:
            full_text += chunk.text

    text = full_text.strip()
    if text.lower() == "none":
        return None

    try:
        parts = text.split(",")
        return (int(parts[0].strip()), int(parts[1].strip()))
    except (ValueError, IndexError):
        return None
```

**Step 4: Run tests**

```bash
uv run python -m pytest tests/test_core_check.py -v
```

Expected: All PASS.

**Step 5: Commit**

```bash
git add core/check.py core/help.py core/coordinates.py tests/test_core_check.py
git commit -m "feat: add core check/help/coordinates modules"
```

---

### Task 4: Create app state management

**Files:**
- Create: `ui/state.py`
- Create: `tests/test_state.py`

**Step 1: Write the failing test**

```python
# tests/test_state.py
from ui.state import AppState


def test_initial_state():
    state = AppState()
    assert state.manuals == []
    assert state.active_manual_ids == []
    assert state.goal == ""
    assert state.messages == []
    assert state.current_step == 0
    assert state.capture_window is None
    assert state.is_capturing is False


def test_add_message():
    state = AppState()
    state.add_message("user", "Hello")
    assert len(state.messages) == 1
    assert state.messages[0] == {"role": "user", "content": "Hello"}


def test_reset():
    state = AppState()
    state.goal = "test"
    state.current_step = 5
    state.add_message("user", "hi")
    state.reset_session()
    assert state.goal == ""
    assert state.current_step == 0
    assert state.messages == []
```

**Step 2: Run test to verify it fails**

```bash
uv run python -m pytest tests/test_state.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement**

```python
# ui/state.py
"""Application state management."""
from dataclasses import dataclass, field
from typing import Any, List, Optional

from api.models import Manual


@dataclass
class AppState:
    manuals: List[Manual] = field(default_factory=list)
    active_manual_ids: List[str] = field(default_factory=list)
    goal: str = ""
    messages: List[dict] = field(default_factory=list)
    current_step: int = 0
    capture_window: Optional[str] = None
    is_capturing: bool = False

    def add_message(self, role: str, content: Any):
        self.messages.append({"role": role, "content": content})

    def reset_session(self):
        """Reset session state (keeps manuals)."""
        self.goal = ""
        self.messages.clear()
        self.current_step = 0
        self.is_capturing = False
```

**Step 4: Run tests**

```bash
uv run python -m pytest tests/test_state.py -v
```

Expected: All PASS.

**Step 5: Commit**

```bash
git add ui/state.py tests/test_state.py
git commit -m "feat: add AppState for session management"
```

---

### Task 5: Create QThread workers

**Files:**
- Create: `ui/workers/step_worker.py`
- Create: `ui/workers/check_worker.py`
- Create: `ui/workers/capture_thread.py`
- Create: `ui/workers/manual_worker.py`

**Step 1: Implement step_worker.py**

```python
# ui/workers/step_worker.py
"""QThread worker for streaming step generation."""
from typing import List, Optional

from PySide6.QtCore import QThread, Signal

from core.step import generate_step


class StepWorker(QThread):
    text_chunk = Signal(str)
    finished_text = Signal(str)  # full accumulated text
    error = Signal(str)

    def __init__(self, messages: list, manual_ids: Optional[List[str]] = None):
        super().__init__()
        self._messages = messages
        self._manual_ids = manual_ids

    def run(self):
        try:
            full_text = ""
            for chunk in generate_step(self._messages, self._manual_ids):
                full_text += chunk
                self.text_chunk.emit(chunk)
            self.finished_text.emit(full_text)
        except Exception as e:
            self.error.emit(str(e))
```

**Step 2: Implement check_worker.py**

```python
# ui/workers/check_worker.py
"""QThread worker for step completion check."""
from PySide6.QtCore import QThread, Signal

from core.check import check_step_completion


class CheckWorker(QThread):
    check_result = Signal(bool)
    error = Signal(str)

    def __init__(self, messages: list):
        super().__init__()
        self._messages = messages

    def run(self):
        try:
            result = check_step_completion(self._messages)
            self.check_result.emit(result)
        except Exception as e:
            self.error.emit(str(e))
```

**Step 3: Implement capture_thread.py**

```python
# ui/workers/capture_thread.py
"""QThread for periodic window capture and change detection."""
import io
import time

import mss
import pygetwindow as gw
from PIL import Image
from PySide6.QtCore import QThread, Signal


class CaptureThread(QThread):
    frame_captured = Signal(bytes)  # JPEG bytes of current frame
    change_detected = Signal(bytes, bytes)  # before, after JPEG bytes
    error = Signal(str)

    CAPTURE_INTERVAL_MS = 200
    CHANGE_THRESHOLD = 0.01  # 1% pixel difference

    def __init__(self, window_title: str):
        super().__init__()
        self._window_title = window_title
        self._running = False

    def run(self):
        self._running = True
        prev_frame = None

        with mss.mss() as sct:
            while self._running:
                try:
                    frame = self._capture_window(sct)
                    if frame is None:
                        time.sleep(self.CAPTURE_INTERVAL_MS / 1000)
                        continue

                    jpeg_bytes = self._to_jpeg(frame)
                    self.frame_captured.emit(jpeg_bytes)

                    if prev_frame is not None:
                        if self._has_changed(prev_frame, frame):
                            prev_jpeg = self._to_jpeg(prev_frame)
                            self.change_detected.emit(prev_jpeg, jpeg_bytes)

                    prev_frame = frame

                except Exception as e:
                    self.error.emit(str(e))

                time.sleep(self.CAPTURE_INTERVAL_MS / 1000)

    def stop(self):
        self._running = False

    def _capture_window(self, sct) -> Image.Image | None:
        """Capture the target window region."""
        try:
            windows = gw.getWindowsWithTitle(self._window_title)
            if not windows:
                return None
            win = windows[0]
            if win.isMinimized:
                return None
            region = {
                "left": win.left,
                "top": win.top,
                "width": win.width,
                "height": win.height,
            }
            screenshot = sct.grab(region)
            return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        except Exception:
            return None

    @staticmethod
    def _to_jpeg(image: Image.Image) -> bytes:
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=75)
        return buf.getvalue()

    @staticmethod
    def _has_changed(prev: Image.Image, curr: Image.Image) -> bool:
        """Simple pixel-diff change detection."""
        if prev.size != curr.size:
            return True
        prev_pixels = prev.tobytes()
        curr_pixels = curr.tobytes()
        diff_count = sum(1 for a, b in zip(prev_pixels, curr_pixels) if abs(a - b) > 10)
        total = len(prev_pixels)
        return (diff_count / total) > CaptureThread.CHANGE_THRESHOLD
```

**Step 4: Implement manual_worker.py**

```python
# ui/workers/manual_worker.py
"""QThread worker for manual processing (parse + embed)."""
import os
import shutil

from PySide6.QtCore import QThread, Signal

from api.models import Manual
from api.services import manual_store
from api.services.embedder import embed_and_store
from api.services.parser.pdf_parser import parse_pdf
from api.services.parser.url_parser import parse_url
from api.services.parser.github_parser import parse_github


UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "uploads",
)


class ManualWorker(QThread):
    progress = Signal(str)  # status message
    complete = Signal(Manual)
    error = Signal(str, str)  # manual_id, error message

    def __init__(self, manual: Manual, file_path: str = ""):
        super().__init__()
        self._manual = manual
        self._file_path = file_path

    def run(self):
        try:
            self.progress.emit(f"Processing {self._manual.name}...")

            if self._manual.type == "pdf":
                content_pieces = parse_pdf(self._file_path)
            elif self._manual.type == "url":
                content_pieces = parse_url(self._manual.source)
            elif self._manual.type == "github":
                content_pieces = parse_github(self._manual.source)
            else:
                raise ValueError(f"Unknown manual type: {self._manual.type}")

            self.progress.emit(f"Embedding {self._manual.name}...")
            embed_and_store(self._manual.id, content_pieces)

            updated = manual_store.get_manual(self._manual.id)
            if updated:
                self.complete.emit(updated)
            else:
                self.complete.emit(self._manual)

        except Exception as e:
            manual_store.update_manual(
                self._manual.id, status="error", error_message=str(e)
            )
            self.error.emit(self._manual.id, str(e))
```

**Step 5: Verify imports**

```bash
uv run python -c "from ui.workers.step_worker import StepWorker; print('OK')"
uv run python -c "from ui.workers.check_worker import CheckWorker; print('OK')"
uv run python -c "from ui.workers.capture_thread import CaptureThread; print('OK')"
uv run python -c "from ui.workers.manual_worker import ManualWorker; print('OK')"
```

Expected: All print OK.

**Step 6: Commit**

```bash
git add ui/workers/
git commit -m "feat: add QThread workers for step/check/capture/manual"
```

---

### Task 6: Create manual panel widget

**Files:**
- Create: `ui/widgets/manual_panel.py`

**Step 1: Implement**

```python
# ui/widgets/manual_panel.py
"""Left-side manual management panel: upload, list, delete."""
import os
import shutil

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QFileDialog,
    QHBoxLayout, QMessageBox,
)

from api.models import Manual
from api.services import manual_store, vectorstore
from ui.workers.manual_worker import ManualWorker, UPLOAD_DIR


class ManualPanel(QWidget):
    manual_added = Signal(Manual)
    manual_removed = Signal(str)  # manual_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._workers: list[ManualWorker] = []
        self._init_ui()
        self._refresh_list()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Title
        title = QLabel("Manuals")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Upload tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_pdf_tab(), "PDF")
        tabs.addTab(self._create_url_tab(), "URL")
        tabs.addTab(self._create_github_tab(), "GitHub")
        layout.addWidget(tabs)

        # Manual list
        self._list_widget = QListWidget()
        layout.addWidget(self._list_widget)

    def _create_pdf_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        btn = QPushButton("Select PDF File...")
        btn.clicked.connect(self._on_upload_pdf)
        layout.addWidget(btn)
        return w

    def _create_url_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://docs.example.com")
        layout.addWidget(self._url_input)
        btn = QPushButton("Add URL")
        btn.clicked.connect(self._on_add_url)
        layout.addWidget(btn)
        return w

    def _create_github_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        self._github_input = QLineEdit()
        self._github_input.setPlaceholderText("https://github.com/user/repo")
        layout.addWidget(self._github_input)
        btn = QPushButton("Add Repo")
        btn.clicked.connect(self._on_add_github)
        layout.addWidget(btn)
        return w

    def _on_upload_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        name = os.path.basename(path)
        manual = Manual.new(name=name, type="pdf", source=path)
        dest = os.path.join(UPLOAD_DIR, f"{manual.id}_{name}")
        shutil.copy2(path, dest)
        manual.source = dest
        manual_store.add_manual(manual)
        self._start_processing(manual, file_path=dest)

    def _on_add_url(self):
        url = self._url_input.text().strip()
        if not url:
            return
        manual = Manual.new(name=url, type="url", source=url)
        manual_store.add_manual(manual)
        self._url_input.clear()
        self._start_processing(manual)

    def _on_add_github(self):
        url = self._github_input.text().strip()
        if not url:
            return
        manual = Manual.new(name=url, type="github", source=url)
        manual_store.add_manual(manual)
        self._github_input.clear()
        self._start_processing(manual)

    def _start_processing(self, manual: Manual, file_path: str = ""):
        worker = ManualWorker(manual, file_path)
        worker.complete.connect(self._on_worker_complete)
        worker.error.connect(self._on_worker_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        self._workers.append(worker)
        worker.start()
        self._refresh_list()

    def _on_worker_complete(self, manual: Manual):
        self.manual_added.emit(manual)
        self._refresh_list()

    def _on_worker_error(self, manual_id: str, error: str):
        QMessageBox.warning(self, "Processing Error", f"Failed to process manual: {error}")
        self._refresh_list()

    def _cleanup_worker(self, worker: ManualWorker):
        if worker in self._workers:
            self._workers.remove(worker)

    def _refresh_list(self):
        self._list_widget.clear()
        manuals = manual_store.load_manuals()
        for m in manuals:
            status = {"processing": "...", "ready": "OK", "error": "ERR"}.get(m.status, "?")
            item_widget = QWidget()
            h = QHBoxLayout(item_widget)
            h.setContentsMargins(4, 2, 4, 2)
            h.addWidget(QLabel(f"[{status}] {m.name}"))
            h.addStretch()
            del_btn = QPushButton("X")
            del_btn.setFixedSize(24, 24)
            del_btn.clicked.connect(lambda checked, mid=m.id: self._delete_manual(mid))
            h.addWidget(del_btn)

            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            item.setData(256, m.id)  # Qt.UserRole
            self._list_widget.addItem(item)
            self._list_widget.setItemWidget(item, item_widget)

    def _delete_manual(self, manual_id: str):
        manual = manual_store.get_manual(manual_id)
        if manual:
            vectorstore.delete_collection(manual_id)
            if manual.type == "pdf" and manual.source and os.path.exists(manual.source):
                try:
                    os.remove(manual.source)
                except Exception:
                    pass
            manual_store.delete_manual(manual_id)
            self.manual_removed.emit(manual_id)
        self._refresh_list()

    def get_manual_ids(self) -> list[str]:
        """Return IDs of all ready manuals."""
        return [m.id for m in manual_store.load_manuals() if m.status == "ready"]
```

**Step 2: Verify import**

```bash
uv run python -c "from ui.widgets.manual_panel import ManualPanel; print('OK')"
```

**Step 3: Commit**

```bash
git add ui/widgets/manual_panel.py
git commit -m "feat: add ManualPanel widget"
```

---

### Task 7: Create step card and chat panel widgets

**Files:**
- Create: `ui/widgets/step_card.py`
- Create: `ui/widgets/chat_panel.py`
- Create: `ui/widgets/goal_input.py`
- Create: `ui/widgets/capture_control.py`

**Step 1: Implement step_card.py**

```python
# ui/widgets/step_card.py
"""Individual step card widget for the chat area."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QHBoxLayout,
)


class StepCard(QFrame):
    def __init__(self, step_number: int, parent=None):
        super().__init__(parent)
        self._step_number = step_number
        self._text = ""
        self._status = "active"  # active, completed, error
        self._init_ui()

    def _init_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            StepCard {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        # Header
        header = QHBoxLayout()
        self._title_label = QLabel(f"Step {self._step_number}")
        self._title_label.setStyleSheet("font-weight: bold; color: #495057;")
        header.addWidget(self._title_label)

        self._status_label = QLabel("")
        header.addStretch()
        header.addWidget(self._status_label)
        layout.addLayout(header)

        # Content
        self._content_label = QLabel("")
        self._content_label.setWordWrap(True)
        self._content_label.setStyleSheet("color: #212529; font-size: 13px;")
        layout.addWidget(self._content_label)

    def append_text(self, text: str):
        self._text += text
        self._content_label.setText(self._text)

    def set_text(self, text: str):
        self._text = text
        self._content_label.setText(text)

    def set_completed(self):
        self._status = "completed"
        self._status_label.setText("Done")
        self._status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        self.setStyleSheet("""
            StepCard {
                background: #f0fff4;
                border: 1px solid #c3e6cb;
                border-radius: 8px;
                padding: 12px;
            }
        """)

    def set_error(self, msg: str):
        self._status = "error"
        self._status_label.setText("Error")
        self._status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        self._content_label.setText(msg)
```

**Step 2: Implement chat_panel.py**

```python
# ui/widgets/chat_panel.py
"""Right-side chat panel: step cards + input."""
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLineEdit,
    QHBoxLayout, QPushButton,
)

from ui.widgets.step_card import StepCard


class ChatPanel(QWidget):
    start_requested = Signal()
    refresh_requested = Signal()
    question_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: list[StepCard] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Scrollable card area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_content)
        self._scroll_layout.setAlignment(Qt.AlignTop)
        self._scroll.setWidget(self._scroll_content)
        layout.addWidget(self._scroll, 1)

        # Input area
        input_layout = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask a follow-up question...")
        self._input.returnPressed.connect(self._on_submit_question)
        input_layout.addWidget(self._input)
        layout.addLayout(input_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self._start_btn = QPushButton("Start")
        self._start_btn.clicked.connect(self.start_requested.emit)
        btn_layout.addWidget(self._start_btn)

        self._refresh_btn = QPushButton("Refresh Step")
        self._refresh_btn.clicked.connect(self.refresh_requested.emit)
        btn_layout.addWidget(self._refresh_btn)
        layout.addLayout(btn_layout)

    def add_step_card(self, step_number: int) -> StepCard:
        card = StepCard(step_number)
        self._cards.append(card)
        self._scroll_layout.addWidget(card)
        # Auto-scroll to bottom
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )
        return card

    def get_current_card(self) -> StepCard | None:
        return self._cards[-1] if self._cards else None

    def complete_current_card(self):
        card = self.get_current_card()
        if card:
            card.set_completed()

    def clear_cards(self):
        for card in self._cards:
            self._scroll_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

    def _on_submit_question(self):
        text = self._input.text().strip()
        if text:
            self.question_submitted.emit(text)
            self._input.clear()
```

**Step 3: Implement goal_input.py**

```python
# ui/widgets/goal_input.py
"""Goal input widget."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit


class GoalInput(QWidget):
    goal_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)

        label = QLabel("Goal")
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(label)

        self._input = QLineEdit()
        self._input.setPlaceholderText("What do you want to accomplish?")
        self._input.textChanged.connect(self.goal_changed.emit)
        layout.addWidget(self._input)

    def get_goal(self) -> str:
        return self._input.text().strip()
```

**Step 4: Implement capture_control.py**

```python
# ui/widgets/capture_control.py
"""Capture window selection and status control."""
import pygetwindow as gw

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout,
)


class CaptureControl(QWidget):
    capture_started = Signal(str)  # window title
    capture_stopped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)

        label = QLabel("Screen Capture")
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(label)

        # Window selector
        selector_layout = QHBoxLayout()
        self._combo = QComboBox()
        self._combo.setMinimumWidth(150)
        selector_layout.addWidget(self._combo)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(60)
        refresh_btn.clicked.connect(self._refresh_windows)
        selector_layout.addWidget(refresh_btn)
        layout.addLayout(selector_layout)

        # Status
        self._status_label = QLabel("Not capturing")
        self._status_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        layout.addWidget(self._status_label)

        self._refresh_windows()

    def _refresh_windows(self):
        self._combo.clear()
        titles = [t for t in gw.getAllTitles() if t.strip()]
        titles = sorted(set(titles))
        self._combo.addItems(titles)

    def get_selected_window(self) -> str | None:
        return self._combo.currentText() or None

    def set_status(self, capturing: bool):
        if capturing:
            self._status_label.setText("Capturing...")
            self._status_label.setStyleSheet("color: #28a745; font-size: 12px;")
        else:
            self._status_label.setText("Not capturing")
            self._status_label.setStyleSheet("color: #6c757d; font-size: 12px;")
```

**Step 5: Verify all imports**

```bash
uv run python -c "from ui.widgets.step_card import StepCard; print('OK')"
uv run python -c "from ui.widgets.chat_panel import ChatPanel; print('OK')"
uv run python -c "from ui.widgets.goal_input import GoalInput; print('OK')"
uv run python -c "from ui.widgets.capture_control import CaptureControl; print('OK')"
```

**Step 6: Commit**

```bash
git add ui/widgets/
git commit -m "feat: add chat panel, step card, goal input, capture control widgets"
```

---

### Task 8: Create main window

**Files:**
- Create: `ui/main_window.py`

**Step 1: Implement**

```python
# ui/main_window.py
"""Main application window: orchestrates all panels and workers."""
import base64

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QStatusBar, QMessageBox, QPushButton,
)

from ui.state import AppState
from ui.widgets.manual_panel import ManualPanel
from ui.widgets.chat_panel import ChatPanel
from ui.widgets.goal_input import GoalInput
from ui.widgets.capture_control import CaptureControl
from ui.widgets.step_card import StepCard
from ui.workers.step_worker import StepWorker
from ui.workers.check_worker import CheckWorker
from ui.workers.capture_thread import CaptureThread

from lib.prompts.action import build_action_prompt
from lib.prompts.check import build_check_prompt


STEP_LIMIT = 150


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._state = AppState()
        self._step_worker: StepWorker | None = None
        self._check_worker: CheckWorker | None = None
        self._capture_thread: CaptureThread | None = None
        self._current_card: StepCard | None = None
        self._last_frame: bytes | None = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("GeoLens")
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)

        splitter = QSplitter(Qt.Horizontal)

        # Left panel
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self._manual_panel = ManualPanel()
        left_layout.addWidget(self._manual_panel)

        self._goal_input = GoalInput()
        left_layout.addWidget(self._goal_input)

        self._capture_control = CaptureControl()
        left_layout.addWidget(self._capture_control)

        left_layout.addStretch()

        # Always-on-top toggle
        self._aot_btn = QPushButton("Pin on Top")
        self._aot_btn.setCheckable(True)
        self._aot_btn.toggled.connect(self._toggle_always_on_top)
        left_layout.addWidget(self._aot_btn)

        left.setFixedWidth(250)
        splitter.addWidget(left)

        # Right panel
        self._chat_panel = ChatPanel()
        splitter.addWidget(self._chat_panel)

        layout = QHBoxLayout(central)
        layout.addWidget(splitter)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")

        # Connect signals
        self._chat_panel.start_requested.connect(self._on_start)
        self._chat_panel.refresh_requested.connect(self._on_refresh_step)
        self._chat_panel.question_submitted.connect(self._on_question)

    def _toggle_always_on_top(self, checked: bool):
        flags = self.windowFlags()
        if checked:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        self.show()

    def _on_start(self):
        goal = self._goal_input.get_goal()
        if not goal:
            QMessageBox.warning(self, "No Goal", "Please enter a goal first.")
            return

        window = self._capture_control.get_selected_window()
        if not window:
            QMessageBox.warning(self, "No Window", "Please select a capture window.")
            return

        # Reset session
        self._state.reset_session()
        self._state.goal = goal
        self._state.capture_window = window
        self._state.active_manual_ids = self._manual_panel.get_manual_ids()
        self._chat_panel.clear_cards()

        # Start capture
        self._start_capture(window)

        # Generate first step
        self._generate_next_step()

    def _start_capture(self, window_title: str):
        if self._capture_thread:
            self._capture_thread.stop()
            self._capture_thread.wait()

        self._capture_thread = CaptureThread(window_title)
        self._capture_thread.frame_captured.connect(self._on_frame_captured)
        self._capture_thread.change_detected.connect(self._on_change_detected)
        self._capture_thread.error.connect(self._on_capture_error)
        self._capture_thread.start()
        self._state.is_capturing = True
        self._capture_control.set_status(True)

    def _on_frame_captured(self, jpeg_bytes: bytes):
        self._last_frame = jpeg_bytes

    def _on_change_detected(self, before: bytes, after: bytes):
        if self._check_worker and self._check_worker.isRunning():
            return  # Already checking

        # Build check messages
        before_b64 = base64.b64encode(before).decode()
        after_b64 = base64.b64encode(after).decode()
        current_text = self._current_card._text if self._current_card else ""

        messages = build_check_prompt(before_b64, after_b64, current_text)

        self._check_worker = CheckWorker(messages)
        self._check_worker.check_result.connect(self._on_check_result)
        self._check_worker.error.connect(lambda e: self._status_bar.showMessage(f"Check error: {e}"))
        self._check_worker.start()

    def _on_check_result(self, completed: bool):
        if completed:
            self._chat_panel.complete_current_card()
            self._state.current_step += 1
            if self._state.current_step < STEP_LIMIT:
                self._generate_next_step()
            else:
                self._status_bar.showMessage("Step limit reached!")

    def _generate_next_step(self):
        step_num = self._state.current_step + 1
        self._current_card = self._chat_panel.add_step_card(step_num)
        self._status_bar.showMessage(f"Generating step {step_num}...")

        # Build messages with screenshot
        screenshot_b64 = ""
        if self._last_frame:
            screenshot_b64 = base64.b64encode(self._last_frame).decode()

        messages = self._build_step_messages(screenshot_b64)

        self._step_worker = StepWorker(messages, self._state.active_manual_ids)
        self._step_worker.text_chunk.connect(self._on_step_chunk)
        self._step_worker.finished_text.connect(self._on_step_done)
        self._step_worker.error.connect(self._on_step_error)
        self._step_worker.start()

    def _build_step_messages(self, screenshot_b64: str) -> list:
        """Build the message array for step generation."""
        system_content = build_action_prompt(self._state.goal)

        messages = [{"role": "system", "content": system_content}]

        # Add conversation history
        messages.extend(self._state.messages)

        # Add current screenshot as user message
        user_content = []
        if screenshot_b64:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"},
            })
        user_content.append({"type": "text", "text": "What should I do next?"})

        messages.append({"role": "user", "content": user_content})
        return messages

    def _on_step_chunk(self, text: str):
        if self._current_card:
            self._current_card.append_text(text)

    def _on_step_done(self, full_text: str):
        self._state.add_message("assistant", full_text)
        self._status_bar.showMessage(
            f"Step {self._state.current_step + 1} ready"
        )

    def _on_step_error(self, error: str):
        if self._current_card:
            self._current_card.set_error(f"Error: {error}")
        self._status_bar.showMessage(f"Error: {error}")

    def _on_refresh_step(self):
        if self._current_card:
            self._current_card.set_text("")
            screenshot_b64 = ""
            if self._last_frame:
                screenshot_b64 = base64.b64encode(self._last_frame).decode()
            messages = self._build_step_messages(screenshot_b64)
            self._step_worker = StepWorker(messages, self._state.active_manual_ids)
            self._step_worker.text_chunk.connect(self._on_step_chunk)
            self._step_worker.finished_text.connect(self._on_step_done)
            self._step_worker.error.connect(self._on_step_error)
            self._step_worker.start()

    def _on_question(self, question: str):
        """Handle follow-up question."""
        from core.help import generate_help
        from ui.workers.step_worker import StepWorker

        card = self._chat_panel.add_step_card(0)  # 0 = Q&A card
        card._title_label.setText("Q&A")

        help_messages = list(self._state.messages)
        help_messages.append({"role": "user", "content": question})

        worker = StepWorker(help_messages)  # Reuse StepWorker pattern
        worker.text_chunk.connect(card.append_text)
        worker.error.connect(lambda e: card.set_error(e))
        worker.start()
        self._step_worker = worker  # Keep reference

    def _on_capture_error(self, error: str):
        self._status_bar.showMessage(f"Capture error: {error}")

    def closeEvent(self, event):
        if self._capture_thread:
            self._capture_thread.stop()
            self._capture_thread.wait()
        event.accept()
```

**Step 2: Verify import**

```bash
uv run python -c "from ui.main_window import MainWindow; print('OK')"
```

Note: This may fail if `lib/prompts/` imports aren't resolvable. Those will be handled in Task 9.

**Step 3: Commit**

```bash
git add ui/main_window.py
git commit -m "feat: add MainWindow orchestrating all panels and workers"
```

---

### Task 9: Create prompt builders (port from TypeScript)

The frontend's `lib/prompts/*.ts` need Python equivalents for the PySide6 app.

**Files:**
- Create: `core/prompts.py`

**Step 1: Read existing TypeScript prompts to understand structure**

Check these files:
- `lib/prompts/action.ts`
- `lib/prompts/check.ts`
- `lib/prompts/coordinate.ts`
- `lib/prompts/help.ts`

**Step 2: Implement Python equivalents**

```python
# core/prompts.py
"""Prompt builders ported from lib/prompts/*.ts."""


def build_action_prompt(goal: str, manual_context: str = "") -> str:
    """Build system prompt for step generation."""
    prompt = (
        "You are an AI assistant helping a user accomplish a task on their computer. "
        "The user will share their screen and you will guide them step by step.\n\n"
        f"User's goal: {goal}\n\n"
        "Instructions:\n"
        "- Give ONE clear, specific instruction at a time\n"
        "- Reference exact UI elements (buttons, menus, fields) visible on screen\n"
        "- Be concise but precise\n"
        "- If the task is complete, respond with [DONE]\n"
    )
    if manual_context:
        prompt += f"\n\n--- Reference Manual Context ---\n{manual_context}\n--- End Reference Manual Context ---\n"
    return prompt


def build_check_prompt(before_b64: str, after_b64: str, instruction: str) -> list:
    """Build messages for step completion check."""
    return [
        {
            "role": "system",
            "content": (
                "You are checking if a user completed a step. "
                "Compare the before and after screenshots. "
                f'The instruction was: "{instruction}"\n'
                "Respond with only 'Yes' if the step appears completed, or 'No' if not."
            ),
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Before:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{before_b64}"}},
                {"type": "text", "text": "After:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{after_b64}"}},
            ],
        },
    ]


def build_coordinate_prompt(screenshot_b64: str, instruction: str) -> list:
    """Build messages for click target detection."""
    return [
        {
            "role": "system",
            "content": (
                "You are identifying click targets on a screenshot. "
                f'The instruction is: "{instruction}"\n'
                "Respond with only the x,y pixel coordinates of the element to click, "
                "or 'None' if no click target is found."
            ),
        },
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}},
                {"type": "text", "text": "Where should I click?"},
            ],
        },
    ]


def build_help_prompt(question: str) -> list:
    """Build messages for follow-up Q&A."""
    return [
        {
            "role": "system",
            "content": "You are a helpful assistant answering follow-up questions about a software task.",
        },
        {"role": "user", "content": question},
    ]
```

**Step 3: Update main_window.py imports**

Replace `from lib.prompts.action import build_action_prompt` and `from lib.prompts.check import build_check_prompt` with:
```python
from core.prompts import build_action_prompt, build_check_prompt
```

**Step 4: Commit**

```bash
git add core/prompts.py ui/main_window.py
git commit -m "feat: add Python prompt builders, update main_window imports"
```

---

### Task 10: Create app entry point

**Files:**
- Create: `main.py`

**Step 1: Implement**

```python
# main.py
"""GeoLens PySide6 desktop application entry point."""
import sys
import os

from dotenv import load_dotenv

# Load .env before any imports that need API keys
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
# Also try .env.local for compatibility
load_dotenv(os.path.join(os.path.dirname(__file__), ".env.local"))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GeoLens")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

**Step 2: Smoke test — verify the window opens**

```bash
uv run python main.py
```

Expected: A 900x600 window appears with left panel (Manuals, Goal, Capture) and right panel (chat area with Start/Refresh buttons). Close the window to exit.

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add main.py entry point"
```

---

### Task 11: Clean up web-only files

Remove Next.js frontend and FastAPI router code that is no longer needed.

**Files:**
- Delete: `app/` directory (entire Next.js frontend)
- Delete: `api/routers/` directory
- Delete: `api/utils/stream.py`
- Delete: `api/index.py`
- Delete: `lib/` directory
- Delete: `hooks/` directory
- Delete: `components/` directory
- Keep: `api/services/`, `api/models.py`, `api/utils/gemini.py` (used by core/check.py)

**Step 1: Remove files**

```bash
rm -rf app/ lib/ hooks/ components/ api/routers/ api/utils/stream.py api/index.py
rm -f package.json package-lock.json next.config.js tsconfig.json tailwind.config.ts postcss.config.mjs next-env.d.ts
rm -f vercel.json Procfile
rm -f playwright.config.ts
rm -rf tests/home.spec.ts tests/screenshots/ test-results/
rm -rf node_modules/ .next/
```

**Step 2: Verify the app still runs**

```bash
uv run python main.py
```

Expected: Window opens without import errors.

**Step 3: Verify tests still pass**

```bash
uv run python -m pytest tests/ -v
```

Expected: All existing Python tests pass.

**Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove web frontend and FastAPI router code"
```

---

### Task 12: Update CLAUDE.md and README

**Files:**
- Modify: `CLAUDE.md`
- Modify: `README.md`

**Step 1: Update CLAUDE.md**

Update to reflect the PySide6 architecture:
- Tech stack: Remove Next.js/React/Tailwind, add PySide6/mss/pygetwindow
- Commands: Replace `npm run dev` with `uv run python main.py`
- Architecture: Update frontend/backend sections
- Remove SSE streaming protocol section
- Update project structure

**Step 2: Update README.md**

Update setup instructions:
- Remove Node.js prerequisite
- Update install steps to `uv pip install -r requirements.txt`
- Update run command to `uv run python main.py`

**Step 3: Commit**

```bash
git add CLAUDE.md README.md
git commit -m "docs: update CLAUDE.md and README for PySide6 migration"
```

---

### Task 13: End-to-end integration test

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration test**

```python
# tests/test_integration.py
"""Integration tests for the PySide6 app."""
import pytest
from unittest.mock import patch, MagicMock

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


@pytest.fixture(scope="session")
def app():
    """Create QApplication once for all tests."""
    application = QApplication.instance() or QApplication([])
    yield application


@pytest.fixture
def main_window(app):
    window = MainWindow()
    yield window
    window.close()


def test_window_opens(main_window):
    assert main_window.windowTitle() == "GeoLens"
    assert main_window.width() >= 900
    assert main_window.height() >= 600


def test_start_without_goal_shows_warning(main_window, qtbot):
    """Start without goal should show warning."""
    # Clear goal
    main_window._goal_input._input.clear()
    # Should not crash
    main_window._on_start()


def test_manual_panel_exists(main_window):
    assert main_window._manual_panel is not None


def test_chat_panel_add_card(main_window):
    card = main_window._chat_panel.add_step_card(1)
    assert card is not None
    card.append_text("Hello")
    assert "Hello" in card._text
```

**Step 2: Run integration tests**

```bash
uv pip install pytest-qt
uv run python -m pytest tests/test_integration.py -v
```

Expected: All tests pass.

**Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add PySide6 integration tests"
```

---

## Summary

| Task | Description | Est. Files |
|------|-------------|------------|
| 1 | Update deps + directories | 2 modified, 4 created |
| 2 | Core: step generation | 2 created |
| 3 | Core: check/help/coordinates | 4 created |
| 4 | App state management | 2 created |
| 5 | QThread workers | 4 created |
| 6 | Manual panel widget | 1 created |
| 7 | Chat/step/goal/capture widgets | 4 created |
| 8 | Main window | 1 created |
| 9 | Prompt builders | 1 created, 1 modified |
| 10 | App entry point | 1 created |
| 11 | Clean up web files | Many deleted |
| 12 | Update docs | 2 modified |
| 13 | Integration tests | 1 created |
