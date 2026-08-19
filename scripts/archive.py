"""Track A: fetch new/updated posts from the Medium RSS feed and archive them
as Markdown. Run via .github/workflows/archive.yml (or manually)."""
from datetime import datetime, timezone

from fetch_feed import fetch_entries
from html_to_md import html_to_markdown
from lib import (
    REPO_ROOT,
    content_hash,
    load_archived_index,
    save_archived_index,
    slugify,
    unique_post_path,
    write_markdown,
)


def _guid_key(guid: str) -> str:
    return guid.rsplit("/", 1)[-1] if guid else guid


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def process_entry(entry: dict, index: dict) -> bool:
    key = _guid_key(entry["guid"])
    new_hash = content_hash(entry["content_html"])
    existing = index.get(key)

    if existing and existing.get("source") != "track_a":
        # Already archived by Track B (scripts/import_export.py), which hashes
        # Medium's internal paragraph model rather than RSS HTML. The two
        # hash schemes never agree even when content is unchanged, so without
        # this check Track A would re-derive (and overwrite with a lower
        # fidelity version of) every post Track B already archived, on every
        # single run. Leave Track B's version alone; only Track A's own
        # entries get re-hash-checked for edits below.
        return False

    if existing and existing["content_hash"] == new_hash:
        return False  # already archived and unchanged

    now = _now_iso()
    archived_at = existing["archived_at"] if existing else now
    published = entry["published"] or ""
    date_str = published[:10] if published[:10].count("-") == 2 else now[:10]
    year = date_str[:4]
    slug = slugify(entry["title"])

    rel_path = unique_post_path(year, date_str, slug, key, index)
    abs_path = REPO_ROOT / rel_path

    image_dir_name = f"{date_str}-{slug}"
    image_dir = REPO_ROOT / "assets" / "images" / image_dir_name
    image_rel_prefix = f"../../assets/images/{image_dir_name}"

    body_md = html_to_markdown(entry["content_html"], image_dir, image_rel_prefix)

    frontmatter = {
        "title": entry["title"],
        "author": entry["author"],
        "medium_url": entry["link"],
        "medium_guid": key,
        "published_at": published,
        "updated_at": now,
        "archived_at": archived_at,
        "tags": entry["tags"],
    }
    write_markdown(abs_path, frontmatter, body_md)

    index[key] = {
        "source": "track_a",
        "path": str(rel_path),
        "title": entry["title"],
        "author": entry["author"],
        "medium_url": entry["link"],
        "content_hash": new_hash,
        "published_at": published,
        "updated_at": now,
        "archived_at": archived_at,
        "tags": entry["tags"],
    }
    return True


def main() -> None:
    index = load_archived_index()
    entries = fetch_entries()
    changed = sum(process_entry(entry, index) for entry in entries)
    save_archived_index(index)
    print(f"{changed} post(s) written/updated out of {len(entries)} fetched from RSS")


if __name__ == "__main__":
    main()
