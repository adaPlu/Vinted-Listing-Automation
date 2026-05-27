"""eBay marketplace agent scaffold."""

from __future__ import annotations

from typing import Any

from agents.platform_base import MarketplaceAgent


class EbayAgent(MarketplaceAgent):
    platform_name = "ebay"

    def create_draft(self, image_paths: list[str], listing: dict[str, Any]) -> tuple[bool, bool]:
        print("eBay draft creation is scaffolded for Sprint 2.")
        print("Future work: OAuth, listing API, shipping policies, sold comps.")
        return False, False
