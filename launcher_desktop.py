"""
GeoLens Desktop Application (for local PC with GUI environment)
PySide6 + QWebEngineView: native window with embedded browser.
Starts Next.js + FastAPI servers automatically.

Requirements:
  pip install PySide6

Usage (on local PC with desktop environment):
  python launcher_desktop.py
"""

import sys
import os
import signal
import subprocess
import time
import socket
import webbrowser
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar
)
from PySide6.QtCore import Qt, QUrl, QTimer, QSize, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QPixmap, QIcon

PROJECT_DIR = Path(__file__).parent.resolve()
FRONTEND_PORT = 3000
BACKEND_PORT = 8000
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"


# ─── Utilities ───

def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def kill_port(port: int):
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True
            )
            for line in result.stdout.strip().split("\n"):
                if f":{port}" in line and "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(["taskkill", "/F", "/PID", pid],
                                   capture_output=True)
        else:
            result = subprocess.run(
                ["lsof", "-t", f"-i:{port}"], capture_output=True, text=True
            )
            for pid in result.stdout.strip().split("\n"):
                if pid.strip():
                    os.kill(int(pid.strip()), signal.SIGKILL)
    except Exception:
        pass


def find_node() -> str:
    """Find node binary across platforms."""
    candidates = []
    if sys.platform == "win32":
        candidates = [
            os.path.expandvars(r"%APPDATA%\nvm\current\node.exe"),
            os.path.expandvars(r"%ProgramFiles%\nodejs\node.exe"),
            "node",
        ]
    else:
        candidates = [
            os.path.expanduser("~/anaconda3/bin/node"),
            "/usr/local/bin/node",
            "/usr/bin/node",
        ]

    for candidate in candidates:
        if candidate == "node":
            # Check if node is in PATH
            try:
                result = subprocess.run(
                    ["node", "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    return "node"
            except FileNotFoundError:
                continue
        elif os.path.exists(candidate):
            return candidate
    return ""


def find_npx(node_bin: str) -> str:
    if node_bin == "node":
        return "npx"
    node_dir = os.path.dirname(node_bin)
    if sys.platform == "win32":
        npx = os.path.join(node_dir, "npx.cmd")
        if os.path.exists(npx):
            return npx
    return os.path.join(node_dir, "npx")


def create_app_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor(59, 130, 246)))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(4, 4, 56, 56)
    painter.setPen(QColor(255, 255, 255))
    painter.setFont(QFont("Segoe UI", 28, QFont.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "G")
    painter.end()
    return QIcon(pixmap)


# ─── Server Thread ───

class ServerThread(QThread):
    status_changed = Signal(str)
    servers_ready = Signal()
    failed = Signal(str)

    def __init__(self):
        super().__init__()
        self.backend_proc = None
        self.frontend_proc = None
        self._env = None
        self._npx_bin = None

    def run(self):
        env = os.environ.copy()
        node_bin = find_node()
        if not node_bin:
            self.failed.emit("Node.js not found! Please install Node.js.")
            return

        if node_bin != "node":
            env["PATH"] = os.path.dirname(node_bin) + os.pathsep + env.get("PATH", "")
        self._env = env
        self._npx_bin = find_npx(node_bin)

        # Clean ports
        for port, name in [(BACKEND_PORT, "Backend"), (FRONTEND_PORT, "Frontend")]:
            if is_port_open(port):
                self.status_changed.emit(f"Cleaning up {name} port ({port})...")
                kill_port(port)
                time.sleep(0.5)

        # Start backend
        self.status_changed.emit("Starting backend server (FastAPI)...")
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        self.backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.index:app",
             "--host", "127.0.0.1", "--port", str(BACKEND_PORT)],
            cwd=str(PROJECT_DIR), env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=creation_flags if sys.platform == "win32" else 0,
        )

        # Start frontend
        self.status_changed.emit("Starting frontend server (Next.js)...")
        self.frontend_proc = subprocess.Popen(
            [self._npx_bin, "next", "dev", "--port", str(FRONTEND_PORT)],
            cwd=str(PROJECT_DIR), env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=creation_flags if sys.platform == "win32" else 0,
        )

        # Wait for ready
        for i in range(90):
            be = is_port_open(BACKEND_PORT)
            fe = is_port_open(FRONTEND_PORT)
            if be and fe:
                self.status_changed.emit("Servers ready!")
                time.sleep(0.3)
                self.servers_ready.emit()
                return

            waiting = []
            if not be:
                waiting.append("backend")
            if not fe:
                waiting.append("frontend")
            self.status_changed.emit(
                f"Waiting for {', '.join(waiting)}... ({(i + 1) // 2}s)"
            )
            time.sleep(0.5)

        self.failed.emit("Servers failed to start within 45 seconds.")

    def stop(self):
        for proc in [self.frontend_proc, self.backend_proc]:
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        kill_port(FRONTEND_PORT)
        kill_port(BACKEND_PORT)


