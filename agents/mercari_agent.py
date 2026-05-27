"""Mercari marketplace agent scaffold."""

from __future__ import annotations

from typing import Any

from agents.platform_base import MarketplaceAgent


class MercariAgent(MarketplaceAgent):
    platform_name = "mercari"

    def create_draft(self, image_paths: list[str], listing: dict[str, Any]) -> tuple[bool, bool]:
        print("Mercari draft creation is scaffolded for Sprint 2.")
        print("Future work: browser automation and offer strategy.")
        return False, False
