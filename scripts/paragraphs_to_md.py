"""Convert Medium's internal "Paragraph" rich-content model (as captured by
scripts/browser_backfill.js from window.__APOLLO_STATE__) into Markdown.

This is Track B's converter (backfilled posts). Track A (scripts/html_to_md.py)
converts the pre-rendered HTML that Medium's RSS feed exposes instead — RSS
doesn't expose this paragraph model, only finished HTML.

Paragraph/markup shape reverse-engineered from live API responses on
2026-08-17 (see SPEC.md section 2). Not officially documented by Medium;
unrecognized `type` values fall back to plain text rather than raising, since
new/rare block types will otherwise silently break the whole import.
"""
from __future__ import annotations

from pathlib import Path

from lib import download_image, new_session

HEADING_LEVELS = {"H1": 1, "H2": 2, "H3": 3, "H4": 4}

_MARKUP_TAGS = {
    "STRONG": ("**", "**"),
    "EM": ("_", "_"),
    "CODE": ("`", "`"),
    "STRIKETHROUGH": ("~~", "~~"),
}


def _apply_markups(text: str, markups: list[dict] | None) -> str:
    if not markups:
        return text

    events: list[tuple[int, str]] = []
    for mk in markups:
        mtype = mk.get("type")
        start, end = mk.get("start", 0), mk.get("end", 0)
        if mtype == "A":
            open_tag, close_tag = "[", f"]({mk.get('href', '')})"
        elif mtype in _MARKUP_TAGS:
            open_tag, close_tag = _MARKUP_TAGS[mtype]
        else:
            continue
        events.append((start, open_tag))
        events.append((end, close_tag))

    # Insert furthest-right first so earlier offsets stay valid.
    events.sort(key=lambda e: e[0], reverse=True)
    chars = list(text)
    for offset, insert_text in events:
        chars.insert(offset, insert_text)
    return "".join(chars)


def _image_block(paragraph: dict, image_dir: Path, image_rel_prefix: str, index: int, session) -> str:
    meta = paragraph.get("metadata") or {}
    image_id = meta.get("id")
    if not image_id:
        return ""
    width = min(meta.get("originalWidth") or 1400, 1400)
    src_url = f"https://miro.medium.com/v2/resize:fit:{width}/{image_id}"
    filename = download_image(src_url, image_dir, index, session)
    if not filename:
        return ""
    alt = (meta.get("alt") or "").replace("[", "").replace("]", "")
    return f"![{alt}]({image_rel_prefix}/{filename})"


def paragraphs_to_markdown(paragraphs: list[dict], image_dir: Path, image_rel_prefix: str) -> str:
    session = new_session()
    blocks: list[str] = []
    image_index = 0

    for paragraph in paragraphs:
        ptype = paragraph.get("type")
        text = paragraph.get("text") or ""
        rendered = _apply_markups(text, paragraph.get("markups"))

        if ptype in HEADING_LEVELS:
            blocks.append("#" * HEADING_LEVELS[ptype] + " " + rendered)
        elif ptype == "P":
            blocks.append(rendered)
        elif ptype in ("BQ", "PQ"):
            blocks.append("> " + rendered)
        elif ptype == "PRE":
            lang = (paragraph.get("codeBlockMetadata") or {}).get("lang") or ""
            blocks.append(f"```{lang}\n{text}\n```")
        elif ptype == "ULI":
            blocks.append(f"- {rendered}")
        elif ptype == "OLI":
            blocks.append(f"1. {rendered}")
        elif ptype == "IMG":
            image_index += 1
            block = _image_block(paragraph, image_dir, image_rel_prefix, image_index, session)
            if block:
                blocks.append(block)
        elif ptype == "MIXTAPE_EMBED":
            # text already carries an "A" markup spanning the whole title in
            # practice, so apply_markups() above would double-wrap it — use
            # the raw text here instead of `rendered`.
            href = (paragraph.get("mixtapeMetadata") or {}).get("href", "")
            blocks.append(f"[{text or href}]({href})" if href else text)
        elif ptype == "IFRAME":
            media = (paragraph.get("iframe") or {}).get("mediaResource") or {}
            href = media.get("href") or media.get("iframeSrc") or ""
            blocks.append(f"[embedded content]({href})" if href else text)
        else:
            # Unknown block type: keep the text so nothing silently vanishes.
            if rendered:
                blocks.append(rendered)

    return "\n\n".join(b for b in blocks if b).strip()
