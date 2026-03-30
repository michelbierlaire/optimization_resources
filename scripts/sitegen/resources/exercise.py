"""Exercise resource page builder."""

from __future__ import annotations

from typing import Any

from ..links import resource_page_link
from ..metadata import build_metadata_details, track_title
from ..related import build_simple_related_lines
from ..rendering import pdf_embed_html


def exercise_asset_paths(resource: dict[str, Any]) -> tuple[str, str]:
    """Return the published question and solution PDF paths for an exercise."""
    topics = resource.get("topics") or []
    topic_dir = str(topics[0]) if topics else "misc"
    base = f"assets/exercises/{topic_dir}/{resource['id']}"
    return f"/{base}-question.pdf", f"/{base}-solution.pdf"


def build_exercise_page(
    resource: dict[str, Any],
    topics: dict[str, dict[str, Any]],
    resources: dict[str, dict[str, Any]],
    asset_link_fn,
) -> str:
    """Render the markdown page for an exercise resource."""
    question_pdf, solution_pdf = exercise_asset_paths(resource)
    lines = [f"# Exercise: {resource['title']}\n\n"]
    track_labels = [
        track_title(track_id) for track_id in resource.get("tracks", [])
    ]
    if track_labels:
        heading = "Track" if len(track_labels) == 1 else "Tracks"
        lines.append(f"## {heading}\n\n")
        for label in track_labels:
            lines.append(f"- {label}\n")
        lines.append("\n")
    lines.append(pdf_embed_html(question_pdf, resource["title"], asset_link_fn))
    lines.append("\n\n")
    lines.append(f"{resource['summary']}\n\n")

    lines.append("## Solution\n\n")
    lines.append(f"- [Open solution]({solution_pdf})\n\n")

    if resource.get("slides_ref"):
        ref = resources[resource["slides_ref"]]
        lines.append("## Associated slides\n\n")
        lines.append(
            f"- {resource_page_link(ref, from_section='resources')}\n\n"
        )

    if resource.get("notebook_ref"):
        ref = resources[resource["notebook_ref"]]
        lines.append("## Associated notebook\n\n")
        lines.append(
            f"- {resource_page_link(ref, from_section='resources')}\n\n"
        )

    related_block = build_simple_related_lines(resource, resources)
    if related_block:
        lines.append(related_block)

    lines.append(build_metadata_details(resource, topics))
    return "".join(lines)
