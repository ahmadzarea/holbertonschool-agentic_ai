#!/usr/bin/env python3
"""Scrape a web page and save the extracted data to JSON or CSV.

Usage:
    python scrape.py https://example.com -o data.json
    python scrape.py https://example.com -o data.csv

Requires: pip install requests beautifulsoup4
"""
import argparse
import csv
import json
import logging
import sys
import time

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("scraper")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SimpleScraper/1.0)"}


def fetch(url, retries=3, timeout=10):
    """Download a page, retrying on transient errors."""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except requests.HTTPError as e:
            status = e.response.status_code
            # Client errors (except 429) won't be fixed by retrying
            if 400 <= status < 500 and status != 429:
                raise
            log.warning("HTTP %s (attempt %d/%d)", status, attempt, retries)
        except (requests.ConnectionError, requests.Timeout) as e:
            log.warning("%s (attempt %d/%d)", type(e).__name__, attempt, retries)
        if attempt < retries:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts")


def parse(html, base_url=""):
    """Extract title, headings and links from the HTML."""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""
    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
    links = [
        {"text": a.get_text(strip=True), "href": a["href"]}
        for a in soup.find_all("a", href=True)
    ]
    return {"url": base_url, "title": title, "headings": headings, "links": links}


def save(data, path):
    """Save data as JSON or CSV depending on file extension."""
    if path.endswith(".csv"):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "href"])
            writer.writeheader()
            writer.writerows(data["links"])
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    log.info("Saved data to %s", path)


def main():
    parser = argparse.ArgumentParser(description="Scrape a web page.")
    parser.add_argument("url")
    parser.add_argument("-o", "--output", default="output.json")
    args = parser.parse_args()

    try:
        html = fetch(args.url)
        data = parse(html, args.url)
        save(data, args.output)
    except requests.exceptions.MissingSchema:
        log.error("Invalid URL (include http:// or https://): %s", args.url)
        return 1
    except requests.HTTPError as e:
        log.error("HTTP error: %s", e)
        return 1
    except requests.RequestException as e:
        log.error("Network error: %s", e)
        return 1
    except OSError as e:
        log.error("Could not write file: %s", e)
        return 1
    except Exception as e:  # last resort
        log.error("Unexpected error: %s", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
