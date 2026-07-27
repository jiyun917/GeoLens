"""Emergency secret scanner — full git history across all refs.

Runs before gitleaks install completes; catches the most common exposed
secret patterns. High-signal patterns aimed at what we know is in this
project: Gemini/Anthropic/OpenAI API keys, generic tokens, .env-style
KEY=value pairs with high-entropy values.

Exit code:
  0 — no matches
  1 — matches found (prints commit, file, line preview)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# Patterns keyed by service. Order matters — most specific first.
# All patterns are conservative (no false-positive-heavy generic entropy).
PATTERNS = [
    # Google Gemini / Cloud API keys (AIza prefix + 35 chars)
    ("google_api_key",   re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    # Anthropic API keys (sk-ant-)
    ("anthropic",        re.compile(r"sk-ant-[A-Za-z0-9_-]{80,}")),
    # OpenAI API keys (sk- + 40+ alnum, distinguishing from anthropic)
    ("openai",           re.compile(r"sk-(?!ant-)[A-Za-z0-9]{20,}")),
    # OpenRouter (sk-or-...)
    ("openrouter",       re.compile(r"sk-or-[A-Za-z0-9_-]{20,}")),
    # GitHub tokens (ghp_, ghs_, gho_, etc.)
    ("github_token",     re.compile(r"gh[pos]_[A-Za-z0-9]{36,}")),
    # AWS access keys
    ("aws_akid",         re.compile(r"AKIA[0-9A-Z]{16}")),
    # Slack tokens
    ("slack",            re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    # Generic .env-style secrets (KEY=long-value) — sensitivity filter
    ("env_secret",       re.compile(
        r"^\s*(?:[A-Z_]*(?:API_?KEY|SECRET|TOKEN|PASSWORD)[A-Z_]*)\s*=\s*"
        r"['\"]?([A-Za-z0-9_+/=.-]{20,})['\"]?",
        re.MULTILINE,
    )),
]

# .env.example is a template with placeholder values — allowlist those
ALLOWED_PLACEHOLDERS = {
    "your-api-key-here", "your_api_key_here", "placeholder", "changeme",
    "xxxxxxxxxx", "your-key", "your_key", "sk-your-key", "your-secret-here",
    "OPENAI_API_KEY_HERE", "GEMINI_API_KEY_HERE", "ANTHROPIC_API_KEY_HERE",
}


def run(cmd: list[str]) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.stdout


def list_all_commits() -> list[str]:
    out = run(["git", "log", "--all", "--pretty=format:%H"])
    return [c for c in out.splitlines() if c.strip()]


def get_commit_diff(commit: str) -> str:
    return run(["git", "show", "--format=", "--no-renames", commit])


def scan_text(text: str, commit: str) -> list[tuple]:
    findings = []
    for label, pat in PATTERNS:
        for m in pat.finditer(text):
            matched = m.group(0)
            # Strip leading + or - (diff markers) if present
            payload = matched.lstrip("+-").strip()
            if any(ph.lower() in payload.lower() for ph in ALLOWED_PLACEHOLDERS):
                continue
            # For env_secret, extract just the value
            if label == "env_secret":
                val = m.group(1) if m.groups() else ""
                if any(ph.lower() in val.lower() for ph in ALLOWED_PLACEHOLDERS):
                    continue
            # Preview: mask middle of match
            preview = payload[:10] + "…" + payload[-4:] if len(payload) > 20 else payload
            # Find containing line for context
            line_start = text.rfind("\n", 0, m.start()) + 1
            line_end = text.find("\n", m.end())
            if line_end == -1:
                line_end = len(text)
            context = text[line_start:line_end][:200]
            findings.append((commit[:8], label, preview, context))
    return findings


def main():
    commits = list_all_commits()
    print(f"Scanning {len(commits)} commits across all refs...")
    all_findings = []
    for i, c in enumerate(commits):
        if (i + 1) % 5 == 0:
            print(f"  ... {i+1}/{len(commits)}")
        diff = get_commit_diff(c)
        findings = scan_text(diff, c)
        all_findings.extend(findings)

    # Also scan working tree (uncommitted files that git doesn't diff)
    print("\nScanning working tree files...")
    wt_files = run(["git", "ls-files"]).splitlines()
    for fp in wt_files:
        p = Path(fp)
        if not p.exists() or p.stat().st_size > 2_000_000:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        findings = scan_text(text, "WORKING")
        all_findings.extend(findings)

    print()
    print("=" * 70)
    if not all_findings:
        print("STATUS: CLEAN — no secret patterns matched in history or working tree.")
        sys.exit(0)
    else:
        print(f"STATUS: {len(all_findings)} POTENTIAL MATCHES — REVIEW MANUALLY.")
        print("=" * 70)
        for commit, label, preview, context in all_findings[:30]:
            print(f"\n  commit={commit} type={label}")
            print(f"    preview: {preview}")
            print(f"    context: {context[:180]}")
        if len(all_findings) > 30:
            print(f"\n  ... and {len(all_findings) - 30} more")
        sys.exit(1)


if __name__ == "__main__":
    main()
