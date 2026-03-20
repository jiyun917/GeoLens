import os
import shutil
import tempfile
from typing import List, Tuple

from git import Repo

# File extensions to categorize
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".c", ".cpp",
    ".h", ".hpp", ".cs", ".rb", ".php", ".swift", ".kt", ".scala", ".sh",
}
DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc"}
CONFIG_EXTENSIONS = {
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env.example",
    ".gitignore", ".dockerignore", "Dockerfile", "Makefile",
}

# Directories to skip
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".next", ".cache", "coverage", ".tox",
}

MAX_FILE_SIZE = 100_000  # 100KB


def categorize_file(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    name = os.path.basename(file_path)
    if ext in CODE_EXTENSIONS:
        return "code"
    if ext in DOC_EXTENSIONS or name.upper().startswith("README"):
        return "doc"
    if ext in CONFIG_EXTENSIONS or name in ("Dockerfile", "Makefile", "Procfile"):
        return "config"
    return "other"


def get_language(file_path: str) -> str:
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".tsx": "typescript", ".jsx": "javascript", ".java": "java",
        ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php",
        ".md": "markdown", ".sh": "bash",
    }
    _, ext = os.path.splitext(file_path)
    return ext_map.get(ext, ext.lstrip(".") if ext else "unknown")


def parse_github(repo_url: str) -> List[Tuple[str, dict]]:
    """
    Shallow clone a GitHub repo, walk files, and extract content with metadata.
    Prioritizes READMEs and documentation files.
    """
    tmp_dir = tempfile.mkdtemp()
    results: List[Tuple[str, dict]] = []
    readme_results: List[Tuple[str, dict]] = []

    try:
        Repo.clone_from(repo_url, tmp_dir, depth=1)

        # Generate directory tree
        tree_lines = []
        for root, dirs, files in os.walk(tmp_dir):
            # Filter out skip dirs
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            rel_root = os.path.relpath(root, tmp_dir)
            level = rel_root.count(os.sep)
            indent = "  " * level
            dir_name = os.path.basename(root)
            if rel_root != ".":
                tree_lines.append(f"{indent}{dir_name}/")
            for f in sorted(files):
                tree_lines.append(f"{indent}  {f}")

        if tree_lines:
            tree_text = "Directory structure:\n" + "\n".join(tree_lines[:200])
            results.append((tree_text, {
                "source": repo_url,
                "file_path": "DIRECTORY_TREE",
                "category": "structure",
                "type": "github",
            }))

        # Walk and extract files
        for root, dirs, files in os.walk(tmp_dir):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for file_name in sorted(files):
                file_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(file_path, tmp_dir)
                category = categorize_file(file_name)

                if category == "other":
                    continue

                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > MAX_FILE_SIZE:
                        continue

                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    if not content.strip():
                        continue

                    metadata = {
                        "source": repo_url,
                        "file_path": rel_path,
                        "language": get_language(file_name),
                        "category": category,
                        "type": "github",
                    }

                    entry = (content, metadata)

                    # Prioritize READMEs
                    if file_name.upper().startswith("README"):
                        readme_results.append(entry)
                    else:
                        results.append(entry)

                except Exception:
                    continue

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # READMEs first, then docs, then code/config
    return readme_results + results
