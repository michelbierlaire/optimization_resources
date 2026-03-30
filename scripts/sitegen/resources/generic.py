"""Generic page builder for resource types without a custom layout."""

from __future__ import annotations

from typing import Any

from ..config import PATH_FROM_RESOURCES_TO_TOPICS
from ..links import asset_link, resource_page_link
from ..metadata import build_metadata_details, topic_title, track_title
from ..related import build_related_lines
from ..rendering import pdf_embed_html
from ..utils import is_defined, normalized_resource_type


def build_generic_page(
    resource: dict[str, Any],
    topics: dict[str, dict[str, Any]],
    resources: dict[str, dict[str, Any]],
) -> str:
    """Render the markdown page for a generic resource."""
    resource_type = normalized_resource_type(resource)
    lines = [f"# {resource['title']}\n\n"]
    track_labels = [
        track_title(track_id) for track_id in resource.get("tracks", [])
    ]
    if track_labels:
        heading = "Track" if len(track_labels) == 1 else "Tracks"
        lines.append(f"## {heading}\n\n")
        for label in track_labels:
            lines.append(f"- {label}\n")
        lines.append("\n")

    if resource_type != "textbook":
        lines.append("## Topics\n\n")
        for topic_id in resource.get("topics", []):
            lines.append(
                f"- [{topic_title(topic_id, topics)}]"
                f"({PATH_FROM_RESOURCES_TO_TOPICS}/{topic_id}.md)\n"
            )
        lines.append("\n")

    lines.append("## Summary\n\n")
    lines.append(f"{resource['summary']}\n\n")

    lines.append("## Access\n\n")
    if resource_type == "textbook" and is_defined(resource.get("path")):
        path = str(resource["path"]).strip()
        lines.append(pdf_embed_html(path, resource["title"], asset_link))
        lines.append("\n\n")
        published_asset_link = asset_link(path)
        lines.append(
            f'- <a href="{published_asset_link}" target="_blank" rel="noopener noreferrer">Open textbook PDF</a>\n'
        )
    elif is_defined(resource.get("url")):
        url = str(resource["url"]).strip()
        lines.append(
            f'- External resource: <a href="{url}" target="_blank" rel="noopener noreferrer">'
            f'{resource["title"]}</a>\n'
        )
    elif is_defined(resource.get("path")):
        published_asset_link = asset_link(str(resource["path"]))
        lines.append(
            f'- Repository asset: [{resource["title"]}]'
            f'({published_asset_link})\n'
        )
    lines.append("\n")

    if resource.get("slides_ref"):
        ref = resources[resource["slides_ref"]]
        lines.append(
            "- **Associated slides:** "
            f"{resource_page_link(ref, from_section='resources')}\n"
        )
    if resource.get("notebook_ref"):
        ref = resources[resource["notebook_ref"]]
        lines.append(
            "- **Associated notebook:** "
            f"{resource_page_link(ref, from_section='resources')}\n"
        )
    if resource.get("slides_ref") or resource.get("notebook_ref"):
        lines.append("\n")

    lines.append(build_related_lines(resource, resources))
    lines.append(build_metadata_details(resource, topics))
    return "".join(lines)
