from __future__ import annotations

from pathlib import Path

from app.models.project import Project
from app.models.run import SubtaskRun, WorkflowRun
from app.models.session import ProjectSession
from app.storage.file_store import FileStore
from app.storage.header_paths import (
    project_sessions_dir,
    session_file_for_project,
    session_workflows_dir,
    workflow_detail_path,
    workflow_subtasks_dir,
)


class WorkflowStateStore:
    def __init__(self) -> None:
        self.store = FileStore()

    def save_workflow(self, session: ProjectSession, workflow: WorkflowRun) -> None:
        workflow.session_snapshot = session.snapshot()
        self.store.write_json(self._workflow_path(session, workflow.workflow_id), workflow.model_dump(mode="json"))

    def get_workflow(self, session: ProjectSession, workflow_id: str) -> WorkflowRun:
        data = self.store.read_json(self._workflow_path(session, workflow_id))
        if not data:
            raise FileNotFoundError(workflow_id)
        return WorkflowRun.model_validate(data)

    def list_workflows(self, session: ProjectSession) -> list[WorkflowRun]:
        workflows_dir = session_workflows_dir(session)
        workflows: list[WorkflowRun] = []
        for workflow_file in sorted(workflows_dir.glob("*.json")):
            data = self.store.read_json(workflow_file)
            if data:
                workflows.append(WorkflowRun.model_validate(data))
        return workflows

    def save_subtask(self, session: ProjectSession, workflow_id: str, subtask: SubtaskRun) -> None:
        self.store.write_json(self._subtask_path(session, workflow_id, subtask.subtask_id), subtask.model_dump(mode="json"))

    def list_subtasks(self, session: ProjectSession, workflow_id: str) -> list[SubtaskRun]:
        subtasks_dir = self._subtasks_dir(session, workflow_id)
        subtasks: list[SubtaskRun] = []
        for subtask_file in sorted(subtasks_dir.glob("*.json")):
            data = self.store.read_json(subtask_file)
            if data:
                subtasks.append(SubtaskRun.model_validate(data))
        return subtasks

    def get_workflow_for_project(self, project: Project, workflow_id: str, session: ProjectSession | None = None) -> WorkflowRun:
        if session is not None:
            return self.get_workflow(session, workflow_id)
        sessions_dir = project_sessions_dir(project)
        for session_dir in sorted(sessions_dir.glob("sess_*")):
            session_file = session_file_for_project(project, session_dir.name)
            data = self.store.read_json(session_file)
            if not data:
                continue
            project_session = ProjectSession.model_validate(data)
            try:
                return self.get_workflow(project_session, workflow_id)
            except FileNotFoundError:
                continue
        raise FileNotFoundError(workflow_id)

    def _workflow_path(self, session: ProjectSession, workflow_id: str) -> Path:
        return workflow_detail_path(session, workflow_id)

    def _subtasks_dir(self, session: ProjectSession, workflow_id: str) -> Path:
        return workflow_subtasks_dir(session, workflow_id)

    def _subtask_path(self, session: ProjectSession, workflow_id: str, subtask_id: str) -> Path:
        return self._subtasks_dir(session, workflow_id) / f"{subtask_id}.json"
