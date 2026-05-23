from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
from uuid import uuid4

from app.clients.hermes_client import DEFAULT_BASE_URL
from app.models.project import Project
from app.models.session import ProjectSession
from app.storage.file_store import FileStore
from app.storage.header_paths import session_file_for_project, session_file_path
from app.storage.header_store import HeaderStore


class SessionService:
    REQUIRED_WORKSPACE_DIRS = ("runs", "logs", "outputs", "workflows")

    def __init__(self, header_store: HeaderStore | None = None) -> None:
        self.store = FileStore()
        self.header_store = header_store

    def list_sessions(self, project: Project) -> list[ProjectSession]:
        if self.header_store is not None:
            return self.header_store.list_sessions(project.project_id)

        sessions: list[ProjectSession] = []
        for session_file in sorted(self._sessions_dir(project).glob("*/session.json")):
            data = self.store.read_json(session_file)
            if data:
                sessions.append(ProjectSession.model_validate(data))
        return sessions

    def create_session(self, project: Project) -> ProjectSession:
        now = datetime.now()
        session_id = f"sess_{uuid4().hex[:8]}"
        workspace_dir = self._session_dir(project, session_id)
        workspace_dir.mkdir(parents=True, exist_ok=False)
        self.ensure_session_workspace(project=project, workspace_dir=workspace_dir, session_id=session_id)

        session = ProjectSession(
            session_id=session_id,
            project_id=project.project_id,
            created_id=project.created_id,
            update_id=project.update_id,
            workspace_path=str(workspace_dir),
            conversation=session_id,
            base_url=os.environ.get("HERMES_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
            created_at=now,
            updated_at=now,
        )
        self.save_session(project, session)
        return session

    def get_session(self, project: Project, session_id: str) -> ProjectSession:
        if self.header_store is not None:
            session = self.header_store.get_session(session_id)
            if session is None or session.project_id != project.project_id:
                raise FileNotFoundError(session_id)
            return session

        session_path = self._session_file(project, session_id)
        data = self.store.read_json(session_path)
        if not data:
            raise FileNotFoundError(session_id)
        return ProjectSession.model_validate(data)

    def resume_session(self, project: Project, session_id: str) -> ProjectSession:
        session = self.get_session(project, session_id)
        self.ensure_session_workspace(project=project, workspace_dir=session.workspace_dir, session_id=session.session_id)
        return session

    def get_or_create_default_session(self, project: Project) -> ProjectSession:
        if project.current_session_id:
            return self.resume_session(project, project.current_session_id)
        return self.create_session(project)

    def save_session(self, project: Project, session: ProjectSession) -> None:
        self.ensure_session_workspace(project=project, workspace_dir=session.workspace_dir, session_id=session.session_id)
        session.update_id = project.update_id
        session.updated_at = datetime.now()
        self.store.write_json(session_file_path(session), session.model_dump(mode="json"))
        if self.header_store is not None:
            self.header_store.upsert_session(session)

    def ensure_session_workspace(
        self,
        *,
        project: Project,
        workspace_dir: Path,
        session_id: str,
    ) -> None:
        workspace_dir.mkdir(parents=True, exist_ok=True)
        for name in self.REQUIRED_WORKSPACE_DIRS:
            (workspace_dir / name).mkdir(parents=True, exist_ok=True)

        session_file_for_project(project, session_id).parent.mkdir(parents=True, exist_ok=True)

    def _sessions_dir(self, project: Project) -> Path:
        return Path(project.workspace_path) / "sessions"

    def _session_dir(self, project: Project, session_id: str) -> Path:
        return self._sessions_dir(project) / session_id

    def _session_file(self, project: Project, session_id: str) -> Path:
        return self._session_dir(project, session_id) / "session.json"
