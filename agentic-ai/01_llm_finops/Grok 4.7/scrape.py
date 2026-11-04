#!/usr/bin/env python3
"""Fetch a web page, extract structured content, and save it as JSON."""

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


class PageExtractor(HTMLParser):
    """Collect title, headings, paragraphs, and links from HTML."""

    _SKIP_TAGS = {"script", "style", "noscript"}
    _HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title = ""
        self.headings = []
        self.paragraphs = []
        self.links = []
        self._skip_depth = 0
        self._capture = None
        self._buffer = []
        self._current_href = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return

        attr_map = {name.lower(): value for name, value in attrs}
        if tag == "title" and not self.title:
            self._capture = "title"
            self._buffer = []
        elif tag in self._HEADING_TAGS:
            self._capture = "heading"
            self._buffer = []
        elif tag == "p":
            self._capture = "paragraph"
            self._buffer = []
        elif tag == "a":
            href = attr_map.get("href")
            if href:
                self._capture = "link"
                self._buffer = []
                self._current_href = urljoin(self.base_url, href.strip())

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self._SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth or self._capture is None:
            return

        text = " ".join("".join(self._buffer).split())
        if self._capture == "title" and tag == "title" and text:
            self.title = text
        elif self._capture == "heading" and tag in self._HEADING_TAGS and text:
            self.headings.append({"level": tag, "text": text})
        elif self._capture == "paragraph" and tag == "p" and text:
            self.paragraphs.append(text)
        elif self._capture == "link" and tag == "a" and self._current_href:
            self.links.append({"text": text, "href": self._current_href})

        if tag in {"title", "p", "a"} or tag in self._HEADING_TAGS:
            self._capture = None
            self._buffer = []
            self._current_href = None

    def handle_data(self, data):
        if self._skip_depth or self._capture is None:
            return
        self._buffer.append(data)

    def as_dict(self, url, status):
        return {
            "url": url,
            "status": status,
            "title": self.title,
            "headings": self.headings,
            "paragraphs": self.paragraphs,
            "links": self.links,
        }


def fetch(url, timeout):
    """Download a page. Raises ValueError or URLError on failure."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"URL must be an absolute http(s) address: {url}")

    request = Request(
        url,
        headers={"User-Agent": "grok-scraper/1.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        status = getattr(response, "status", response.getcode())
        content_type = response.headers.get("Content-Type", "")
        charset = response.headers.get_content_charset() or "utf-8"
        raw = response.read()

    if status >= 400:
        raise HTTPError(url, status, f"HTTP {status}", hdrs=None, fp=None)

    if "html" not in content_type.lower() and "text" not in content_type.lower():
        raise ValueError(f"Expected an HTML page, got Content-Type {content_type!r}")

    try:
        html = raw.decode(charset, errors="replace")
    except LookupError as exc:
        raise ValueError(f"Unknown character encoding {charset!r}") from exc

    if not html.strip():
        raise ValueError("Page body is empty")

    return status, html


def scrape(url, timeout):
    """Fetch a page and return extracted content."""
    status, html = fetch(url, timeout)
    parser = PageExtractor(url)
    parser.feed(html)
    parser.close()
    data = parser.as_dict(url, status)
    if not any((data["title"], data["headings"], data["paragraphs"], data["links"])):
        raise ValueError("No title, headings, paragraphs, or links found")
    return data


def save(data, output_path):
    """Write scraped data as pretty-printed JSON."""
    path = Path(output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Could not write {path}: {exc}") from exc
    return path


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Scrape a web page and save the data as JSON.")
    parser.add_argument("url", help="Absolute http(s) URL to scrape")
    parser.add_argument(
        "-o",
        "--output",
        default="Grok/output/page.json",
        help="Path of the JSON file to write (default: Grok/output/page.json)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15,
        help="Request timeout in seconds (default: 15)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.timeout <= 0:
        print("Error: timeout must be greater than 0", file=sys.stderr)
        return 2

    try:
        data = scrape(args.url, args.timeout)
        path = save(data, args.output)
    except HTTPError as exc:
        print(f"Error: server returned HTTP {exc.code} for {args.url}", file=sys.stderr)
        return 1
    except URLError as exc:
        reason = getattr(exc, "reason", exc)
        print(f"Error: could not reach {args.url}: {reason}", file=sys.stderr)
        return 1
    except TimeoutError as exc:
        print(f"Error: timed out after {args.timeout}s fetching {args.url}: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Saved {path} "
        f"(title={data['title']!r}, headings={len(data['headings'])}, "
        f"paragraphs={len(data['paragraphs'])}, links={len(data['links'])})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
