"""Configuration constants for the site generator."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
RESOURCE_DIR = DATA_DIR / "resources"

TYPE_TO_SECTION = {
    "textbook": "textbook",
    "slides": "slides",
    "video": "videos",
    "exercise": "exercises",
    "notebook": "notebooks",
}

RESOURCE_ITEMS_DIR = "resources/items"
TOPICS_DIR = "topics"
ASSETS_DIR = "assets"

PATH_FROM_TOPICS_TO_RESOURCES = f"../{RESOURCE_ITEMS_DIR}"
PATH_FROM_RESOURCES_TO_ITEMS = "../items"
PATH_FROM_RESOURCES_TO_TOPICS = f"../../{TOPICS_DIR}"
PATH_FROM_SITE_ROOT_TO_ASSETS = f"/{ASSETS_DIR}"