# ─── Splash Window ───

class SplashWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoLens")
        self.setFixedSize(480, 320)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(8)

        title = QLabel("GeoLens")
        title.setFont(QFont("Segoe UI", 38, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("AI-Powered Geoscience Interpretation")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #9CA3AF; background: transparent;")
        subtitle.setAlignment(Qt.AlignCenter)

        self.status = QLabel("Initializing...")
        self.status.setFont(QFont("Segoe UI", 10))
        self.status.setStyleSheet("color: #60A5FA; background: transparent;")
        self.status.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setFixedHeight(4)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: #27272a; border: none; border-radius: 2px;
            }
            QProgressBar::chunk {
                background: #3b82f6; border-radius: 2px;
            }
        """)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(24)
        layout.addWidget(self.progress)
        layout.addSpacing(8)
        layout.addWidget(self.status)
        layout.addStretch()

        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(24, 24, 27)))
        painter.setPen(QColor(63, 63, 70))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 20, 20)

    def set_status(self, text: str):
        self.status.setText(text)


# ─── Main Window ───

class MainWindow(QMainWindow):
    def __init__(self, server_thread: ServerThread):
        super().__init__()
        self.server_thread = server_thread
        self.setWindowTitle("GeoLens")
        self.setWindowIcon(create_app_icon())
        self.resize(1440, 900)
        self.setMinimumSize(QSize(900, 600))
        self.setStyleSheet("QMainWindow { background-color: #09090b; }")

        self._setup_content()

    def _setup_content(self):
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtWebEngineCore import QWebEngineSettings

            self.browser = QWebEngineView()

            # Enable features
            settings = self.browser.settings()
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
            settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)

            self.browser.setUrl(QUrl(FRONTEND_URL))
            self.setCentralWidget(self.browser)
            self._use_webengine = True
        except ImportError:
            self._use_webengine = False
            self._show_fallback()

    def _show_fallback(self):
        """Fallback if WebEngine is not available."""
        fallback = QWidget()
        fallback.setStyleSheet("background-color: #09090b;")
        layout = QVBoxLayout(fallback)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("G")
        icon_label.setFont(QFont("Segoe UI", 48, QFont.Bold))
        icon_label.setStyleSheet("color: #3b82f6;")
        icon_label.setAlignment(Qt.AlignCenter)

        msg = QLabel(f"GeoLens is running at:\n{FRONTEND_URL}")
        msg.setFont(QFont("Segoe UI", 16))
        msg.setStyleSheet("color: white;")
        msg.setAlignment(Qt.AlignCenter)

        hint = QLabel("Opened in your default browser.\nYou can close this window — the server will keep running.")
        hint.setFont(QFont("Segoe UI", 10))
        hint.setStyleSheet("color: #9CA3AF;")
        hint.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addSpacing(12)
        layout.addWidget(msg)
        layout.addSpacing(8)
        layout.addWidget(hint)

        self.setCentralWidget(fallback)
        webbrowser.open(FRONTEND_URL)

    def closeEvent(self, event):
        self.server_thread.stop()
        event.accept()


# ─── Entry Point ───

def main():
    # High DPI support
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("GeoLens")
    app.setWindowIcon(create_app_icon())
    app.setStyle("Fusion")

    # Dark palette
    from PySide6.QtGui import QPalette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(9, 9, 11))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(24, 24, 27))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(39, 39, 42))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, QColor(59, 130, 246))
    app.setPalette(palette)

    # Splash
    splash = SplashWindow()
    splash.show()

    # Server thread
    server = ServerThread()

    main_window = None

    def on_status(text):
        splash.set_status(text)

    def on_ready():
        nonlocal main_window
        splash.close()
        main_window = MainWindow(server)
        main_window.show()

    def on_failed(msg):
        splash.set_status(f"Error: {msg}")
        QTimer.singleShot(4000, lambda: (server.stop(), app.quit()))

    server.status_changed.connect(on_status)
    server.servers_ready.connect(on_ready)
    server.failed.connect(on_failed)
    server.start()

    app.aboutToQuit.connect(server.stop)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
