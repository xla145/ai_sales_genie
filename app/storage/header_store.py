from __future__ import annotations

from dataclasses import dataclass

from app.models.project import Project, ProjectStatus
from app.models.run import PhaseId, ProjectRun, RunStatus, WorkflowRun, WorkflowStatus
from app.models.session import ProjectSession, SessionStatus


@dataclass
class HeaderStore:
    def upsert_project(self, project: Project) -> None:
        raise NotImplementedError

    def get_project(self, project_id: str, user_id: str) -> Project | None:
        raise NotImplementedError

    def list_projects(self, user_id: str) -> list[Project]:
        raise NotImplementedError

    def delete_project(self, project_id: str) -> None:
        raise NotImplementedError

    def upsert_session(self, project_session: ProjectSession) -> None:
        raise NotImplementedError

    def list_sessions(self, project_id: str) -> list[ProjectSession]:
        raise NotImplementedError

    def get_session(self, session_id: str) -> ProjectSession | None:
        raise NotImplementedError

    def upsert_run(self, run: ProjectRun) -> None:
        raise NotImplementedError

    def list_runs(self, project_id: str, session_id: str | None = None) -> list[ProjectRun]:
        raise NotImplementedError

    def get_run(self, run_id: str) -> ProjectRun | None:
        raise NotImplementedError

    def upsert_workflow(self, workflow: WorkflowRun) -> None:
        raise NotImplementedError

    def get_workflow(self, workflow_id: str) -> WorkflowRun | None:
        raise NotImplementedError


class InMemoryHeaderStore(HeaderStore):
    def __init__(self) -> None:
        self.projects: dict[str, Project] = {}
        self.sessions: dict[str, ProjectSession] = {}
        self.runs: dict[str, ProjectRun] = {}
        self.workflows: dict[str, WorkflowRun] = {}

    def upsert_project(self, project: Project) -> None:
        self.projects[project.project_id] = project.model_copy(deep=True)

    def get_project(self, project_id: str, user_id: str) -> Project | None:
        project = self.projects.get(project_id)
        if project is None or project.created_id != user_id:
            return None
        return project.model_copy(deep=True)

    def list_projects(self, user_id: str) -> list[Project]:
        return [project.model_copy(deep=True) for project in self.projects.values() if project.created_id == user_id]

    def delete_project(self, project_id: str) -> None:
        self.projects.pop(project_id, None)

    def upsert_session(self, project_session: ProjectSession) -> None:
        self.sessions[project_session.session_id] = project_session.model_copy(deep=True)

    def list_sessions(self, project_id: str) -> list[ProjectSession]:
        return [
            session.model_copy(deep=True)
            for session in self.sessions.values()
            if session.project_id == project_id
        ]

    def get_session(self, session_id: str) -> ProjectSession | None:
        session = self.sessions.get(session_id)
        return session.model_copy(deep=True) if session is not None else None

    def upsert_run(self, run: ProjectRun) -> None:
        self.runs[run.run_id] = run.model_copy(deep=True)

    def list_runs(self, project_id: str, session_id: str | None = None) -> list[ProjectRun]:
        runs = [run for run in self.runs.values() if run.project_id == project_id]
        if session_id is not None:
            runs = [run for run in runs if run.session_id == session_id]
        return [run.model_copy(deep=True) for run in runs]

    def get_run(self, run_id: str) -> ProjectRun | None:
        run = self.runs.get(run_id)
        return run.model_copy(deep=True) if run is not None else None

    def upsert_workflow(self, workflow: WorkflowRun) -> None:
        self.workflows[workflow.workflow_id] = workflow.model_copy(deep=True)

    def get_workflow(self, workflow_id: str) -> WorkflowRun | None:
        workflow = self.workflows.get(workflow_id)
        return workflow.model_copy(deep=True) if workflow is not None else None


def build_header_store(session_factory=None) -> HeaderStore:
    if session_factory is None:
        return InMemoryHeaderStore()

    from app.storage.sql_header_store import SqlHeaderStore

    return SqlHeaderStore(session_factory)
