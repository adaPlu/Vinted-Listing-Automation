"""OpenAI Vision metadata agent with safe heuristic fallback.

Requires optional dependency:
    pip install openai

Environment:
    OPENAI_API_KEY must be set for real vision mode.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path


class VisionAgent:
    CATEGORY_KEYWORDS = {
        "dress": ["dress", "gown", "maxi", "mini"],
        "shirt": ["shirt", "tee", "tshirt", "top", "blouse"],
        "pants": ["pants", "jeans", "trousers", "leggings"],
        "jacket": ["jacket", "coat", "blazer", "hoodie"],
        "shoes": ["shoes", "sneakers", "boots", "heels"],
    }

    BRAND_KEYWORDS = [
        "nike", "adidas", "zara", "lululemon", "gap", "old navy",
        "h&m", "forever 21", "levi", "levis",
    ]

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def analyze_item(self, folder: Path, images: list[str]) -> dict:
        if os.getenv("OPENAI_API_KEY"):
            metadata = self._try_openai_vision(folder, images)
            if metadata:
                return metadata

        return self._heuristic_metadata(folder)

    def _heuristic_metadata(self, folder: Path) -> dict:
        text = folder.name.replace("_", " ").replace("-", " ").lower()
        return {
            "category": self._guess_category(text),
            "brand": self._guess_brand(text),
            "colors": [],
            "pattern": "",
            "material": "",
            "style": self._guess_style(text),
            "gender": "",
            "size_guess": "",
            "keywords": [word for word in text.split() if len(word) > 2],
            "confidence": 0.45,
            "source": "heuristic",
        }

    def _guess_category(self, text: str) -> str:
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return category
        return "clothing"

    def _guess_brand(self, text: str) -> str:
        for brand in self.BRAND_KEYWORDS:
            if brand in text:
                return brand.title()
        return ""

    def _guess_style(self, text: str) -> str:
        for style in ["y2k", "vintage", "boho", "goth", "streetwear", "formal", "casual"]:
            if style in text:
                return style
        return "casual"

    def _image_to_data_url(self, image_path: str) -> str:
        path = Path(image_path)
        suffix = path.suffix.lower().replace(".", "")
        mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix

        encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:image/{mime};base64,{encoded}"

    def _try_openai_vision(self, folder: Path, images: list[str]) -> dict | None:
        try:
            from openai import OpenAI
        except Exception as exc:
            print(f"OpenAI package unavailable; using heuristic vision fallback: {exc}")
            return None

        if not images:
            return None

        try:
            client = OpenAI()

            image_payload = []
            for image in images[:4]:
                image_payload.append({
                    "type": "image_url",
                    "image_url": {"url": self._image_to_data_url(image)}
                })

            prompt = """
Analyze this resale clothing/accessory item for a Vinted listing.
Return ONLY valid JSON with these keys:
category, brand, colors, pattern, material, style, gender, size_guess,
keywords, title_suggestion, description_suggestion, confidence.
Be conservative. Do not invent a brand if it is not visible.
"""

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            *image_payload,
                        ],
                    }
                ],
                temperature=0.2,
            )

            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)

            return {
                "category": data.get("category", ""),
                "brand": data.get("brand", ""),
                "colors": data.get("colors", []),
                "pattern": data.get("pattern", ""),
                "material": data.get("material", ""),
                "style": data.get("style", ""),
                "gender": data.get("gender", ""),
                "size_guess": data.get("size_guess", ""),
                "keywords": data.get("keywords", []),
                "title_suggestion": data.get("title_suggestion", ""),
                "description_suggestion": data.get("description_suggestion", ""),
                "confidence": float(data.get("confidence", 0.75) or 0.75),
                "source": "openai_vision",
            }

        except Exception as exc:
            print(f"OpenAI Vision failed; using heuristic fallback: {exc}")
            return None
