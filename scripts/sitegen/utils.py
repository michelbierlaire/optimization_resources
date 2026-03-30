"""Generic utility helpers for the site generator."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def is_defined(value: Any) -> bool:
    """Return True when a metadata value is meaningfully defined."""
    return value is not None and str(value).strip() != ""


def normalized_resource_type(resource: dict[str, Any]) -> str:
    """Return the normalized resource type."""
    return str(resource.get("type", "")).strip().lower()


def normalized_resource_format(resource: dict[str, Any]) -> str:
    """Return the normalized resource format."""
    return str(resource.get("format", "")).strip().lower()


def generated_file_notice() -> str:
    """Return a standard header for generated markdown files."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"<!-- This file was automatically generated on {timestamp}. -->\n\n"
