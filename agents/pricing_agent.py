"""Pricing agent with comps-aware fallback and fast-sale discount."""

from __future__ import annotations

from agents.comps_agent import CompsAgent


class PricingAgent:
    def __init__(self, fast_sale_discount: float = 0.60) -> None:
        self.fast_sale_discount = fast_sale_discount
        self.comps_agent = CompsAgent()

    def estimate_price(self, listing: dict, vision_metadata: dict | None = None) -> dict:
        title = str(listing.get("title", ""))
        category = str(listing.get("category", ""))

        comps = self.comps_agent.find_comps(title, category)
        average = self.comps_agent.average_price(comps)

        if average:
            base_price = average
            source = "market_comps"
            confidence = 0.75
        else:
            try:
                base_price = float(listing.get("price", 25) or 25)
            except Exception:
                base_price = 25.0

            source = "fallback_listing_price"
            confidence = 0.45

        final_price = round(base_price * self.fast_sale_discount, 2)

        return {
            "source": source,
            "base_price": base_price,
            "final_price": final_price,
            "confidence": confidence,
            "comps_count": len(comps),
            "discount_rule": self.fast_sale_discount,
        }
