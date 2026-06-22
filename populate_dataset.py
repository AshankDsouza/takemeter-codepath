#!/usr/bin/env python3
"""Populate takemeter_dataset.csv from raw Reddit JSON files in /data.

Files are organized into category subfolders (data/sports_news, data/educative,
data/entertaining); each subfolder's label is applied to all its files. The
script errors out if any category has fewer than MIN_FILES_PER_CATEGORY files.

Each JSON file is a RedditPost[] (Reddit listing format):
  - element [0] = the main post listing (t3)
  - element [1] = the comments listing (t1 entries under .data.children)

The 'text' column holds the post title + post body + top three comments.
Other metadata (users, dates, scores) is intentionally excluded.
"""

import csv
import glob
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "takemeter_dataset.csv")
REDDIT_BASE = "https://www.reddit.com"
TOP_N_COMMENTS = 3
MIN_FILES_PER_CATEGORY = 10

# Label assigned per source subfolder of data/.
CATEGORY_LABELS = {
    "sports_news": "sports-news",
    "educative": "educative",
    "entertaining": "entertaining",
}


def extract_post(listing):
    """Return (title, selftext, permalink) from the post listing element."""
    post = listing["data"]["children"][0]["data"]
    return (
        post.get("title", "").strip(),
        post.get("selftext", "").strip(),
        post.get("permalink", ""),
    )


def extract_top_comments(listing, n=TOP_N_COMMENTS):
    """Return up to n top-level comment bodies, in order."""
    bodies = []
    for child in listing["data"]["children"]:
        if child.get("kind") != "t1":
            continue
        body = child["data"].get("body", "").strip()
        if body:
            bodies.append(body)
        if len(bodies) >= n:
            break
    return bodies


def build_text(title, selftext, comments):
    parts = [title]
    if selftext:
        parts.append(selftext)
    parts.extend(comments)
    return "\n\n".join(parts)


def main():
    rows = []
    for folder, label in CATEGORY_LABELS.items():
        category_dir = os.path.join(DATA_DIR, folder)
        paths = sorted(glob.glob(os.path.join(category_dir, "*.json")))

        if len(paths) < MIN_FILES_PER_CATEGORY:
            raise SystemExit(
                f"Category '{folder}' has {len(paths)} files; "
                f"a minimum of {MIN_FILES_PER_CATEGORY} is required."
            )

        for path in paths:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list) or len(data) < 1:
                print(f"Skipping {path}: unexpected format")
                continue

            title, selftext, permalink = extract_post(data[0])
            comments = extract_top_comments(data[1]) if len(data) > 1 else []

            rows.append({
                "text": build_text(title, selftext, comments),
                "label": label,
                "notes": "",
                "url": REDDIT_BASE + permalink if permalink else "",
            })
            print(f"Processed {folder}/{os.path.basename(path)}: {len(comments)} comments")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "notes", "url"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
