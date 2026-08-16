"""Fetch the Medium RSS feed for the lab publication and parse entries.

Medium's RSS feed only ever contains the latest ~10 posts (Medium's own
limitation, not something this script can work around). See SPEC.md section 0.
"""
from __future__ import annotations

import calendar
from datetime import datetime, timezone

import feedparser

FEED_URL = "https://medium.com/feed/furuhashilab"


def _iso_published(entry) -> str:
    """feedparser gives RFC822 strings (e.g. 'Tue, 21 Jul 2026 ...'), which do
    not sort correctly as plain strings. Normalize to ISO 8601 UTC instead."""
    parsed = entry.get("published_parsed")
    if not parsed:
        return entry.get("published", "")
    return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc).isoformat()


def _canonical_link(entry) -> str:
    return entry.get("link", "").split("?", 1)[0]


def fetch_entries(feed_url: str = FEED_URL) -> list[dict]:
    feed = feedparser.parse(feed_url)
    if feed.bozo and not feed.entries:
        raise RuntimeError(f"failed to parse feed {feed_url}: {feed.bozo_exception}")

    entries = []
    for entry in feed.entries:
        if entry.get("content"):
            content_html = entry["content"][0]["value"]
        else:
            content_html = entry.get("summary", "")
        entries.append(
            {
                "guid": entry.get("id") or entry.get("link", ""),
                "link": _canonical_link(entry),
                "title": entry.get("title", "(無題)"),
                "author": entry.get("author", "furuhashilab"),
                "published": _iso_published(entry),
                "tags": [t["term"] for t in entry.get("tags", [])],
                "content_html": content_html,
            }
        )
    return entries


if __name__ == "__main__":
    for e in fetch_entries():
        print(e["guid"], "-", e["title"])
