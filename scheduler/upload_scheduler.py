"""Upload scheduling scaffold."""

from __future__ import annotations

from datetime import datetime


class UploadScheduler:
    def should_upload_now(self) -> bool:
        current_hour = datetime.now().hour

        preferred_hours = [
            9,
            12,
            18,
            20,
        ]

        return current_hour in preferred_hours
