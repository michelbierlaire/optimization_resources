"""Load topics and resources from YAML catalogs."""

from __future__ import annotations

from typing import Any
import warnings

import yaml

from .config import DATA_DIR, RESOURCE_DIR, TYPE_TO_SECTION
from .utils import is_defined, normalized_resource_type
from .validation import validate_resource


def load_topics() -> dict[str, dict[str, Any]]:
    """Load the topic catalog keyed by topic id."""
    with (DATA_DIR / "topics.yml").open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return {topic["id"]: topic for topic in data["topics"]}


def load_tracks() -> dict[str, dict[str, Any]]:
    """Load the track catalog keyed by track id."""
    tracks_path_yml = DATA_DIR / "tracks.yml"
    tracks_path_yaml = DATA_DIR / "tracks.yaml"

    if tracks_path_yml.exists():
        tracks_path = tracks_path_yml
    elif tracks_path_yaml.exists():
        tracks_path = tracks_path_yaml
    else:
        raise FileNotFoundError(
            "Could not find track catalog. Expected data/tracks.yml or data/tracks.yaml."
        )

    with tracks_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return {track["id"]: track for track in data["tracks"]}


def validate_resource_references(
    resources: dict[str, dict[str, Any]],
    tracks: dict[str, dict[str, Any]],
) -> None:
    """Validate that cross-resource references point to existing resources."""
    single_reference_fields = ["slides_ref", "notebook_ref"]
    multi_reference_fields = ["related", "exercises_ref"]

    for resource in resources.values():
        resource_id = resource.get("id", "<unknown>")

        track_ids = resource.get("tracks") or []
        if not track_ids:
            raise ValueError(
                f"Resource '{resource_id}' must belong to at least one track."
            )
        for track_id in track_ids:
            if not is_defined(track_id) or track_id not in tracks:
                raise ValueError(
                    f"Resource '{resource_id}' references unknown track '{track_id}'."
                )

        for field in single_reference_fields:
            ref_id = resource.get(field)
            if is_defined(ref_id) and ref_id not in resources:
                raise ValueError(
                    f"Resource '{resource_id}' references unknown {field} '{ref_id}'."
                )

        for field in multi_reference_fields:
            ref_ids = resource.get(field) or []
            for ref_id in ref_ids:
                if is_defined(ref_id) and ref_id not in resources:
                    raise ValueError(
                        f"Resource '{resource_id}' references unknown {field} '{ref_id}'."
                    )


def load_resources() -> dict[str, dict[str, Any]]:
    """Load all resources keyed by resource id."""
    resources: dict[str, dict[str, Any]] = {}
    tracks = load_tracks()
    yaml_paths = sorted(RESOURCE_DIR.glob("*.yml"))
    yaml_paths += sorted(RESOURCE_DIR.glob("*.yaml"))
    for path in yaml_paths:
        with path.open("r", encoding="utf-8") as stream:
            resource = yaml.safe_load(stream)
        resource["type"] = normalized_resource_type(resource)
        if resource["type"] not in TYPE_TO_SECTION:
            warnings.warn(
                f"Unknown resource type '{resource['type']}' in resource "
                f"'{resource.get('id', '<unknown>')}'"
            )
        validate_resource(resource)
        resources[resource["id"]] = resource
    validate_resource_references(resources, tracks)
    return resources
