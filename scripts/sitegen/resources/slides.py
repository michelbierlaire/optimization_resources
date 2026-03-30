"""Slides resource page builder."""

from __future__ import annotations

from typing import Any

from ..links import resource_page_link
from ..metadata import build_metadata_details, track_title
from ..related import build_simple_related_lines
from ..rendering import pdf_embed_html
from ..utils import is_defined


def build_slides_page(
    resource: dict[str, Any],
    topics: dict[str, dict[str, Any]],
    resources: dict[str, dict[str, Any]],
    asset_link_fn,
) -> str:
    """Render the markdown page for a slides resource."""
    lines = [f"# Slides: {resource['title']}\n\n"]

    track_labels = [
        track_title(track_id) for track_id in resource.get("tracks", [])
    ]
    if track_labels:
        heading = "Track" if len(track_labels) == 1 else "Tracks"
        lines.append(f"## {heading}\n\n")
        for label in track_labels:
            lines.append(f"- {label}\n")
        lines.append("\n")

    if is_defined(resource.get("path")):
        path = str(resource["path"]).strip()
        lines.append(pdf_embed_html(path, resource["title"], asset_link_fn))
        lines.append("\n\n")
    elif is_defined(resource.get("url")):
        url = str(resource["url"]).strip()
        lines.append(
            f'<p><a href="{url}" target="_blank">Open slides</a></p>\n\n'
        )

    lines.append(f"{resource['summary']}\n\n")

    exercise_ids = resource.get("exercises_ref") or []
    exercise_lines: list[str] = []
    for exercise_id in exercise_ids:
        exercise = resources[exercise_id]
        exercise_lines.append(
            f"- {resource_page_link(exercise, from_section='resources')}\n"
        )
    if exercise_lines:
        lines.append("## Exercises\n\n")
        lines.extend(exercise_lines)
        lines.append("\n")

    related_block = build_simple_related_lines(resource, resources)
    if related_block:
        lines.append(related_block)

    lines.append(build_metadata_details(resource, topics))
    return "".join(lines)
