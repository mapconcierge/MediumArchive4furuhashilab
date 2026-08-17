"""Shared helpers for the Medium archive pipeline."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "data" / "archived_posts.json"

IMAGE_FETCH_TIMEOUT = 20
USER_AGENT = (
    "MediumArchive4furuhashilab-bot "
    "(+https://github.com/mapconcierge/MediumArchive4furuhashilab)"
)


def image_extension(url: str, content_type: str) -> str:
    path_ext = Path(urlparse(url).path).suffix
    if path_ext and len(path_ext) <= 5:
        return path_ext
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
    }
    return mapping.get(content_type, ".jpg")


def download_image(url: str, dest_dir: Path, index: int, session: requests.Session) -> str | None:
    try:
        resp = session.get(url, timeout=IMAGE_FETCH_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return None
    ext = image_extension(url, resp.headers.get("Content-Type", ""))
    filename = f"{index:03d}{ext}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / filename).write_bytes(resp.content)
    return filename


def new_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session


def slugify(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    return text[:max_len].strip("-") or "post"


def content_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def unique_post_path(year: str, date_str: str, slug: str, key: str, index: dict) -> Path:
    """posts/{year}/{date}-{slug}.md, disambiguated with -2/-3/... if another
    post (different guid) already claims that path — same date + near-identical
    titles happens often enough across ~1600 posts by different authors."""
    base = f"{date_str}-{slug}"
    candidate = f"{base}.md"
    n = 2
    taken = {v["path"] for k, v in index.items() if k != key}
    while str(Path("posts") / year / candidate) in taken:
        candidate = f"{base}-{n}.md"
        n += 1
    return Path("posts") / year / candidate


def load_archived_index() -> dict:
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {}


def save_archived_index(data: dict) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def yaml_scalar(value) -> str:
    """Minimal YAML-safe scalar dump for the frontmatter we generate ourselves."""
    if isinstance(value, list):
        return "[" + ", ".join(yaml_scalar(v) for v in value) + "]"
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def write_markdown(path: Path, frontmatter: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {yaml_scalar(value)}")
    lines.append("---")
    header = "\n".join(lines)
    path.write_text(header + "\n\n" + body.strip() + "\n", encoding="utf-8")
