#!/usr/bin/env python3
"""Scrape chess.com news articles and save raw JSON files compatible with
populate_dataset.py into data/sports_news/.

Each saved file is a two-element list matching the RedditPost[] format that
populate_dataset.py expects:
  [0] = post listing  (title + body in data.children[0].data)
  [1] = comments listing (empty children list — chess.com comments are not useful)

Usage:
    python data_creation.py              # scrapes pages 1-50 (default)
    python data_creation.py --pages 5   # scrapes only first 5 pages
"""

import argparse
import json
import os
import random
import string
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.chess.com"
NEWS_URL = BASE_URL + "/news"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "sports_news")
DEFAULT_PAGES = 50
REQUEST_DELAY = 0.5  # seconds between requests to be polite


def _random_filename():
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=10)) + ".json"


def _empty_comments_listing():
    return {
        "kind": "Listing",
        "data": {
            "children": [],
            "after": None,
            "before": None,
        },
    }


def _post_listing(title, body, url):
    return {
        "kind": "Listing",
        "data": {
            "children": [
                {
                    "kind": "t3",
                    "data": {
                        "title": title,
                        "selftext": body,
                        "permalink": url,
                        "url": url,
                    },
                }
            ],
            "after": None,
            "before": None,
        },
    }


def collect_article_urls(total_pages):
    urls = []
    for page in range(1, total_pages + 1):
        page_url = f"{NEWS_URL}?page={page}"
        print(f"Fetching article list: page {page}/{total_pages} ...")
        try:
            resp = requests.get(page_url, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  Warning: could not fetch {page_url}: {e}")
            time.sleep(REQUEST_DELAY)
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("article")
        for article in articles:
            link_tag = article.find("a", class_="post-preview-title")
            if link_tag and link_tag.get("href"):
                href = link_tag["href"].strip()
                if not href.startswith("http"):
                    href = BASE_URL + href
                urls.append(href)

        time.sleep(REQUEST_DELAY)

    return urls


def scrape_article(url):
    """Fetch a chess.com news article and return (title, body) or None on failure."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  Warning: could not fetch {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else ""

    content_div = soup.find("div", class_="post-view-content")
    if content_div:
        body = content_div.get_text(separator="\n", strip=True)
    else:
        body = ""

    return title, body


def save_article(title, body, url):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    payload = [
        _post_listing(title, body, url),
        _empty_comments_listing(),
    ]
    filename = _random_filename()
    filepath = os.path.join(OUTPUT_DIR, filename)
    # Avoid the (extremely unlikely) collision with an existing file.
    while os.path.exists(filepath):
        filename = _random_filename()
        filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return filename


def main():
    parser = argparse.ArgumentParser(description="Scrape chess.com news into data/sports_news/")
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES,
                        help=f"Number of news listing pages to scrape (default: {DEFAULT_PAGES})")
    args = parser.parse_args()

    article_urls = collect_article_urls(args.pages)
    print(f"\nFound {len(article_urls)} article URLs. Scraping content...\n")

    saved = 0
    for i, url in enumerate(article_urls, 1):
        print(f"[{i}/{len(article_urls)}] {url}")
        result = scrape_article(url)
        if result is None:
            time.sleep(REQUEST_DELAY)
            continue
        title, body = result
        filename = save_article(title, body, url)
        print(f"  Saved → {filename}")
        saved += 1
        time.sleep(REQUEST_DELAY)

    print(f"\nDone. {saved} articles saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
