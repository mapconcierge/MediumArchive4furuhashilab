"""Convert Medium RSS content HTML into Markdown, downloading referenced images
so the archive doesn't depend on Medium's CDN staying available."""
from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify as _markdownify

from lib import download_image, new_session


def html_to_markdown(html: str, image_dir: Path, image_rel_prefix: str) -> str:
    """Rewrite <img src> to local files under image_dir, then convert to Markdown."""
    soup = BeautifulSoup(html, "html.parser")
    session = new_session()

    for i, img in enumerate(soup.find_all("img"), start=1):
        src = img.get("src")
        if not src:
            continue
        filename = download_image(src, image_dir, i, session)
        if filename:
            img["src"] = f"{image_rel_prefix}/{filename}"

    return _markdownify(str(soup), heading_style="ATX").strip()
