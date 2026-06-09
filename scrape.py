"""
Reddit post scraper — outputs a clean Markdown file.

Uses the sandbox's existing Chromium browser (via CDP) to load Redlib
(a privacy-friendly Reddit frontend), then parses the HTML with
BeautifulSoup into clean, well-structured Markdown.

Usage:
    python3 scrape.py <reddit_post_url> [output_dir]

The script automatically converts any reddit.com URL to a Redlib URL.
Multiple Redlib instances are tried in order until one succeeds.
"""

import sys
import re
import html as html_module
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# CDP endpoint for the sandbox's persistent Chromium browser
CDP_ENDPOINT = "http://localhost:9222"

# Public Redlib instances to try in order (fallback if CDP fails)
REDLIB_INSTANCES = [
    "redlib.catsarch.com",
    "redlib.privacyredirect.com",
    "reddit.idevicehacked.com",
    "redlib.ducks.party",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def reddit_url_to_path(url: str) -> str:
    """Extract the path component from a reddit.com URL."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") + "/"
    return path


def fetch_via_cdp(path: str) -> str:
    """
    Navigate to a Redlib page using the existing sandbox Chromium instance
    (connected via Chrome DevTools Protocol). Returns the full page HTML.
    """
    # Try multiple Redlib instances
    last_error = None
    for instance in REDLIB_INSTANCES:
        full_url = f"https://{instance}{path}"
        try:
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
                context = browser.contexts[0]
                page = context.pages[0]
                page.goto(full_url, wait_until="networkidle", timeout=25000)
                html_content = page.content()

            # Sanity check: make sure it's not a bot-check or error page
            if "Making sure you" in html_content or "Reddit error" in html_content[:2000]:
                last_error = f"Bot check or error at {instance}"
                continue

            print(f"  Loaded from: {full_url}")
            return html_content

        except Exception as e:
            last_error = str(e)
            continue

    raise RuntimeError(
        f"All Redlib instances failed via CDP. Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# HTML → Markdown conversion
# ---------------------------------------------------------------------------

def md_body(element) -> str:
    """
    Convert a BeautifulSoup element (the post body or comment body)
    into clean Markdown text, preserving basic formatting.
    """
    if element is None:
        return ""

    parts = []

    for child in element.children:
        if not hasattr(child, "name"):
            # Plain text node
            t = str(child)
            if t.strip():
                parts.append(t)
            continue

        tag = child.name

        if tag in ("p",):
            inner = md_body(child).strip()
            if inner:
                parts.append(inner + "\n\n")

        elif tag in ("br",):
            parts.append("\n")

        elif tag in ("ul", "ol"):
            for li in child.find_all("li", recursive=False):
                parts.append(f"- {md_body(li).strip()}\n")
            parts.append("\n")

        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            parts.append("#" * level + " " + md_body(child).strip() + "\n\n")

        elif tag == "blockquote":
            inner = md_body(child).strip()
            quoted = "\n".join("> " + line for line in inner.split("\n"))
            parts.append(quoted + "\n\n")

        elif tag == "pre":
            code_el = child.find("code")
            code = code_el.get_text() if code_el else child.get_text()
            parts.append(f"```\n{code}\n```\n\n")

        elif tag == "code":
            parts.append(f"`{child.get_text()}`")

        elif tag in ("strong", "b"):
            parts.append(f"**{md_body(child).strip()}**")

        elif tag in ("em", "i"):
            parts.append(f"*{md_body(child).strip()}*")

        elif tag == "a":
            parts.append(child.get_text())

        elif tag in ("div", "span", "section"):
            parts.append(md_body(child))

        else:
            inner = child.get_text()
            if inner.strip():
                parts.append(inner)

    result = "".join(parts)
    # Unescape HTML entities
    result = html_module.unescape(result)
    # Collapse excessive blank lines
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def parse_comment(comment_div, depth: int = 0) -> list:
    """
    Recursively parse a Redlib `div.comment` element into Markdown lines.
    Extracts ONLY the raw text content.
    """
    lines = []

    # Body
    body_el = comment_div.find("div", class_="comment_body")
    md_el = body_el.find("div", class_="md") if body_el else None
    body = md_body(md_el or body_el)
    
    if body and body != "*[deleted or removed]*":
        for para in body.split("\n\n"):
            for line in para.split("\n"):
                stripped = line.strip()
                if stripped:
                    lines.append(stripped)
            lines.append("")

    # Recurse into replies
    replies_el = comment_div.find("blockquote", class_="replies")
    if replies_el:
        child_comments = replies_el.find_all("div", class_="comment", recursive=False)
        for child in child_comments:
            lines.extend(parse_comment(child, depth + 1))

    return lines


# ---------------------------------------------------------------------------
# Main scraping logic
# ---------------------------------------------------------------------------

def scrape_post(url: str, output_dir: Path) -> Path:
    """Fetch a Reddit post via Redlib and write a clean Markdown file."""
    path = reddit_url_to_path(url)
    print(f"Fetching: {path}")

    html_content = fetch_via_cdp(path)
    soup = BeautifulSoup(html_content, "html.parser")

    # --- Title ---
    title_el = soup.find("h1", class_="post_title")
    if not title_el:
        title_el = soup.find("h1")
    title = html_module.unescape(title_el.get_text(strip=True)) if title_el else "Untitled"

    # --- Subreddit ---
    sub_el = soup.find("a", class_="post_subreddit")
    subreddit = sub_el.get_text(strip=True) if sub_el else ""

    # --- Post body (self-text) ---
    post_body_el = soup.find("div", class_="post_body")
    md_el = post_body_el.find("div", class_="md") if post_body_el else None
    post_body = md_body(md_el or post_body_el)

    # --- Comments ---
    # In some Redlib versions, each top-level comment is in its own 'thread' div
    # In others, they are all in one. We'll find all div.comment whose parent
    # has the class 'thread'.
    top_comments = [
        c for c in soup.find_all("div", class_="comment")
        if c.parent and c.parent.name == "div" and "thread" in c.parent.get("class", [])
    ]

    # --- Build Markdown ---
    lines = []

    if post_body:
        lines.append(post_body)
        lines.append("")

    if top_comments:
        for comment_div in top_comments:
            lines.extend(parse_comment(comment_div, depth=0))

    md = "\n".join(lines)
    # Remove excessive trailing blank lines
    md = re.sub(r"\n{3,}$", "\n", md)

    # --- Save ---
    filename = slugify(title) + ".md"
    out_path = output_dir / filename
    out_path.write_text(md, encoding="utf-8")

    return out_path


def slugify(text: str) -> str:
    """Convert a title to a safe filename."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    text = text.strip("_")
    return text[:80]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scrape.py <reddit_post_url> [output_dir]")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path(".")
    output_dir.mkdir(parents=True, exist_ok=True)

    out_path = scrape_post(url, output_dir)
    content = out_path.read_text(encoding="utf-8")

    print(f"Saved:      {out_path}")
    print(f"Characters: {len(content):,}")
    print(f"OUTPUT_FILE:{out_path.resolve()}")


if __name__ == "__main__":
    main()
