"""Video resource page builder."""

from __future__ import annotations

from typing import Any

from ..links import asset_link, resource_page_link
from ..metadata import build_metadata_details, track_title
from ..related import build_simple_related_lines
from ..rendering import video_embed_html
from ..utils import is_defined


def build_video_page(
    resource: dict[str, Any],
    topics: dict[str, dict[str, Any]],
    resources: dict[str, dict[str, Any]],
) -> str:
    """Render the markdown page for a video resource."""
    lines = [f"# Video: {resource['title']}\n\n"]
    track_labels = [
        track_title(track_id) for track_id in resource.get("tracks", [])
    ]
    if track_labels:
        heading = "Track" if len(track_labels) == 1 else "Tracks"
        lines.append(f"## {heading}\n\n")
        for label in track_labels:
            lines.append(f"- {label}\n")
        lines.append("\n")

    if is_defined(resource.get("url")):
        url = str(resource["url"]).strip()
        lines.append(video_embed_html(url, resource["title"]))
        lines.append("\n\n")
    elif is_defined(resource.get("path")):
        published_asset_link = asset_link(str(resource["path"]))
        lines.append(f"[Open video]({published_asset_link})\n\n")

    lines.append(f"{resource['summary']}\n\n")
    if is_defined(resource.get("duration")):
        lines.append(f"**Duration:** {resource['duration']}\n\n")

    if resource.get("slides_ref"):
        ref = resources[resource["slides_ref"]]
        lines.append("## Associated slides\n\n")
        lines.append(
            f"- {resource_page_link(ref, from_section='resources')}\n\n"
        )

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
