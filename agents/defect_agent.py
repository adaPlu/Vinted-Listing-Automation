"""Defect detection agent for resale listings.

Sprint 2 implementation:
- Lightweight image-quality and defect-risk scanner.
- Uses OpenCV/Pillow-style heuristics when available.
- Fails safely and never blocks listing creation unless configured later.
"""

from __future__ import annotations

from pathlib import Path


class DefectAgent:
    """Detect possible visual defects and quality risks."""

    def inspect_images(self, image_paths: list[str]) -> dict:
        findings: list[dict] = []

        for image_path in image_paths:
            findings.extend(self._inspect_single_image(Path(image_path)))

        severity = "none"

        if any(item["severity"] == "high" for item in findings):
            severity = "high"
        elif any(item["severity"] == "medium" for item in findings):
            severity = "medium"
        elif findings:
            severity = "low"

        return {
            "has_possible_defects": bool(findings),
            "severity": severity,
            "findings": findings,
            "description_note": self._build_description_note(findings),
            "source": "heuristic",
        }

    def _inspect_single_image(self, image_path: Path) -> list[dict]:
        findings: list[dict] = []

        if not image_path.exists():
            return [{
                "image": str(image_path),
                "type": "missing_file",
                "severity": "high",
                "message": "Image file was missing during defect scan.",
            }]

        try:
            from PIL import Image, ImageStat

            image = Image.open(image_path).convert("RGB")
            stat = ImageStat.Stat(image)

            brightness = sum(stat.mean) / 3
            contrast = max(stat.stddev)

            if brightness < 45:
                findings.append({
                    "image": str(image_path),
                    "type": "dark_photo",
                    "severity": "medium",
                    "message": "Photo appears dark; inspect item carefully.",
                })

            if contrast < 18:
                findings.append({
                    "image": str(image_path),
                    "type": "low_contrast",
                    "severity": "low",
                    "message": "Photo appears low contrast; details may be hard to see.",
                })

        except Exception as exc:
            findings.append({
                "image": str(image_path),
                "type": "scan_failed",
                "severity": "low",
                "message": f"Defect scan failed safely: {exc}",
            })

        return findings

    def _build_description_note(self, findings: list[dict]) -> str:
        if not findings:
            return ""

        high_or_medium = [
            item for item in findings
            if item.get("severity") in {"high", "medium"}
        ]

        if not high_or_medium:
            return ""

        return (
            "Please review photos carefully. Automated image check flagged "
            "possible lighting or condition details for manual confirmation."
        )
