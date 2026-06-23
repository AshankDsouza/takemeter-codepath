#!/usr/bin/env python3
"""Scrape chess.com and chess.stackexchange.com and save raw JSON files
compatible with populate_dataset.py into the appropriate data/ subfolders.

Each saved file is a two-element list matching the RedditPost[] format:
  [0] = post listing  (title + body in data.children[0].data)
  [1] = comments listing (answers/replies as t1 children)

Usage:
    python data_creation.py                        # all three categories, 50 pages each
    python data_creation.py --pages 5              # 5 pages for each category
    python data_creation.py --category sports_news # single category
"""

import argparse
import json
import os
import random
import string
import time

import requests
from bs4 import BeautifulSoup

CHESS_COM_BASE = "https://www.chess.com"
STACK_BASE = "https://chess.stackexchange.com"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DEFAULT_PAGES = 10
REQUEST_DELAY = 0.5


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _random_filename(output_dir):
    chars = string.ascii_lowercase + string.digits
    while True:
        name = "".join(random.choices(chars, k=10)) + ".json"
        if not os.path.exists(os.path.join(output_dir, name)):
            return name


def _comments_listing(children):
    return {
        "kind": "Listing",
        "data": {
            "children": children,
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


def _comment_child(body):
    return {"kind": "t1", "data": {"body": body}}


def _save(output_dir, title, body, url, comments):
    os.makedirs(output_dir, exist_ok=True)
    comment_children = [_comment_child(c) for c in comments]
    payload = [
        _post_listing(title, body, url),
        _comments_listing(comment_children),
    ]
    filename = _random_filename(output_dir)
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return filename


def _get(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        print(f"  Warning: could not fetch {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# chess.com scraper (shared for sports_news and entertaining)
# ---------------------------------------------------------------------------

def _chess_com_article_urls(listing_base, total_pages):
    urls = []
    for page in range(1, total_pages + 1):
        page_url = f"{listing_base}?page={page}"
        print(f"  Listing page {page}/{total_pages}: {page_url}")
        resp = _get(page_url)
        if resp is None:
            time.sleep(REQUEST_DELAY)
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        for article in soup.find_all("article"):
            link = article.find("a", class_="post-preview-title")
            if link and link.get("href"):
                href = link["href"].strip()
                if not href.startswith("http"):
                    href = CHESS_COM_BASE + href
                urls.append(href)
        time.sleep(REQUEST_DELAY)
    return urls


def _scrape_chess_com_article(url):
    resp = _get(url)
    if resp is None:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else ""
    content = soup.find("div", class_="post-view-content")
    body = content.get_text(separator="\n", strip=True) if content else ""
    return title, body


def scrape_chess_com(listing_path, output_subdir, total_pages):
    output_dir = os.path.join(DATA_DIR, output_subdir)
    listing_base = CHESS_COM_BASE + listing_path
    article_urls = _chess_com_article_urls(listing_base, total_pages)
    print(f"\nFound {len(article_urls)} articles for {output_subdir}. Scraping...\n")
    saved = 0
    for i, url in enumerate(article_urls, 1):
        print(f"  [{i}/{len(article_urls)}] {url}")
        result = _scrape_chess_com_article(url)
        if result is None:
            time.sleep(REQUEST_DELAY)
            continue
        title, body = result
        filename = _save(output_dir, title, body, url, [])
        print(f"    Saved → {filename}")
        saved += 1
        time.sleep(REQUEST_DELAY)
    print(f"\n{output_subdir}: {saved} files saved.\n")


# ---------------------------------------------------------------------------
# chess.stackexchange.com scraper (educative)
# ---------------------------------------------------------------------------

def _stack_question_urls(total_pages):
    urls = []
    for page in range(1, total_pages + 1):
        page_url = f"{STACK_BASE}/questions?tab=newest&page={page}"
        print(f"  Listing page {page}/{total_pages}: {page_url}")
        resp = _get(page_url)
        if resp is None:
            time.sleep(REQUEST_DELAY)
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        for div in soup.find_all("div", class_="s-post-summary--content"):
            h3 = div.find("h3", class_="s-post-summary--content-title")
            if h3:
                a = h3.find("a")
                if a and a.get("href"):
                    href = a["href"].strip()
                    if not href.startswith("http"):
                        href = STACK_BASE + href
                    urls.append(href)
        time.sleep(REQUEST_DELAY)
    return urls


def _scrape_stack_question(url):
    resp = _get(url)
    if resp is None:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.find("title")
    raw_title = title_tag.get_text(strip=True) if title_tag else ""
    title = raw_title.replace(" - Chess Stack Exchange", "").strip()

    post_cell = soup.find("div", class_="postcell")
    if post_cell:
        prose = post_cell.find("div", class_="s-prose")
        body = prose.get_text(separator="\n", strip=True) if prose else ""
    else:
        body = ""

    comments = []
    for answer_cell in soup.find_all("div", class_="answercell"):
        prose = answer_cell.find("div", class_="s-prose")
        if prose:
            text = prose.get_text(separator="\n", strip=True)
            if text:
                comments.append(text)

    return title, body, comments


def scrape_stack_educative(total_pages):
    output_dir = os.path.join(DATA_DIR, "educative")
    question_urls = _stack_question_urls(total_pages)
    print(f"\nFound {len(question_urls)} questions for educative. Scraping...\n")
    saved = 0
    for i, url in enumerate(question_urls, 1):
        print(f"  [{i}/{len(question_urls)}] {url}")
        result = _scrape_stack_question(url)
        if result is None:
            time.sleep(REQUEST_DELAY)
            continue
        title, body, comments = result
        filename = _save(output_dir, title, body, url, comments)
        print(f"    Saved → {filename}")
        saved += 1
        time.sleep(REQUEST_DELAY)
    print(f"\neducative: {saved} files saved.\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

CATEGORIES = {
    "sports_news": lambda pages: scrape_chess_com("/news", "sports_news", pages),
    "entertaining": lambda pages: scrape_chess_com("/articles", "entertaining", pages),
    "educative": lambda pages: scrape_stack_educative(pages),
}


def main():
    parser = argparse.ArgumentParser(description="Generate raw data for all three dataset categories.")
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES,
                        help=f"Listing pages to scrape per category (default: {DEFAULT_PAGES})")
    parser.add_argument("--category", choices=list(CATEGORIES.keys()),
                        help="Scrape only one category (default: all three)")
    args = parser.parse_args()

    targets = [args.category] if args.category else list(CATEGORIES.keys())
    for category in targets:
        print(f"\n{'='*60}")
        print(f"Scraping: {category}")
        print(f"{'='*60}")
        CATEGORIES[category](args.pages)


if __name__ == "__main__":
    main()
