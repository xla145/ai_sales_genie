from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.runtime_core.session import EngineSession, SessionMode


class SessionStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ProjectSession(BaseModel):
    session_id: str
    project_id: str
    workspace_path: str
    conversation: str
    base_url: str | None = None
    llm_provider: str | None = None
    provider_session_ref: str | None = None
    mode: SessionMode = SessionMode.ACT
    status: SessionStatus = SessionStatus.ACTIVE
    metadata: dict[str, Any] = Field(default_factory=dict)
    hermes_session_ref: str | None = None
    message_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    current_model: str | None = None
    created_at: datetime
    updated_at: datetime

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
            "project_id": self.project_id,
            "mode": self.mode.value,
            "status": self.status.value,
            "message_count": self.message_count,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "current_model": self.current_model,
            "conversation": self.conversation,
            "workspace_path": self.workspace_path,
        }

    def to_engine_session(self, *, metadata: dict[str, Any] | None = None) -> EngineSession:
        merged_metadata = dict(self.metadata)
        if metadata:
            merged_metadata.update(metadata)
        return EngineSession(
            session_id=self.session_id,
            workspace_path=self.workspace_path,
            conversation=self.conversation,
            mode=self.mode,
            metadata=merged_metadata,
            message_count=self.message_count,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            current_model=self.current_model,
        )

    def sync_from_engine_session(self, engine_session: EngineSession) -> None:
        self.mode = engine_session.mode
        self.conversation = engine_session.conversation
        self.message_count = engine_session.message_count
        self.input_tokens = engine_session.input_tokens
        self.output_tokens = engine_session.output_tokens
        self.current_model = engine_session.current_model
        self.metadata.update(engine_session.metadata)
