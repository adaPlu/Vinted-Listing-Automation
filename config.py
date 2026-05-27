"""Project configuration for the AI Reseller Suite."""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
IMAGE_FOLDER = PROJECT_ROOT / "listing_images"
LOG_FOLDER = PROJECT_ROOT / "logs"
SCREENSHOT_FOLDER = PROJECT_ROOT / "screenshots"

VINTED_NEW_ITEM_URL = "https://www.vinted.com/items/new"
CDP_ENDPOINT = "http://127.0.0.1:9222"

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

# Human-in-the-loop safety setting: the script should upload and fill a draft,
# then stop for manual review instead of posting automatically.
REQUIRE_HUMAN_REVIEW = True

DEFAULT_TIMEOUT_MS = 30_000
LONG_TIMEOUT_MS = 120_000
