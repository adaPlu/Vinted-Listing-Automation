"""Comparable-sales pricing scaffold with safe manual fallback."""

from __future__ import annotations


class CompsAgent:
    def find_comps(self, query: str, category: str = "") -> list[dict]:
        # Live sold-comps searching should be added with APIs or approved sources.
        # This scaffold intentionally returns no live data to avoid brittle scraping.
        return []

    def average_price(self, comps: list[dict]) -> float | None:
        prices = []
        for comp in comps:
            try:
                prices.append(float(comp["price"]))
            except Exception:
                pass

        if not prices:
            return None

        return round(sum(prices) / len(prices), 2)
