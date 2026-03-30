"""Top-level page writers for topics, resources, and section indexes."""

from __future__ import annotations

from collections import defaultdict
import shutil
from typing import Any

from .config import DOCS_DIR, RESOURCE_ITEMS_DIR, TYPE_TO_SECTION
from .links import asset_link, resource_page_link
from .metadata import topic_title
from .resources.exercise import build_exercise_page
from .resources.generic import build_generic_page
from .resources.notebook import build_notebook_page
from .resources.slides import build_slides_page
from .resources.video import build_video_page
from .utils import (
    generated_file_notice,
    is_defined,
    normalized_resource_format,
    normalized_resource_type,
)


def track_title(track_id: str, tracks: dict[str, dict[str, Any]]) -> str:
    """Return the human-readable track title."""
    return tracks.get(track_id, {"title": track_id})["title"]


def position_key(resource: dict[str, Any]) -> tuple[int, ...]:
    """Return a sortable key derived from the string-based `position` field."""
    position = resource.get("position")
    if position in (None, ""):
        return (999999,)
    return tuple(int(part) for part in str(position).split("."))


def build_type_navigation_block(
    resource: dict[str, Any],
    previous_resource: dict[str, Any] | None,
    next_resource: dict[str, Any] | None,
) -> str:
    """Render previous/next navigation within the same resource type."""
    if previous_resource is None and next_resource is None:
        return ""

    resource_type = normalized_resource_type(resource)
    lines = ["## Navigation\n\n"]
    if previous_resource is not None:
        lines.append(
            f"- Previous {resource_type}: "
            f"[{previous_resource['title']}]({previous_resource['id']}.md)\n"
        )
    if next_resource is not None:
        lines.append(
            f"- Next {resource_type}: "
            f"[{next_resource['title']}]({next_resource['id']}.md)\n"
        )
    lines.append("\n")
    return "".join(lines)



def build_navigation_by_id(
    by_type: dict[str, list[dict[str, Any]]]
) -> dict[str, str]:
    """Build a previous/next navigation block for each resource id."""
    navigation_by_id: dict[str, str] = {}
    for resource_type, resources_of_type in by_type.items():
        ordered_resources = sorted(resources_of_type, key=position_key)
        for index, resource in enumerate(ordered_resources):
            previous_resource = ordered_resources[index - 1] if index > 0 else None
            next_resource = (
                ordered_resources[index + 1]
                if index + 1 < len(ordered_resources)
                else None
            )
            navigation_by_id[resource["id"]] = build_type_navigation_block(
                resource,
                previous_resource,
                next_resource,
            )
    return navigation_by_id


def write_topic_pages(
    topics: dict[str, dict[str, Any]],
    tracks: dict[str, dict[str, Any]],
    resources: dict[str, dict[str, Any]],
) -> None:
    """Generate one page per topic."""
    topic_dir = DOCS_DIR / "topics"
    topic_dir.mkdir(parents=True, exist_ok=True)
    for old_page in topic_dir.glob("*.md"):
        old_page.unlink()

    by_topic: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for resource in resources.values():
        for topic_id in resource.get("topics", []):
            by_topic[topic_id].append(resource)

    topic_index_lines = [
        generated_file_notice(),
        "# Topics\n\n",
        "Browse the content by topic.\n\n",
    ]
    for topic_id, topic in topics.items():
        page = topic_dir / f"{topic_id}.md"
        title = topic["title"]
        page_lines = [generated_file_notice(), f"# {title}\n\n"]
        parent = topic.get("parent")
        if parent:
            page_lines.append(
                f"**Parent topic:** [{topic_title(parent, topics)}]"
                f"({parent}.md)\n\n"
            )

        resources_for_topic = sorted(by_topic.get(topic_id, []), key=position_key)
        if resources_for_topic:
            page_lines.append("## Resources\n\n")
            for resource in resources_for_topic:
                page_lines.append(
                    f"### {resource_page_link(resource, from_section='topics')}\n\n"
                )
                page_lines.append(f"- **Type:** {resource['type']}\n")
                page_lines.append(f"- **Format:** {resource.get('format', '')}\n")
                track_labels = [
                    track_title(track_id, tracks)
                    for track_id in resource.get("tracks", [])
                ]
                if track_labels:
                    page_lines.append(
                        f"- **Tracks:** {', '.join(track_labels)}\n"
                    )
                if resource.get("duration"):
                    page_lines.append(f"- **Duration:** {resource['duration']}\n")
                if resource.get("book_chapter"):
                    page_lines.append(
                        f"- **Book chapter:** {resource['book_chapter']}\n"
                    )
                page_lines.append(f"- **Date:** {resource['date']}\n\n")
                page_lines.append(f"{resource['summary']}\n\n")
        else:
            page_lines.append(
                "No resource is currently associated with this topic.\n"
            )

        page.write_text("".join(page_lines), encoding="utf-8")
        topic_index_lines.append(f"- [{title}]({topic_id}.md)\n")

    (topic_dir / "index.md").write_text(
        "".join(topic_index_lines) + "\n", encoding="utf-8"
    )


