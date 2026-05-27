"""Queue agent for bulk processing and resumable jobs."""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime


class QueueAgent:
    def __init__(self, queue_file: str = "queue_system/job_queue.json") -> None:
        self.queue_file = Path(queue_file)
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.queue_file.exists():
            self._save([])

    def _load(self) -> list[dict]:
        return json.loads(self.queue_file.read_text(encoding="utf-8"))

    def _save(self, data: list[dict]) -> None:
        self.queue_file.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

    def add_job(self, folder_name: str) -> None:
        data = self._load()

        data.append({
            "folder_name": folder_name,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "retry_count": 0,
        })

        self._save(data)

    def next_job(self) -> dict | None:
        data = self._load()

        for job in data:
            if job["status"] == "pending":
                job["status"] = "processing"
                self._save(data)
                return job

        return None

    def complete_job(self, folder_name: str) -> None:
        data = self._load()

        for job in data:
            if job["folder_name"] == folder_name:
                job["status"] = "completed"

        self._save(data)

    def fail_job(self, folder_name: str) -> None:
        data = self._load()

        for job in data:
            if job["folder_name"] == folder_name:
                job["status"] = "failed"
                job["retry_count"] += 1

        self._save(data)
