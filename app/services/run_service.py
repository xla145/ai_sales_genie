from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.runtime_core.llm.base_client import BaseLLMClient
from app.models.project import Project, ProjectStatus
from app.models.run import CreateRunRequest, ProjectRun, RunStatus
from app.models.session import ProjectSession
from app.engine.skill_registry import get_skill_definition
from app.services.hermes_runner import run_project
from app.services.project_service import ProjectService
from app.services.session_service import SessionService
from app.storage.file_store import FileStore
from app.storage.header_paths import (
    run_detail_path,
    run_log_path,
    run_output_path,
    session_runs_dir,
)
from app.storage.header_store import HeaderStore
from app.storage.logger import ProjectLogger


class MissingRunInputError(Exception):
    pass


class RunService:
    def __init__(
        self,
        base_dir: Path,
        project_service: ProjectService,
        session_service: SessionService,
        llm_client: BaseLLMClient,
        header_store: HeaderStore | None = None,
    ) -> None:
        self.base_dir = base_dir
        self.project_service = project_service
        self.session_service = session_service
        self.llm_client = llm_client
        self.store = FileStore()
        self.header_store = header_store
        self.running_tasks: dict[str, asyncio.Task] = {}

    def list_runs(self, project_id: str, user_id: str, session_id: str | None = None) -> list[ProjectRun]:
        project, session = self._resolve_project_and_session(project_id, user_id, session_id)
        if self.header_store is not None:
            runs = self.header_store.list_runs(project_id, session_id)
            hydrated: list[ProjectRun] = []
            for run in runs:
                run_session = session if session_id is not None and session.session_id == run.session_id else self.session_service.get_session(project, run.session_id)
                hydrated.append(self._hydrate_run_details(run, run_session))
            return hydrated

        runs_dir = session_runs_dir(session)
        runs: list[ProjectRun] = []
        for run_file in sorted(runs_dir.glob("*.json")):
            data = self.store.read_json(run_file)
            if data:
                runs.append(ProjectRun.model_validate(data))
        return runs

    def get_run(self, project_id: str, user_id: str, run_id: str, session_id: str | None = None) -> ProjectRun:
        project = self.project_service.get_project_for_user(project_id, user_id)
        if self.header_store is not None:
            stored = self.header_store.get_run(run_id)
            if stored is None or stored.project_id != project.project_id:
                raise FileNotFoundError(run_id)
            session = self.session_service.get_session(project, stored.session_id)
            return self._hydrate_run_details(stored, session)

        if session_id:
            session = self.session_service.get_session(project, session_id)
            return self._read_run_from_session(session, run_id)

        for session in self.session_service.list_sessions(project):
            run = self._read_run_from_session(session, run_id, raise_if_missing=False)
            if run is not None:
                return run
        raise FileNotFoundError(run_id)

    def read_logs(self, project_id: str, user_id: str, run_id: str, session_id: str | None = None) -> str:
        run = self.get_run(project_id, user_id, run_id, session_id=session_id)
        log_path = Path(run.log_path)
        if not log_path.exists():
            return ""
        return log_path.read_text(encoding="utf-8")

    async def create_run(self, project_id: str, user_id: str, payload: CreateRunRequest) -> ProjectRun:
        project, session = self._resolve_project_and_session(project_id, user_id, payload.session_id)
        self._validate_input_files(session, payload.input_files, payload.phase_name)
        run_id = f"run_{uuid4().hex[:8]}"
        now = datetime.now()
        log_path = run_log_path(session, run_id)

        merged_config = dict(project.config)
        if payload.prompt is not None:
            merged_config["prompt"] = payload.prompt
        if payload.fail:
            merged_config["fail"] = True
        merged_config["sleep_seconds"] = payload.sleep_seconds
        project.config = merged_config
        project.status = ProjectStatus.RUNNING
        project.current_session_id = session.session_id
        self.project_service.save_project(project, user_id=user_id)

        run = ProjectRun(
            run_id=run_id,
            project_id=project_id,
            session_id=session.session_id,
            created_id=project.created_id,
            update_id=project.update_id,
            phase_id=payload.phase_id,
            phase_name=payload.phase_name,
            skill_name=payload.skill_name,
            input_files=payload.input_files,
            expected_outputs=payload.expected_outputs,
            status=RunStatus.PENDING,
            started_at=now,
            log_path=str(log_path),
            output_path=str(run_output_path(session, run_id)),
            detail_path=str(run_detail_path(session, run_id)),
        )
        self._save_run(session, run)
        task_key = f"{project_id}:{session.session_id}:{run_id}"
        self.running_tasks[task_key] = asyncio.create_task(self._execute_run(project, session, run, task_key))
        return run

    async def _execute_run(
        self,
        project: Project,
        session: ProjectSession,
        run: ProjectRun,
        task_key: str,
    ) -> None:
        logger = ProjectLogger(Path(run.log_path))
        run.status = RunStatus.RUNNING
        self._save_run(session, run)
        try:
            skill_definition = get_skill_definition(run.phase_id)
            result = await run_project(
                project,
                session,
                run,
                logger,
                self.session_service,
                self.llm_client,
                self.base_dir,
                skill_definition,
            )
            run.status = RunStatus.SUCCESS
            run.result_summary = result
            project.status = ProjectStatus.SUCCESS
        except Exception as exc:
            run.status = RunStatus.FAILED
            run.error_message = str(exc)
            project.status = ProjectStatus.FAILED
            logger.error(f"Run failed: {exc}")
        finally:
            run.ended_at = datetime.now()
            run.result_summary_path = str(run_output_path(session, run.run_id))
            run.update_id = project.update_id
            self._save_run(session, run)
            self.project_service.save_project(project, user_id=project.update_id)
            self.running_tasks.pop(task_key, None)

    async def wait_for_run(self, project_id: str, user_id: str, run_id: str, session_id: str, *, poll_interval: float = 0.1) -> ProjectRun:
        while True:
            run = self.get_run(project_id, user_id, run_id, session_id=session_id)
            if run.status in {RunStatus.SUCCESS, RunStatus.FAILED}:
                if run.status == RunStatus.FAILED:
                    raise RuntimeError(run.error_message or 'Run failed')
                return run
            await asyncio.sleep(poll_interval)

    def has_active_runs(self, project_id: str) -> bool:
        prefix = f"{project_id}:"
        return any(key.startswith(prefix) for key in self.running_tasks)

    def _resolve_project_and_session(
        self,
        project_id: str,
        user_id: str,
        session_id: str | None,
    ) -> tuple[Project, ProjectSession]:
        project = self.project_service.get_project_for_user(project_id, user_id)
        if session_id:
            session = self.session_service.resume_session(project, session_id)
        else:
            session = self.session_service.get_or_create_default_session(project)
            if project.current_session_id != session.session_id:
                project.current_session_id = session.session_id
                self.project_service.save_project(project, user_id=user_id)
        return project, session

    def _save_run(self, session: ProjectSession, run: ProjectRun) -> None:
        self.store.write_json(
            run_detail_path(session, run.run_id),
            run.model_dump(mode="json"),
        )
        if self.header_store is not None:
            self.header_store.upsert_run(run)

    def _validate_input_files(self, session: ProjectSession, input_files: list[str], phase_name: str) -> None:
        workspace_dir = Path(session.workspace_path)
        missing_files: list[str] = []
        for relative_path in input_files:
            candidate = workspace_dir / relative_path
            if not candidate.exists():
                missing_files.append(relative_path)
        if missing_files:
            missing = ", ".join(missing_files)
            raise MissingRunInputError(f"{phase_name} 缺少依赖输入: {missing}")

    def _read_run_from_session(
        self,
        session: ProjectSession,
        run_id: str,
        *,
        raise_if_missing: bool = True,
    ) -> ProjectRun | None:
        run_path = run_detail_path(session, run_id)
        data = self.store.read_json(run_path)
        if not data:
            if raise_if_missing:
                raise FileNotFoundError(run_id)
            return None
        return ProjectRun.model_validate(data)

    def _hydrate_run_details(self, run: ProjectRun, session: ProjectSession) -> ProjectRun:
        detail_path = Path(run.detail_path or run_detail_path(session, run.run_id))
        data = self.store.read_json(detail_path)
        if data:
            return ProjectRun.model_validate(data)
        return run
