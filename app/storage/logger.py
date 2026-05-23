from __future__ import annotations

from datetime import datetime
from pathlib import Path


class ProjectLogger:
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {level.upper()} {message}\n")

    def info(self, message: str) -> None:
        self.log("INFO", message)

    def error(self, message: str) -> None:
        self.log("ERROR", message)

    def stream_chunk(self, text: str) -> None:
        if not text:
            return
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(text)
