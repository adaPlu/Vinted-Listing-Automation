"""SQLite helper for AI Reseller Suite v2."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class DBManager:
    def __init__(self, db_path: str | Path = "database/inventory.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        schema_path = Path("database/schema.sql")
        if not schema_path.exists():
            raise FileNotFoundError("Missing database/schema.sql")

        with self.connect() as conn:
            conn.executescript(schema_path.read_text(encoding="utf-8"))
            self._apply_migrations(conn)
            conn.commit()

    def _apply_migrations(self, conn: sqlite3.Connection) -> None:
        """Add new v2 columns safely when upgrading an existing DB."""
        existing = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(items)").fetchall()
        }

        migrations = {
            "description": "ALTER TABLE items ADD COLUMN description TEXT",
            "brand": "ALTER TABLE items ADD COLUMN brand TEXT",
            "color": "ALTER TABLE items ADD COLUMN color TEXT",
            "material": "ALTER TABLE items ADD COLUMN material TEXT",
            "style": "ALTER TABLE items ADD COLUMN style TEXT",
            "gender": "ALTER TABLE items ADD COLUMN gender TEXT",
            "size_guess": "ALTER TABLE items ADD COLUMN size_guess TEXT",
            "buy_price": "ALTER TABLE items ADD COLUMN buy_price REAL DEFAULT 0",
            "shipping_cost": "ALTER TABLE items ADD COLUMN shipping_cost REAL DEFAULT 0",
            "listing_price": "ALTER TABLE items ADD COLUMN listing_price REAL DEFAULT 0",
            "sold_price": "ALTER TABLE items ADD COLUMN sold_price REAL DEFAULT 0",
            "profit": "ALTER TABLE items ADD COLUMN profit REAL DEFAULT 0",
            "marketplace": "ALTER TABLE items ADD COLUMN marketplace TEXT DEFAULT 'vinted'",
            "listing_url": "ALTER TABLE items ADD COLUMN listing_url TEXT",
            "sold_status": "ALTER TABLE items ADD COLUMN sold_status TEXT DEFAULT 'unsold'",
        }

        for column, sql in migrations.items():
            if column not in existing:
                conn.execute(sql)

        image_cols = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(item_images)").fetchall()
        }
        if "processed_image_path" not in image_cols:
            conn.execute("ALTER TABLE item_images ADD COLUMN processed_image_path TEXT")
