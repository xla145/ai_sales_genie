from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class SessionMode(str, Enum):
    PLAN = "plan"
    ACT = "act"


@dataclass
class EngineSession:
    session_id: str
    workspace_path: str
    conversation: str
    mode: SessionMode = SessionMode.ACT
    metadata: dict[str, Any] = field(default_factory=dict)
    message_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    current_model: str | None = None

    @property
    def workspace_dir(self) -> Path:
        return Path(self.workspace_path)

    def record_usage(self, *, input_tokens: int = 0, output_tokens: int = 0, model: str | None = None) -> None:
        self.input_tokens += max(0, input_tokens)
        self.output_tokens += max(0, output_tokens)
        if model:
            self.current_model = model

    def record_message(self, count: int = 1) -> None:
        self.message_count += max(0, count)

    def snapshot(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "mode": self.mode.value,
            "message_count": self.message_count,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "current_model": self.current_model,
            "conversation": self.conversation,
            "workspace_path": self.workspace_path,
            "metadata": dict(self.metadata),
        }
