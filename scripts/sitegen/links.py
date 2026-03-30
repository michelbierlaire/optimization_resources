"""Link-generation helpers for assets and resource pages."""

from __future__ import annotations

from typing import Any

from .config import (
    ASSETS_DIR,
    PATH_FROM_RESOURCES_TO_ITEMS,
    PATH_FROM_SITE_ROOT_TO_ASSETS,
    PATH_FROM_TOPICS_TO_RESOURCES,
)
from .utils import is_defined


def asset_link(path: str) -> str:
    """Return an absolute site link to a published asset."""
    cleaned = str(path).strip().lstrip("/")
    suffix = cleaned[len(ASSETS_DIR) + 1 :] if cleaned.startswith(f"{ASSETS_DIR}/") else cleaned
    return f"{PATH_FROM_SITE_ROOT_TO_ASSETS}/{suffix}"


def resource_link(resource: dict[str, Any]) -> str:
    """Return a markdown/HTML link to the underlying asset or external URL."""
    if is_defined(resource.get("url")):
        target = str(resource["url"]).strip()
        return (
            f'<a href="{target}" target="_blank" rel="noopener noreferrer">'
            f'{resource["title"]}</a>'
        )
    if is_defined(resource.get("path")):
        target = asset_link(str(resource["path"]))
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
