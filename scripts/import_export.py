"""Track B: import the JSON produced by scripts/browser_backfill.js
(window.fetchAllContent() in the browser console) and archive every post it
contains as Markdown, using the same posts/ + assets/images/ + data/ layout
and frontmatter as Track A (scripts/archive.py).

Usage:
    python import_export.py <path-to-furuhashilab_full_content.json>

See SPEC.md section 2 for why this exists (Medium's RSS feed only exposes the
latest ~10 posts, and Medium's official "download your information" export is
per-account rather than per-publication).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from lib import (
    REPO_ROOT,
    content_hash,
    load_archived_index,
    save_archived_index,
    slugify,
    unique_post_path,
    write_markdown,
)
from paragraphs_to_md import paragraphs_to_markdown


def _iso(epoch_millis) -> str:
    if not epoch_millis:
        return ""
    return datetime.fromtimestamp(epoch_millis / 1000, tz=timezone.utc).isoformat()


def _normalize_tags(raw_tags) -> list[str]:
    # browser_backfill.js stores post.tags as-is from Apollo's cache, which
    # normalizes Tag entities to {"__ref": "Tag:<slug>"} references rather
    # than inlining them. The part after "Tag:" is the tag text itself
    # (Apollo uses it as the cache key), so no extra fetch is needed.
    tags = []
    for t in raw_tags or []:
        if isinstance(t, dict) and "__ref" in t:
            tags.append(t["__ref"].split("Tag:", 1)[-1])
        elif isinstance(t, str):
            tags.append(t)
    return tags


def process_post(post: dict, index: dict) -> bool:
    key = post["id"]
    paragraphs = post.get("paragraphs") or []
    new_hash = content_hash(json.dumps(paragraphs, ensure_ascii=False, sort_keys=True))
    existing = index.get(key)
    if existing and existing.get("content_hash") == new_hash:
        return False

    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    archived_at = existing["archived_at"] if existing else now
    published = _iso(post.get("firstPublishedAt"))
    date_str = published[:10] if published[:10].count("-") == 2 else now[:10]
    year = date_str[:4]
    slug = slugify(post.get("title") or post.get("uniqueSlug") or key)

    rel_path = unique_post_path(year, date_str, slug, key, index)
    abs_path = REPO_ROOT / rel_path

    image_dir_name = f"{date_str}-{slug}"
    image_dir = REPO_ROOT / "assets" / "images" / image_dir_name
    image_rel_prefix = f"../../assets/images/{image_dir_name}"

    body_md = paragraphs_to_markdown(paragraphs, image_dir, image_rel_prefix)

    frontmatter = {
        "title": post.get("title") or "",
        "author": post.get("author") or "furuhashilab",
        "medium_url": post.get("mediumUrl") or "",
        "medium_guid": key,
        "published_at": published,
        "updated_at": now,
        "archived_at": archived_at,
        "tags": _normalize_tags(post.get("tags")),
    }
    write_markdown(abs_path, frontmatter, body_md)

    index[key] = {
        "path": str(rel_path),
        "title": frontmatter["title"],
        "medium_url": frontmatter["medium_url"],
        "content_hash": new_hash,
        "published_at": published,
        "updated_at": now,
        "archived_at": archived_at,
        "tags": frontmatter["tags"],
    }
    return True


def main(json_path: str) -> None:
    posts = json.loads(Path(json_path).read_text(encoding="utf-8"))
    index = load_archived_index()
    changed = sum(process_post(post, index) for post in posts)
    save_archived_index(index)
    print(f"{changed} post(s) written/updated out of {len(posts)} in {json_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python import_export.py <path-to-furuhashilab_full_content.json>")
    main(sys.argv[1])
