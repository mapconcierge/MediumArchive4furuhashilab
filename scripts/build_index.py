"""Regenerate data/index.json, the lightweight metadata list the GitHub Pages
site (index.html / post.html) fetches to render the archive."""
import json

from lib import REPO_ROOT, load_archived_index

OUTPUT_PATH = REPO_ROOT / "data" / "index.json"


def main() -> None:
    archived = load_archived_index()
    posts = sorted(
        (
            {
                "guid": guid,
                "title": rec["title"],
                "author": rec.get("author", ""),
                "author_username": rec.get("author_username", ""),
                "path": rec["path"],
                "medium_url": rec["medium_url"],
                "published_at": rec.get("published_at", ""),
                "updated_at": rec.get("updated_at", ""),
                "tags": rec.get("tags", []),
            }
            for guid, rec in archived.items()
        ),
        key=lambda p: p["published_at"],
        reverse=True,
    )
    OUTPUT_PATH.write_text(
        json.dumps({"posts": posts}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(posts)} post(s) to {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
