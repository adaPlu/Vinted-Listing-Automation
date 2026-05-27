"""Inventory agent v2: duplicate detection, metadata persistence, and pricing history."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from database.db_manager import DBManager


class InventoryAgent:
    def __init__(self) -> None:
        self.db = DBManager()

    def _hash_file(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def folder_fingerprint(self, folder: Path, images: Iterable[str]) -> str:
        parts = [folder.name]
        for image in sorted(images):
            path = Path(image)
            if path.exists():
                parts.append(path.name)
                parts.append(self._hash_file(path))
        return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()

    def is_duplicate_folder(self, folder: Path, images: list[str]) -> bool:
        fingerprint = self.folder_fingerprint(folder, images)
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT status FROM items WHERE folder_fingerprint = ?",
                (fingerprint,),
            ).fetchone()
        return bool(row and row["status"] in {"uploaded", "posted", "processing"})

    def upsert_item(self, folder: Path, images: list[str], status: str = "pending") -> None:
        fingerprint = self.folder_fingerprint(folder, images)
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO items(folder_name, folder_path, folder_fingerprint, status)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(folder_name) DO UPDATE SET
                    folder_path = excluded.folder_path,
                    folder_fingerprint = excluded.folder_fingerprint,
                    status = excluded.status,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (folder.name, str(folder.resolve()), fingerprint, status),
            )
            item_id = conn.execute(
                "SELECT id FROM items WHERE folder_name = ?",
                (folder.name,),
            ).fetchone()["id"]

            conn.execute("DELETE FROM item_images WHERE item_id = ?", (item_id,))
            for image in images:
                path = Path(image)
                if path.exists():
                    conn.execute(
                        """
                        INSERT INTO item_images(item_id, image_path, image_hash)
                        VALUES (?, ?, ?)
                        """,
                        (item_id, str(path.resolve()), self._hash_file(path)),
                    )
            conn.commit()

    def update_status(self, folder_name: str, status: str, error: str | None = None) -> None:
        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE items
                SET status = ?, error = ?, updated_at = CURRENT_TIMESTAMP
                WHERE folder_name = ?
                """,
                (status, error, folder_name),
            )
            conn.commit()

    def save_vision_metadata(self, folder_name: str, metadata: dict) -> None:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT id FROM items WHERE folder_name = ?",
                (folder_name,),
            ).fetchone()
            if not row:
                return

            item_id = row["id"]
            conn.execute(
                """
                INSERT INTO vision_metadata(
                    item_id, source, category, brand, colors, pattern,
                    material, style, gender, keywords, confidence, raw_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    metadata.get("source"),
                    metadata.get("category"),
                    metadata.get("brand"),
                    json.dumps(metadata.get("colors", [])),
                    metadata.get("pattern"),
                    metadata.get("material"),
                    metadata.get("style"),
                    metadata.get("gender"),
                    json.dumps(metadata.get("keywords", [])),
                    float(metadata.get("confidence", 0) or 0),
                    json.dumps(metadata),
                ),
            )
            conn.commit()

    def mark_uploaded(self, folder: Path, listing: dict, pricing_result: dict) -> None:
        vision = listing.get("vision_metadata", {}) or {}

        with self.db.connect() as conn:
            conn.execute(
                """
                UPDATE items
                SET status = 'uploaded',
                    title = ?,
                    description = ?,
                    category = ?,
                    brand = ?,
                    color = ?,
                    material = ?,
                    style = ?,
                    gender = ?,
                    size_guess = ?,
                    listing_price = ?,
                    price = ?,
                    marketplace = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE folder_name = ?
                """,
                (
                    str(listing.get("title", "")),
                    str(listing.get("description", "")),
                    str(listing.get("category", "")),
                    str(vision.get("brand", "")),
                    ", ".join(vision.get("colors", []) or []),
                    str(vision.get("material", "")),
                    str(vision.get("style", "")),
                    str(vision.get("gender", "")),
                    str(vision.get("size_guess", "")),
                    float(listing.get("price", 0) or 0),
                    float(listing.get("price", 0) or 0),
                    "vinted",
                    folder.name,
                ),
            )

            row = conn.execute(
                "SELECT id FROM items WHERE folder_name = ?",
                (folder.name,),
            ).fetchone()

            if row:
                conn.execute(
                    """
                    INSERT INTO pricing_history(
                        item_id, source, base_price, final_price, confidence, details
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["id"],
                        pricing_result.get("source"),
                        float(pricing_result.get("base_price", 0) or 0),
                        float(pricing_result.get("final_price", 0) or 0),
                        float(pricing_result.get("confidence", 0) or 0),
                        json.dumps(pricing_result),
                    ),
                )
            conn.commit()

    def record_event(self, folder_name: str, event_type: str, message: str | None = None) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO events(folder_name, event_type, message) VALUES (?, ?, ?)",
                (folder_name, event_type, message),
            )
            conn.commit()
