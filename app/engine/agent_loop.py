from __future__ import annotations

from dataclasses import dataclass

from app.models.session import ProjectSession, SessionMode


@dataclass(frozen=True)
class AgentTaskContext:
    workspace_dir: str
    session_mode: SessionMode = SessionMode.ACT
    session_id: str | None = None
    conversation: str | None = None
    workflow_id: str | None = None
    subtask_id: str | None = None
    metadata: dict[str, str] | None = None

    @classmethod
    def from_session(
        cls,
        session: ProjectSession,
        *,
        workflow_id: str | None = None,
        subtask_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> "AgentTaskContext":
        return cls(
            workspace_dir=str(session.workspace_dir),
            session_mode=session.mode,
            session_id=session.session_id,
            conversation=session.conversation,
            workflow_id=workflow_id,
            subtask_id=subtask_id,
            metadata=metadata,
        )
