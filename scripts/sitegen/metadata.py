"""Metadata and topic helpers."""

from __future__ import annotations

from typing import Any

import yaml


def topic_title(topic_id: str, topics: dict[str, dict[str, Any]]) -> str:
    """Return the human-readable topic title."""
    return topics.get(topic_id, {"title": topic_id})["title"]


def track_title(track_id: str) -> str:
    """Return a readable title for a track id."""
    parts = str(track_id).replace("_", "-").split("-")
    return " ".join(part.upper() if part.lower() == "epfl" else part.capitalize() for part in parts)


def build_metadata_details(
    resource: dict[str, Any], topics: dict[str, dict[str, Any]]
) -> str:
    """Render collapsible raw metadata for any resource page."""
    payload: dict[str, Any] = {}
    ordered_keys = [
        "id",
        "title",
        "type",
        "topics",
        "tracks",
        "format",
        "path",
        "url",
        "variants",
        "question_source",
        "answer_source",
        "book_chapter",
        "book_section",
        "related",
        "slides_ref",
        "exercises_ref",
        "notebook_ref",
        "duration",
        "date",
        "author",
        "version",
        "language",
        "position",
        "summary",
    ]

    for key in ordered_keys:
        value = resource.get(key)
        if key == "topics":
            value = [
                topic_title(topic_id, topics)
                for topic_id in resource.get("topics", [])
            ]
        if key == "tracks":
            value = [
                track_title(track_id)
                for track_id in resource.get("tracks", [])
            ]
        if value in (None, "", []):
            continue
        payload[key] = value

    rendered = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).rstrip()
    lines = [
        '<details class="resource-metadata">\n',
        '<summary title="Show raw metadata">ⓘ Metadata</summary>\n\n',
        "```yaml\n",
        rendered,
        "\n```\n",
        "</details>\n\n",
    ]
    return "".join(lines)
