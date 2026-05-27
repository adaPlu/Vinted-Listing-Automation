"""Listing generation agent with Vision metadata support."""

from __future__ import annotations

from pathlib import Path


class ListingAgent:
    def generate_listing(self, folder: Path, vision_metadata: dict | None = None) -> dict:
        vision_metadata = vision_metadata or {}

        base_name = folder.name.replace("_", " ").replace("-", " ").title()

        title = vision_metadata.get("title_suggestion") or base_name
        description = vision_metadata.get("description_suggestion") or (
            f"{base_name}. Good preowned condition. "
            "Please review all photos before purchasing."
        )

        category = vision_metadata.get("category") or self._guess_category(folder.name)
        tags = vision_metadata.get("keywords") or [
            word.lower()
            for word in folder.name.replace("_", " ").replace("-", " ").split()
            if len(word) > 2
        ]

        return {
            "title": title[:80],
            "description": description,
            "category": category,
            "price": 25.0,
            "tags": tags[:10],
            "vision_metadata": vision_metadata,
        }

    def _guess_category(self, text: str) -> str:
        lowered = text.lower()
        if "dress" in lowered:
            return "dress"
        if "shirt" in lowered or "top" in lowered:
            return "shirt"
        if "jeans" in lowered or "pants" in lowered:
            return "pants"
        if "shoes" in lowered:
            return "shoes"
        return "clothing"