def write_track_pages(
    tracks: dict[str, dict[str, Any]],
    topics: dict[str, dict[str, Any]],
    resources: dict[str, dict[str, Any]],
) -> None:
    """Generate one page per teaching track."""
    track_dir = DOCS_DIR / "tracks"
    track_dir.mkdir(parents=True, exist_ok=True)
    for old_page in track_dir.glob("*.md"):
        old_page.unlink()

    by_track: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for resource in resources.values():
        for track_id in resource.get("tracks", []):
            by_track[track_id].append(resource)

    track_index_lines = [
        generated_file_notice(),
        "# Tracks\n\n",
        "Browse the content by teaching track.\n\n",
    ]

    for track_id, track in tracks.items():
        page = track_dir / f"{track_id}.md"
        title = track["title"]
        page_lines = [generated_file_notice(), f"# {title}\n\n"]

        description = track.get("description") or ""
        if is_defined(description):
            page_lines.append(f"{description}\n\n")

        resources_for_track = sorted(by_track.get(track_id, []), key=position_key)
        if resources_for_track:
            grouped_by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for resource in resources_for_track:
                grouped_by_type[normalized_resource_type(resource)].append(resource)

            for resource_type in sorted(grouped_by_type):
                page_lines.append(f"## {resource_type.title()}\n\n")
                for resource in grouped_by_type[resource_type]:
                    page_lines.append(
                        f"### {resource_page_link(resource, from_section='topics')}\n\n"
                    )
                    topic_labels = [
                        topic_title(topic_id, topics)
                        for topic_id in resource.get("topics", [])
                    ]
                    if topic_labels:
                        page_lines.append(
                            f"- **Topics:** {', '.join(topic_labels)}\n"
                        )
                    if resource.get("book_chapter"):
                        page_lines.append(
                            f"- **Book chapter:** {resource['book_chapter']}\n"
                        )
                    if resource.get("duration"):
                        page_lines.append(
                            f"- **Duration:** {resource['duration']}\n"
                        )
                    page_lines.append(f"- **Date:** {resource['date']}\n\n")
                    summary = resource.get("summary") or ""
                    if is_defined(summary):
                        page_lines.append(f"{summary}\n\n")
        else:
            page_lines.append(
                "No resource is currently associated with this track.\n"
            )

        page.write_text("".join(page_lines), encoding="utf-8")
        track_index_lines.append(f"- [{title}]({track_id}.md)\n")

    (track_dir / "index.md").write_text(
        "".join(track_index_lines) + "\n", encoding="utf-8"
    )


def write_resource_pages(
    topics: dict[str, dict[str, Any]], resources: dict[str, dict[str, Any]]
) -> None:
    """Generate resource index pages and detailed resource pages."""
    resources_dir = DOCS_DIR / "resources"
    resources_dir.mkdir(parents=True, exist_ok=True)

    detail_dir = resources_dir / "items"
    if detail_dir.exists():
        shutil.rmtree(detail_dir)
    detail_dir.mkdir(parents=True, exist_ok=True)

    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for resource in resources.values():
        resource_type = normalized_resource_type(resource)
        by_type[resource_type].append(resource)
    navigation_by_id = build_navigation_by_id(by_type)

    all_lines = [
        generated_file_notice(),
        "# Resources\n\n",
        "All catalogued resources.\n\n",
    ]
    for resource in sorted(
        resources.values(),
        key=lambda r: (r["type"], position_key(r), r["title"]),
    ):
        detail_rel = f"items/{resource['id']}.md"
        all_lines.append(
            f"- [{resource['title']}]({detail_rel}) — {resource['type']}\n"
        )
    all_lines.append("\n")
    (resources_dir / "index.md").write_text(
        "".join(all_lines), encoding="utf-8"
    )

    for resource in resources.values():
        resource_type = normalized_resource_type(resource)
        resource_format = normalized_resource_format(resource)

        if resource_type == "video" or resource_format == "video":
            content = build_video_page(resource, topics, resources)
        elif resource_type == "slides":
            content = build_slides_page(resource, topics, resources, asset_link)
        elif resource_type == "exercise":
            content = build_exercise_page(
                resource, topics, resources, asset_link
            )
        elif resource_type == "notebook":
            content = build_notebook_page(resource, topics, resources)
        else:
            content = build_generic_page(resource, topics, resources)

        navigation_block = navigation_by_id.get(resource["id"], "")

        metadata_start = content.find('<details class="resource-metadata">')
        if metadata_start != -1:
            metadata_block = content[metadata_start:]
            main_content = content[:metadata_start]
            final_content = main_content + navigation_block + metadata_block
        else:
            final_content = content + navigation_block

        (detail_dir / f"{resource['id']}.md").write_text(
            generated_file_notice() + final_content,
            encoding="utf-8",
        )

    for resource_type, section in TYPE_TO_SECTION.items():
        section_dir = DOCS_DIR / section
        if section_dir.exists():
            shutil.rmtree(section_dir)
        section_dir.mkdir(parents=True, exist_ok=True)
        page_path = section_dir / "index.md"
        resources_of_type = sorted(by_type.get(resource_type, []), key=position_key)

        if resource_type == "textbook" and len(resources_of_type) == 1:
            textbook_page = build_generic_page(resources_of_type[0], topics, resources)
            page_path.write_text(
                generated_file_notice() + textbook_page, encoding="utf-8"
            )
            continue

        lines = [generated_file_notice(), f"# {section.title()}\n\n"]
        lines.append(f"Resources of type `{resource_type}`.\n\n")
        for resource in resources_of_type:
            lines.append(
                f"## [{resource['title']}]"
                f"(../{RESOURCE_ITEMS_DIR}/{resource['id']}.md)\n\n"
            )
            summary = resource.get("summary") or ""
            if is_defined(summary):
                lines.append(f"{summary}\n\n")
        page_path.write_text("".join(lines), encoding="utf-8")
