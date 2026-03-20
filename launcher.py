"""
GeoLens Launcher
Starts Next.js + FastAPI servers, opens system browser, handles cleanup on exit.
"""

import sys
import os
import signal
import subprocess
import time
import socket
import webbrowser
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()
FRONTEND_PORT = 3000
BACKEND_PORT = 8000
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"

backend_proc = None
frontend_proc = None


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def kill_port(port: int):
    try:
        result = subprocess.run(["lsof", "-t", f"-i:{port}"], capture_output=True, text=True)
        for pid in result.stdout.strip().split("\n"):
            if pid.strip():
                os.kill(int(pid.strip()), signal.SIGKILL)
    except Exception:
        pass


def find_node() -> str:
    for candidate in [
        os.path.expanduser("~/anaconda3/bin/node"),
        "/usr/local/bin/node",
        "/usr/bin/node",
    ]:
        if os.path.exists(candidate):
            return candidate
    return ""


def stop_servers():
    global backend_proc, frontend_proc
    for proc in [frontend_proc, backend_proc]:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    kill_port(FRONTEND_PORT)
    kill_port(BACKEND_PORT)


def signal_handler(sig, frame):
    print("\n\033[33m[GeoLens] Shutting down...\033[0m")
    stop_servers()
    print("\033[33m[GeoLens] Goodbye!\033[0m")
    sys.exit(0)


def main():
    global backend_proc, frontend_proc

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print()
    print("  \033[1;36m╔══════════════════════════════════════════╗\033[0m")
    print("  \033[1;36m║\033[0m            \033[1;37mGeoLens\033[0m                       \033[1;36m║\033[0m")
    print("  \033[1;36m║\033[0m   AI-Powered Geoscience Interpretation   \033[1;36m║\033[0m")
    print("  \033[1;36m╚══════════════════════════════════════════╝\033[0m")
    print()

    env = os.environ.copy()
    node_bin = find_node()
    if not node_bin:
        print("  \033[31m[ERROR] Node.js not found!\033[0m")
        sys.exit(1)
    env["PATH"] = os.path.dirname(node_bin) + ":" + env.get("PATH", "")

    # Clean ports
    for port, name in [(BACKEND_PORT, "Backend"), (FRONTEND_PORT, "Frontend")]:
        if is_port_open(port):
            print(f"  \033[33m[{name}]\033[0m Cleaning up port {port}...")
            kill_port(port)
            time.sleep(0.5)

    # Start backend
    print("  \033[34m[Backend]\033[0m  Starting FastAPI on port 8000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.index:app", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)],
        cwd=str(PROJECT_DIR), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    # Start frontend
    print("  \033[34m[Frontend]\033[0m Starting Next.js on port 3000...")
    npx_bin = os.path.join(os.path.dirname(node_bin), "npx")
    frontend_proc = subprocess.Popen(
        [npx_bin, "next", "dev", "--port", str(FRONTEND_PORT)],
        cwd=str(PROJECT_DIR), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    # Wait for servers
    print()
    for i in range(60):
        be = is_port_open(BACKEND_PORT)
        fe = is_port_open(FRONTEND_PORT)

        if be and fe:
            print(f"\r  \033[1;32m✓ Servers ready!\033[0m                              ")
            break

        waiting = []
        if not be: waiting.append("backend")
        if not fe: waiting.append("frontend")
        dots = "." * (i % 4 + 1)
        print(f"\r  Waiting for {', '.join(waiting)}{dots:<4}", end="", flush=True)
        time.sleep(0.5)
    else:
        print("\n  \033[31m[ERROR] Servers failed to start.\033[0m")
        stop_servers()
        sys.exit(1)

    # Open browser
    print(f"  \033[34m→ Opening browser:\033[0m {FRONTEND_URL}")
    webbrowser.open(FRONTEND_URL)

    print()
    print("  \033[1;36m┌───────────────────────────────────────┐\033[0m")
    print("  \033[1;36m│\033[0m  GeoLens is running.                  \033[1;36m│\033[0m")
    print(f"  \033[1;36m│\033[0m  \033[4m{FRONTEND_URL}\033[0m              \033[1;36m│\033[0m")
    print("  \033[1;36m│\033[0m  Press \033[1mCtrl+C\033[0m to stop.               \033[1;36m│\033[0m")
    print("  \033[1;36m└───────────────────────────────────────┘\033[0m")
    print()

    # Monitor servers
    try:
        while True:
            time.sleep(2)
            if backend_proc.poll() is not None:
                print("  \033[33m[Backend]\033[0m Crashed. Restarting...")
                backend_proc = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "api.index:app", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)],
                    cwd=str(PROJECT_DIR), env=env,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            if frontend_proc.poll() is not None:
                print("  \033[33m[Frontend]\033[0m Crashed. Restarting...")
                frontend_proc = subprocess.Popen(
                    [npx_bin, "next", "dev", "--port", str(FRONTEND_PORT)],
                    cwd=str(PROJECT_DIR), env=env,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
    except KeyboardInterrupt:
        pass

    print("\n\033[33m[GeoLens] Shutting down...\033[0m")
    stop_servers()
    print("\033[33m[GeoLens] Goodbye!\033[0m")


if __name__ == "__main__":
    main()
