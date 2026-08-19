"""One-off: apply the {author_name: username} mapping collected by
scripts/browser_author_lookup.js to data/archived_posts.json, then rebuild
data/index.json so index.html/post.html can link author names to their
Medium profile (https://medium.com/@<username>).

Usage:
    python apply_author_usernames.py <path-to-furuhashilab_author_usernames.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from build_index import main as rebuild_index
from lib import load_archived_index, save_archived_index


def main(json_path: str) -> None:
    usernames = json.loads(Path(json_path).read_text(encoding="utf-8"))
    index = load_archived_index()

    updated = 0
    unresolved = set()
    for rec in index.values():
        author = rec.get("author")
        username = usernames.get(author)
        if username:
            if rec.get("author_username") != username:
                rec["author_username"] = username
                updated += 1
        else:
            unresolved.add(author)

    save_archived_index(index)
    rebuild_index()
    print(f"{updated} record(s) updated with author_username")
    if unresolved:
        print(f"no username found for {len(unresolved)} author(s): {sorted(unresolved)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python apply_author_usernames.py <path-to-furuhashilab_author_usernames.json>")
    main(sys.argv[1])
