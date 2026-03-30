"""Notebook resource page builder."""

from __future__ import annotations

from typing import Any

from ..links import resource_page_link
from ..metadata import build_metadata_details, track_title
from ..related import build_simple_related_lines
from ..utils import is_defined


def notebook_iframe_html(rendered_url: str, title: str) -> str:
    """Return embeddable HTML for a rendered notebook view."""
    return (
        f'<iframe src="{rendered_url}" title="{title}" '
        'style="width: 100%; height: 80vh; border: none;"></iframe>'
    )


def github_blob_to_raw(url: str) -> str:
    """Convert a GitHub blob URL into a raw download URL."""
    cleaned = url.strip()
    if "github.com/" not in cleaned or "/blob/" not in cleaned:
        return cleaned
    return cleaned.replace(
        "https://github.com/", "https://raw.githubusercontent.com/"
    ).replace("/blob/", "/")


def github_blob_to_nbviewer(url: str) -> str:
    """Convert a GitHub blob URL into an nbviewer URL."""
    cleaned = url.strip()
    if "github.com/" not in cleaned:
        return cleaned
    return cleaned.replace("https://github.com/", "https://nbviewer.org/github/")


def notebook_interactive_default(variant: dict[str, Any]) -> str | None:
    """Return the preferred interactive mode for a notebook variant."""
    explicit = variant.get("interactive_default")
    if is_defined(explicit):
        return str(explicit).strip().lower()

    interactive = variant.get("interactive") or []
    if interactive:
        return str(interactive[0]).strip().lower()

    return None


def notebook_interactive_links(
    variant: dict[str, Any]
) -> list[tuple[str, str]]:
    """Return interactive links declared for a notebook variant."""
    links: list[tuple[str, str]] = []
    binder_url = variant.get("binder_url")
    jupyterlite_url = variant.get("jupyterlite_url")

    if is_defined(binder_url):
        links.append(("Run in Binder", str(binder_url).strip()))
    if is_defined(jupyterlite_url):
        links.append(("Run in JupyterLite", str(jupyterlite_url).strip()))

    return links


def build_notebook_variant_section(variant: dict[str, Any], embed: bool = False) -> str:
    """Render one notebook variant section."""
    github_url = str(variant["github_url"]).strip()
    rendered_url = str(
        variant.get("rendered_url") or github_blob_to_nbviewer(github_url)
    ).strip()
    download_url = str(
        variant.get("download_url") or github_blob_to_raw(github_url)
    ).strip()
    heading = str(variant.get("label") or "Notebook").strip()

    lines = [f"## {heading}\n\n"]
    if embed:
        lines.append(notebook_iframe_html(rendered_url, heading))
        lines.append("\n\n")
    lines.append(
        f'- <a href="{rendered_url}" target="_blank" '
        f'rel="noopener noreferrer">View notebook</a>\n'
    )
    lines.append(
        f'- <a href="{github_url}" target="_blank" '
        f'rel="noopener noreferrer">Open on GitHub</a>\n'
    )
    lines.append(
        f'- <a href="{download_url}" target="_blank" '
        f'rel="noopener noreferrer">Download notebook</a>\n'
    )

    interactive_links = notebook_interactive_links(variant)
    default_mode = notebook_interactive_default(variant)
    if interactive_links:
        for label, url in interactive_links:
            marker = (
                " (default)"
                if default_mode and default_mode in label.lower()
                else ""
            )
            lines.append(
                f'- <a href="{url}" target="_blank" '
                f'rel="noopener noreferrer">{label}</a>{marker}\n'
            )

    lines.append("\n")
    return "".join(lines)


def build_notebook_page(
    resource: dict[str, Any],
    topics: dict[str, dict[str, Any]],
    resources: dict[str, dict[str, Any]],
) -> str:
    """Render the markdown page for a notebook resource."""
    lines = [f"# Notebook: {resource['title']}\n\n"]
    track_labels = [
        track_title(track_id) for track_id in resource.get("tracks", [])
    ]
    if track_labels:
        heading = "Track" if len(track_labels) == 1 else "Tracks"
        lines.append(f"## {heading}\n\n")
        for label in track_labels:
            lines.append(f"- {label}\n")
        lines.append("\n")
    lines.append(f"{resource['summary']}\n\n")

    variants = resource.get("variants", [])
    embed_variant_id = None
    if len(variants) == 1:
        embed_variant_id = str(variants[0].get("id") or "").strip().lower()
    elif len(variants) > 1:
        for variant in variants:
            candidate_id = str(variant.get("id") or "").strip().lower()
            candidate_label = str(variant.get("label") or "").strip().lower()
            if candidate_id == "question" or "question" in candidate_label:
                embed_variant_id = candidate_id
                break

    for variant in variants:
        variant_id = str(variant.get("id") or "").strip().lower()
        should_embed = variant_id == embed_variant_id and embed_variant_id != ""
        lines.append(build_notebook_variant_section(variant, embed=should_embed))

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
