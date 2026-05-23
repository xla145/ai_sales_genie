from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.runtime_core.llm.base_client import BaseLLMClient
from app.engine.skill_registry import get_skill_definition, list_skill_definitions
from app.engine.task_decomposer import DecompositionContext, build_subtasks, discover_targets
from app.models.project import Project, ProjectStatus
from app.models.run import (
    CreateWorkflowRequest,
    PhaseId,
    RunStatus,
    SubtaskRun,
    WorkflowPhaseState,
    WorkflowRun,
    WorkflowStatus,
)
from app.models.session import ProjectSession
from app.services.hermes_runner import run_subtask
from app.services.project_service import ProjectService
from app.services.session_service import SessionService
from app.services.subagent_pool import SubagentPool
from app.services.workflow_state import WorkflowStateStore
from app.storage.header_paths import session_logs_dir, workflow_detail_path, workflow_log_path
from app.storage.header_store import HeaderStore
from app.storage.logger import ProjectLogger


class MissingWorkflowInputError(Exception):
    pass


class WorkflowService:
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
        self.header_store = header_store
        self.state_store = WorkflowStateStore()
        self.subagent_pool = SubagentPool()
        self.running_tasks: dict[str, object] = {}

    async def create_workflow(self, project_id: str, payload: CreateWorkflowRequest) -> WorkflowRun:
        project, session = self._resolve_project_and_session(project_id, payload.session_id)
        workflow_id = f"wf_{uuid4().hex[:8]}"
        now = datetime.now()
        log_path = workflow_log_path(session, workflow_id)

        merged_config = dict(project.config)
        if payload.prompt is not None:
            merged_config["prompt"] = payload.prompt
        if payload.fail:
            merged_config["fail"] = True
        merged_config["sleep_seconds"] = payload.sleep_seconds
        project.config = merged_config
        project.status = ProjectStatus.RUNNING
        project.current_session_id = session.session_id
        self.project_service.save_project(project)

        workflow = WorkflowRun(
            workflow_id=workflow_id,
            project_id=project.project_id,
            session_id=session.session_id,
            phases=[
                WorkflowPhaseState(
                    phase_id=definition.phase_id,
                    phase_name=definition.phase_name,
                    skill_name=definition.skill_name,
                    input_files=list(definition.input_files),
                    expected_outputs=list(definition.expected_outputs),
                )
                for definition in list_skill_definitions()
            ],
            created_at=now,
            log_path=str(log_path),
            detail_path=str(workflow_detail_path(session, workflow_id)),
        )
        self._save_workflow(session, workflow)
        task_key = f"{project.project_id}:{session.session_id}:{workflow.workflow_id}"
        task = asyncio.create_task(self._execute_workflow(project, session, workflow, payload, task_key))
        self.running_tasks[task_key] = task
        return workflow

    def get_workflow(self, project_id: str, workflow_id: str, session_id: str | None = None) -> WorkflowRun:
        project = self.project_service.get_project(project_id)
        if self.header_store is not None:
            workflow = self.header_store.get_workflow(workflow_id)
            if workflow is None or workflow.project_id != project.project_id:
                raise FileNotFoundError(workflow_id)
            session = self.session_service.resume_session(project, workflow.session_id)
            return self.state_store.get_workflow(session, workflow_id)

        if session_id is not None:
            session = self.session_service.resume_session(project, session_id)
            return self.state_store.get_workflow(session, workflow_id)
        return self.state_store.get_workflow_for_project(project, workflow_id)

    def list_subtasks(self, project_id: str, workflow_id: str, session_id: str | None = None) -> list[SubtaskRun]:
        project = self.project_service.get_project(project_id)
        workflow = self.get_workflow(project_id, workflow_id, session_id=session_id)
        session = self.session_service.resume_session(project, workflow.session_id)
        return self.state_store.list_subtasks(session, workflow_id)

    def has_active_workflows(self, project_id: str) -> bool:
        prefix = f"{project_id}:"
        return any(key.startswith(prefix) for key in self.running_tasks)

    async def _execute_workflow(
        self,
        project: Project,
        session: ProjectSession,
        workflow: WorkflowRun,
        payload: CreateWorkflowRequest,
        task_key: str,
    ) -> None:
        logger = ProjectLogger(Path(workflow.log_path))
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        self._save_workflow(session, workflow)
        try:
            for phase_state in workflow.phases:
                definition = get_skill_definition(phase_state.phase_id)
                self._validate_inputs(session, phase_state.phase_name, phase_state.input_files)
                workflow.current_phase_id = phase_state.phase_id
                phase_state.status = WorkflowStatus.RUNNING
                phase_state.started_at = datetime.now()
                self.state_store.save_workflow(session, workflow)
                if self.header_store is not None:
                    self.header_store.upsert_workflow(workflow)

                prompt = str(project.config.get("prompt") or "请返回一段简短验证文本")
                discovered_targets = discover_targets(definition, prompt)
                subtasks = build_subtasks(
                    definition,
                    DecompositionContext(
                        workflow_id=workflow.workflow_id,
                        project_id=project.project_id,
                        session_id=session.session_id,
                        prompt=prompt,
                        max_parallel_subagents=payload.max_parallel_subagents,
                        discovered_targets=discovered_targets,
                        log_dir=str(session_logs_dir(session)),
                    ),
                )
                phase_state.subtask_ids = [subtask.subtask_id for subtask in subtasks]
                for subtask in subtasks:
                    self.state_store.save_subtask(session, workflow.workflow_id, subtask)

                async def _worker(current_subtask):
                    result = await run_subtask(
                        project=project,
                        session=session,
                        subtask=current_subtask,
                        logger=ProjectLogger(Path(current_subtask.log_path)),
                        session_service=self.session_service,
                        llm_client=self.llm_client,
                        base_dir=self.base_dir,
                        skill_definition=definition,
                    )
                    self.state_store.save_subtask(session, workflow.workflow_id, current_subtask)
                    return result

                parallel_subtasks, serial_subtasks = self._split_parallel_and_serial_subtasks(definition, subtasks)
                finished_subtasks: list[SubtaskRun] = []
                if parallel_subtasks:
                    finished_subtasks.extend(
                        await self.subagent_pool.run(
                            parallel_subtasks,
                            payload.max_parallel_subagents if definition.supports_parallelism else 1,
                            _worker,
                        )
                    )
                for serial_subtask in serial_subtasks:
                    await _worker(serial_subtask)
                    finished_subtasks.append(serial_subtask)
                for subtask in finished_subtasks:
                    self.state_store.save_subtask(session, workflow.workflow_id, subtask)

                failed = [item for item in finished_subtasks if item.status == RunStatus.FAILED]
                if failed:
                    phase_state.status = WorkflowStatus.FAILED
                    phase_state.error_message = "; ".join(item.error_message or item.subtask_id for item in failed)
                    raise RuntimeError(phase_state.error_message)

                self._validate_outputs(session, phase_state.phase_name, phase_state.expected_outputs)
                phase_state.status = WorkflowStatus.SUCCESS
                phase_state.ended_at = datetime.now()
                phase_state.result_summary = {
                    "subtasks": [item.result_summary for item in finished_subtasks],
                    "input_tokens": sum(item.input_tokens for item in finished_subtasks),
                    "output_tokens": sum(item.output_tokens for item in finished_subtasks),
                }
                phase_state.input_tokens = sum(item.input_tokens for item in finished_subtasks)
                phase_state.output_tokens = sum(item.output_tokens for item in finished_subtasks)
                self.state_store.save_workflow(session, workflow)
                if self.header_store is not None:
                    self.header_store.upsert_workflow(workflow)

            workflow.status = WorkflowStatus.SUCCESS
            workflow.result_summary = {
                "completed_phases": [phase.phase_id.value for phase in workflow.phases],
            }
            project.status = ProjectStatus.SUCCESS
        except MissingWorkflowInputError as exc:
            workflow.status = WorkflowStatus.BLOCKED
            workflow.error_message = str(exc)
            project.status = ProjectStatus.FAILED
            logger.error(str(exc))
        except Exception as exc:
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = str(exc)
            project.status = ProjectStatus.FAILED
            logger.error(f"Workflow failed: {exc}")
        finally:
            workflow.ended_at = datetime.now()
            self.state_store.save_workflow(session, workflow)
            if self.header_store is not None:
                self.header_store.upsert_workflow(workflow)
            self.project_service.save_project(project)
            self.running_tasks.pop(task_key, None)

    def _save_workflow(self, session: ProjectSession, workflow: WorkflowRun) -> None:
        self.state_store.save_workflow(session, workflow)
        if self.header_store is not None:
            self.header_store.upsert_workflow(workflow)

    def _resolve_project_and_session(
        self,
        project_id: str,
        session_id: str | None,
    ) -> tuple[Project, ProjectSession]:
        project = self.project_service.get_project(project_id)
        if session_id:
            session = self.session_service.resume_session(project, session_id)
        else:
            session = self.session_service.get_or_create_default_session(project)
            if project.current_session_id != session.session_id:
                project.current_session_id = session.session_id
                self.project_service.save_project(project)
        return project, session

    def _validate_inputs(self, session: ProjectSession, phase_name: str, input_files: list[str]) -> None:
        workspace_dir = Path(session.workspace_path)
        missing_files = [relative_path for relative_path in input_files if not (workspace_dir / relative_path).exists()]
        if missing_files:
            missing = ", ".join(missing_files)
            raise MissingWorkflowInputError(f"{phase_name} 缺少依赖输入: {missing}")

    def _validate_outputs(self, session: ProjectSession, phase_name: str, expected_outputs: list[str]) -> None:
        workspace_dir = Path(session.workspace_path)
        missing_outputs = [relative_path for relative_path in expected_outputs if not (workspace_dir / relative_path).exists()]
        if missing_outputs:
            missing = ", ".join(missing_outputs)
            raise RuntimeError(f"{phase_name} 未生成预期产物: {missing}")

    def _split_parallel_and_serial_subtasks(
        self,
        definition,
        subtasks: list[SubtaskRun],
    ) -> tuple[list[SubtaskRun], list[SubtaskRun]]:
        if definition.phase_id != PhaseId.PHASE3:
            return subtasks, []
        parallel = [item for item in subtasks if not item.subtask_id.endswith("_finalize")]
        serial = [item for item in subtasks if item.subtask_id.endswith("_finalize")]
        return parallel, serial
