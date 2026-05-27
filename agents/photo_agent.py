"""Photo processing agent for resale listing images.

Features:
- Removes background when rembg is installed.
- Places item on clean white background.
- Auto-crops around the item.
- Resizes to marketplace-friendly square format.
- Improves brightness, contrast, sharpness, and color slightly.
- Outputs processed images for upload while preserving originals.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageEnhance, ImageOps, ImageFilter


class PhotoAgent:
    """Processes item photos before Vinted upload."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    def __init__(
        self,
        output_folder_name: str = "processed",
        canvas_size: int = 1600,
        padding_ratio: float = 0.10,
        white_background: tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        self.output_folder_name = output_folder_name
        self.canvas_size = canvas_size
        self.padding_ratio = padding_ratio
        self.white_background = white_background

    def process_folder(self, item_folder: Path | str) -> list[str]:
        """Process all supported images in an item folder and return output paths."""

        folder = Path(item_folder)
        output_folder = folder / self.output_folder_name
        output_folder.mkdir(exist_ok=True)

        raw_images = [
            file for file in sorted(folder.iterdir())
            if file.is_file()
            and file.suffix.lower() in self.SUPPORTED_EXTENSIONS
            and output_folder.name not in file.parts
        ]

        processed_paths: list[str] = []

        for index, image_path in enumerate(raw_images, start=1):
            try:
                output_path = output_folder / f"processed_{index:02d}.png"
                self.process_image(image_path, output_path)
                processed_paths.append(str(output_path.resolve()))
                print(f"Processed photo: {output_path}")
            except Exception as exc:
                print(f"Photo processing failed for {image_path}: {exc}")
                print("Using original image as fallback.")
                processed_paths.append(str(image_path.resolve()))

        return processed_paths

    def process_image(self, input_path: Path | str, output_path: Path | str) -> None:
        """Process one image and save it."""

        input_path = Path(input_path)
        output_path = Path(output_path)

        image = Image.open(input_path)
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGBA")

        image = self._remove_background_if_available(image)
        image = self._crop_to_content(image)
        image = self._place_on_square_canvas(image)
        image = self._enhance(image)

        output_path.parent.mkdir(exist_ok=True)
        image.save(output_path, "PNG")

    def _remove_background_if_available(self, image: Image.Image) -> Image.Image:
        """Use rembg if installed; otherwise keep original image."""

        try:
            from rembg import remove  # type: ignore

            print("Removing background with rembg...")
            return remove(image).convert("RGBA")
        except Exception as exc:
            print(f"rembg unavailable or failed; skipping background removal: {exc}")
            return image.convert("RGBA")

    def _crop_to_content(self, image: Image.Image) -> Image.Image:
        """Crop around non-transparent content if alpha exists."""

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        alpha = image.getchannel("A")
        bbox = alpha.getbbox()

        if not bbox:
            return image

        left, upper, right, lower = bbox
        width = right - left
        height = lower - upper

        pad = int(max(width, height) * self.padding_ratio)

        left = max(0, left - pad)
        upper = max(0, upper - pad)
        right = min(image.width, right + pad)
        lower = min(image.height, lower + pad)

        return image.crop((left, upper, right, lower))

    def _place_on_square_canvas(self, image: Image.Image) -> Image.Image:
        """Place item centered on a square white canvas."""

        canvas_size = self.canvas_size
        max_item_size = int(canvas_size * (1 - self.padding_ratio * 2))

        image.thumbnail((max_item_size, max_item_size), Image.LANCZOS)

        canvas = Image.new("RGBA", (canvas_size, canvas_size), self.white_background + (255,))

        x = (canvas_size - image.width) // 2
        y = (canvas_size - image.height) // 2

        canvas.alpha_composite(image, (x, y))

        return canvas.convert("RGB")

    def _enhance(self, image: Image.Image) -> Image.Image:
        """Apply light sales-safe enhancements."""

        image = image.convert("RGB")

        image = ImageEnhance.Brightness(image).enhance(1.06)
        image = ImageEnhance.Contrast(image).enhance(1.08)
        image = ImageEnhance.Color(image).enhance(1.04)
        image = ImageEnhance.Sharpness(image).enhance(1.15)

        return image
