"""Validation helpers for loaded resources."""

from __future__ import annotations

from typing import Any

from .utils import is_defined, normalized_resource_type


def validate_resource(resource: dict[str, Any]) -> None:
    """Validate a resource entry from the catalog."""
    resource_type = normalized_resource_type(resource)

    if resource_type == "exercise":
        required_fields = ["question_source", "answer_source"]
        for field in required_fields:
            if not is_defined(resource.get(field)):
                raise ValueError(
                    f"Resource '{resource['id']}' must define '{field}'."
                )
        return

    if resource_type == "notebook":
        variants = resource.get("variants") or []
        if not variants:
            raise ValueError(
                f"Resource '{resource['id']}' must define at least one notebook variant."
            )
        for variant in variants:
            if not is_defined(variant.get("github_url")):
                raise ValueError(
                    f"Resource '{resource['id']}' has a notebook variant without 'github_url'."
                )
        return

    has_path = is_defined(resource.get("path"))
    has_url = is_defined(resource.get("url"))
    if has_path == has_url:
        raise ValueError(
            f"Resource '{resource['id']}' must define exactly one of 'path' or 'url'."
        )
