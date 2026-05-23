from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.runtime_core.session import EngineSession, SessionMode


@dataclass(frozen=True)
class RuntimeContext:
    workspace_dir: Path
    session_id: str | None = None
    conversation: str | None = None
    mode: SessionMode = SessionMode.ACT
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_session(cls, session: EngineSession, *, metadata: dict[str, Any] | None = None) -> "RuntimeContext":
        return cls(
            workspace_dir=session.workspace_dir,
            session_id=session.session_id,
            conversation=session.conversation,
            mode=session.mode,
            metadata=dict(metadata or {}),
        )
