"""Shared marketplace agent interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MarketplaceAgent(ABC):
    platform_name = "base"

    @abstractmethod
    def create_draft(self, image_paths: list[str], listing: dict[str, Any]) -> tuple[bool, bool]:
        """Create a marketplace draft and return upload/fill status."""
        raise NotImplementedError

    def upload_images(self, image_paths: list[str]) -> bool:
        raise NotImplementedError

    def fill_listing(self, listing: dict[str, Any]) -> bool:
        raise NotImplementedError

    def review_submission(self) -> bool:
        return True
