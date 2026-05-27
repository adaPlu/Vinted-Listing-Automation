"""Bulk processing engine scaffold."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor


class BulkProcessor:
    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max_workers

    def process(self, items: list, callback):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(callback, item) for item in items]

            for future in futures:
                future.result()
