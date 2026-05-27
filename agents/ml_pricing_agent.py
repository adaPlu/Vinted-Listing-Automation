"""Experimental ML pricing scaffold."""

from __future__ import annotations


class MLPricingAgent:
    def predict_sell_probability(self, listing: dict) -> float:
        title = str(listing.get("title", "")).lower()

        score = 0.50

        keywords = [
            "vintage",
            "nike",
            "rare",
            "y2k",
            "designer",
        ]

        for keyword in keywords:
            if keyword in title:
                score += 0.08

        return round(min(score, 0.95), 2)

    def recommend_price_adjustment(self, probability: float) -> float:
        if probability > 0.80:
            return 1.10

        if probability < 0.40:
            return 0.85

        return 1.00
