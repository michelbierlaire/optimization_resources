"""Shared rendering helpers."""

from __future__ import annotations


def video_embed_html(url: str, title: str) -> str:
    """Return embeddable HTML for supported video URLs, or a link fallback."""
    cleaned = url.strip()
    youtube_id = None
    if "youtu.be/" in cleaned:
        youtube_id = (
            cleaned.split("youtu.be/", 1)[1]
            .split("?", 1)[0]
            .split("/", 1)[0]
        )
    elif "youtube.com/watch?v=" in cleaned:
        youtube_id = cleaned.split("watch?v=", 1)[1].split("&", 1)[0]

    if youtube_id:
        embed_url = f"https://www.youtube.com/embed/{youtube_id}"
        return (
            '<div style="position: relative; padding-bottom: 56.25%; height: 0; '
            'overflow: hidden; max-width: 100%;">'
            f'<iframe src="{embed_url}" title="{title}" '
            'style="position: absolute; top: 0; left: 0; width: 100%; '
            'height: 100%; border: 0;" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
            'gyroscope; picture-in-picture; web-share" '
            'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>'
            "</iframe></div>"
        )

    return (
        f'<p><a href="{cleaned}" target="_blank" '
        'rel="noopener noreferrer">Open video</a></p>'
    )


def pdf_embed_html(path: str, title: str, asset_link_fn) -> str:
    """Return embeddable HTML for PDF documents."""
    cleaned = asset_link_fn(path)
    return (
        f'<iframe src="{cleaned}" title="{title}" '
        'style="width: 100%; height: 80vh; border: none;"></iframe>'
    )
