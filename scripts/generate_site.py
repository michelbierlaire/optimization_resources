"""Generate MkDocs pages from the pedagogical resource catalog."""

from __future__ import annotations

from sitegen.io import load_resources, load_topics, load_tracks
from sitegen.writers import write_resource_pages, write_topic_pages, write_track_pages


def main() -> None:
    """Generate all derived markdown pages."""
    topics = load_topics()
    tracks = load_tracks()
    resources = load_resources()
    write_topic_pages(topics, tracks, resources)
    write_track_pages(tracks, topics, resources)
    write_resource_pages(topics, resources)


if __name__ == "__main__":
    main()
