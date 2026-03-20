import os
from pathlib import Path
from typing import List, Set, Tuple
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup


def _read_local_file(file_path: str) -> str:
    """Read a local HTML file and return its content."""
    # Convert file:/// URL to local path
    if file_path.startswith("file:///"):
        file_path = unquote(file_path[8:])  # Remove "file:///" and decode %20 etc.
    elif file_path.startswith("file://"):
        file_path = unquote(file_path[7:])

    if not os.path.isfile(file_path):
        return ""

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def _parse_local_html(url: str, max_depth: int = 2) -> List[Tuple[str, dict]]:
    """Parse local HTML files (file:/// URLs), following relative links."""
    visited: Set[str] = set()
    results: List[Tuple[str, dict]] = []

    # Get base directory for resolving relative links
    file_path = unquote(url.replace("file:///", "").replace("file://", ""))
    base_dir = os.path.dirname(file_path)

    def crawl(current_path: str, depth: int):
        if depth > max_depth or current_path in visited:
            return
        if not os.path.isfile(current_path):
            return
        visited.add(current_path)

        try:
            with open(current_path, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()
        except Exception:
            return

        soup = BeautifulSoup(html, "html.parser")

        # Remove non-content elements
        for tag in soup.find_all(["nav", "footer", "script", "style", "header", "aside"]):
            tag.decompose()

        main = soup.find("main") or soup.find("article") or soup.find("body")
        if main:
            text = main.get_text(separator="\n", strip=True)
            if text.strip() and len(text.strip()) > 20:
                title = soup.title.string if soup.title else os.path.basename(current_path)
                metadata = {
                    "source": current_path,
                    "title": title,
                    "type": "url",
                }
                results.append((text, metadata))

        # Follow child links
        if depth < max_depth:
            for link in soup.find_all("a", href=True):
                href = link["href"]
                # Skip anchors, javascript, external URLs
                if href.startswith(("#", "javascript:", "http://", "https://", "mailto:")):
                    continue
                # Resolve relative path
                child_path = os.path.normpath(os.path.join(os.path.dirname(current_path), href))
                if child_path.endswith((".htm", ".html")) and os.path.isfile(child_path):
                    crawl(child_path, depth + 1)

    crawl(file_path, 0)
    return results


def parse_url(url: str, max_depth: int = 2) -> List[Tuple[str, dict]]:
    """
    Fetch a web page and extract main content, recursively crawling
    child links on the same domain up to max_depth.
    Supports both http(s):// and file:/// URLs.
    """
    # Handle local file URLs
    if url.startswith("file://"):
        return _parse_local_html(url, max_depth)

    visited: Set[str] = set()
    results: List[Tuple[str, dict]] = []
    base_domain = urlparse(url).netloc

    def crawl(current_url: str, depth: int):
        if depth > max_depth or current_url in visited:
            return
        visited.add(current_url)

        try:
            response = requests.get(current_url, timeout=15)
            response.raise_for_status()
        except Exception:
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove non-content elements
        for tag in soup.find_all(["nav", "footer", "script", "style", "header", "aside"]):
            tag.decompose()

        # Extract main content
        main = soup.find("main") or soup.find("article") or soup.find("body")
        if main:
            text = main.get_text(separator="\n", strip=True)
            if text.strip():
                title = soup.title.string if soup.title else current_url
                metadata = {
                    "source": current_url,
                    "title": title,
                    "type": "url",
                }
                results.append((text, metadata))

        # Find child links on the same domain
        if depth < max_depth:
            for link in soup.find_all("a", href=True):
                child_url = urljoin(current_url, link["href"])
                parsed = urlparse(child_url)
                # Only follow same-domain links, skip fragments and non-http
                if (
                    parsed.netloc == base_domain
                    and parsed.scheme in ("http", "https")
                    and child_url not in visited
                ):
                    # Remove fragment
                    clean_url = parsed._replace(fragment="").geturl()
                    crawl(clean_url, depth + 1)

    crawl(url, 0)
    return results
