"""Depop marketplace agent scaffold."""

from __future__ import annotations

from typing import Any

from agents.platform_base import MarketplaceAgent


class DepopAgent(MarketplaceAgent):
    platform_name = "depop"

    def create_draft(self, image_paths: list[str], listing: dict[str, Any]) -> tuple[bool, bool]:
        print("Depop draft creation is scaffolded for Sprint 2.")
        print("Future work: youth-market keywords, hashtags, and browser automation.")
        return False, False
