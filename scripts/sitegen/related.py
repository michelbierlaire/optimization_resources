"""Helpers for related-resource sections."""

from __future__ import annotations

from typing import Any
import warnings

from .links import resource_page_link


def build_simple_related_lines(
    resource: dict[str, Any],
    resources: dict[str, dict[str, Any]],
) -> str:
    """Render a compact related-resources section for simplified pages."""
    lines: list[str] = []

    if resource.get("book_chapter") or resource.get("book_section"):
        label = "Book"
        if resource.get("book_chapter"):
            label += f", chapter {resource['book_chapter']}"
        if resource.get("book_section"):
            label += f", section {resource['book_section']}"
        lines.append(f"- {label}\n")

    related_ids = resource.get("related") or []
    seen_related = set()
    for related_id in related_ids:
        if related_id in seen_related:
            continue
        seen_related.add(related_id)
        related = resources.get(related_id)
        if related is None:
            warnings.warn(
                f"Unknown related resource id '{related_id}' in resource "
                f"'{resource['id']}'"
            )
            continue
        lines.append(
            f"- {resource_page_link(related, from_section='resources')} "
            f"({related['type']})\n"
        )

    if not lines:
        return ""

    return "## Related resources\n\n" + "".join(lines) + "\n"


def build_related_lines(
    resource: dict[str, Any], resources: dict[str, dict[str, Any]]
) -> str:
    """Render the related resources section for generic pages."""
    related_ids = resource.get("related") or []
    if not related_ids:
        return ""
    lines = ["### Related resources\n"]
    for related_id in related_ids:
        related = resources.get(related_id)
        if related is None:
            warnings.warn(
                f"Unknown related resource id '{related_id}' in resource "
                f"'{resource['id']}'"
            )
            continue
        lines.append(
            f"- {resource_page_link(related, from_section='resources')} "
            f"({related['type']})\n"
        )
    lines.append("\n")
    return "".join(lines)
