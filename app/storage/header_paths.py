from __future__ import annotations

from pathlib import Path

from app.models.project import Project
from app.models.session import ProjectSession


def project_file_path(project: Project) -> Path:
    return Path(project.workspace_path) / "project.json"


def project_config_path(project: Project) -> Path:
    return Path(project.workspace_path) / "config.json"


def project_sessions_dir(project: Project) -> Path:
    return Path(project.workspace_path) / "sessions"


def session_dir_path(project: Project, session_id: str) -> Path:
    return project_sessions_dir(project) / session_id


def session_file_for_project(project: Project, session_id: str) -> Path:
    return session_dir_path(project, session_id) / "session.json"


def session_file_path(session: ProjectSession) -> Path:
    return Path(session.workspace_path) / "session.json"


def session_runs_dir(session: ProjectSession) -> Path:
    return Path(session.workspace_path) / "runs"


def session_outputs_dir(session: ProjectSession) -> Path:
    return Path(session.workspace_path) / "outputs"


def session_workflows_dir(session: ProjectSession) -> Path:
    return Path(session.workspace_path) / "workflows"


def workflow_subtasks_dir(session: ProjectSession, workflow_id: str) -> Path:
    return session_workflows_dir(session) / workflow_id / "subtasks"


def run_output_path(session: ProjectSession, run_id: str) -> Path:
    return session_outputs_dir(session) / f"{run_id}.txt"


def run_log_path(session: ProjectSession, run_id: str) -> Path:
    return session_logs_dir(session) / f"{run_id}.log"


def run_detail_path(session: ProjectSession, run_id: str) -> Path:
    return session_runs_dir(session) / f"{run_id}.json"


def session_logs_dir(session: ProjectSession) -> Path:
    return Path(session.workspace_path) / "logs"


def workflow_log_path(session: ProjectSession, workflow_id: str) -> Path:
    return session_logs_dir(session) / f"{workflow_id}.log"


def workflow_detail_path(session: ProjectSession, workflow_id: str) -> Path:
    return session_workflows_dir(session) / f"{workflow_id}.json"
