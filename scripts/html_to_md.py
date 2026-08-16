"""Convert Medium RSS content HTML into Markdown, downloading referenced images
so the archive doesn't depend on Medium's CDN staying available."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as _markdownify

TIMEOUT = 20
USER_AGENT = (
    "MediumArchive4furuhashilab-bot "
    "(+https://github.com/mapconcierge/MediumArchive4furuhashilab)"
)


def _image_extension(url: str, content_type: str) -> str:
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


def _download_image(url: str, dest_dir: Path, index: int, session: requests.Session) -> str | None:
    try:
        resp = session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return None
    ext = _image_extension(url, resp.headers.get("Content-Type", ""))
    filename = f"{index:03d}{ext}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / filename).write_bytes(resp.content)
    return filename


def html_to_markdown(html: str, image_dir: Path, image_rel_prefix: str) -> str:
    """Rewrite <img src> to local files under image_dir, then convert to Markdown."""
    soup = BeautifulSoup(html, "html.parser")
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    for i, img in enumerate(soup.find_all("img"), start=1):
        src = img.get("src")
        if not src:
            continue
        filename = _download_image(src, image_dir, i, session)
        if filename:
            img["src"] = f"{image_rel_prefix}/{filename}"

    return _markdownify(str(soup), heading_style="ATX").strip()
