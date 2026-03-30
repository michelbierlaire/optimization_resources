"""Link-generation helpers for assets and resource pages."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from .config import (
    ASSETS_DIR,
    PATH_FROM_RESOURCES_TO_ITEMS,
    PATH_FROM_TOPICS_TO_RESOURCES,
)
from .utils import is_defined


def asset_link(path: str, from_section: str = "resources") -> str:
    """Return a relative link to a published asset."""
    cleaned = str(path).strip().lstrip("/")
    asset_path = PurePosixPath(
        cleaned if cleaned.startswith(f"{ASSETS_DIR}/") else f"{ASSETS_DIR}/{cleaned}"
    )

    if from_section == "resources":
        prefix = PurePosixPath("../..")
    elif from_section in {
        "topics",
        "tracks",
        "textbook",
        "slides",
        "notebooks",
        "exercises",
        "videos",
        "resources_index",
    }:
        prefix = PurePosixPath("..")
    elif from_section == "home":
        prefix = PurePosixPath(".")
    else:
        raise ValueError(f"Unknown section '{from_section}'")

    return str(prefix / asset_path)


def resource_link(resource: dict[str, Any], from_section: str = "resources") -> str:
    """Return a markdown/HTML link to the underlying asset or external URL."""
    if is_defined(resource.get("url")):
        target = str(resource["url"]).strip()
        return (
            f'<a href="{target}" target="_blank" rel="noopener noreferrer">'
            f'{resource["title"]}</a>'
        )
    if is_defined(resource.get("path")):
        target = asset_link(str(resource["path"]), from_section=from_section)
        return f'[{resource["title"]}]({target})'
    return resource["title"]


def resource_page_link(resource: dict[str, Any], from_section: str = "resources") -> str:
    """Return a markdown link to the generated detail page for a resource."""
    if from_section == "topics":
        target = f"{PATH_FROM_TOPICS_TO_RESOURCES}/{resource['id']}.md"
    elif from_section == "resources":
        target = f"{resource['id']}.md"
    else:
        raise ValueError(f"Unknown section '{from_section}'")
    return f'[{resource["title"]}]({target})'
