from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session, sessionmaker

from app.models.project import Project, ProjectStatus
from app.models.run import PhaseId, ProjectRun, RunStatus, WorkflowRun, WorkflowStatus
from app.models.session import ProjectSession, SessionStatus
from app.storage.db import session_scope
from app.storage.db_models import ProjectRecord, ProjectRunRecord, ProjectSessionRecord, WorkflowRecord
from app.storage.header_store import HeaderStore


@dataclass
class SqlHeaderStore(HeaderStore):
    session_factory: sessionmaker[Session]

    def upsert_project(self, project: Project) -> None:
        with session_scope(self.session_factory) as session:
            record = session.get(ProjectRecord, project.project_id) or ProjectRecord(project_id=project.project_id)
            record.name = project.name
            record.description = project.description
            record.status = project.status.value
            record.workspace_path = project.workspace_path
            record.current_session_id = project.current_session_id
            record.created_at = project.created_at
            record.updated_at = project.updated_at
            session.add(record)

    def get_project(self, project_id: str) -> Project | None:
        with session_scope(self.session_factory) as session:
            record = session.get(ProjectRecord, project_id)
            if record is None:
                return None
            return Project(
                project_id=record.project_id,
                name=record.name,
                description=record.description,
                status=ProjectStatus(record.status),
                workspace_path=record.workspace_path,
                current_session_id=record.current_session_id,
                config={},
                created_at=record.created_at,
                updated_at=record.updated_at,
            )

    def list_projects(self) -> list[Project]:
        with session_scope(self.session_factory) as session:
            records = session.query(ProjectRecord).order_by(ProjectRecord.created_at).all()
            return [
                Project(
                    project_id=record.project_id,
                    name=record.name,
                    description=record.description,
                    status=ProjectStatus(record.status),
                    workspace_path=record.workspace_path,
                    current_session_id=record.current_session_id,
                    config={},
                    created_at=record.created_at,
                    updated_at=record.updated_at,
                )
                for record in records
            ]

    def delete_project(self, project_id: str) -> None:
        with session_scope(self.session_factory) as session:
            record = session.get(ProjectRecord, project_id)
            if record is not None:
                session.delete(record)

    def upsert_session(self, project_session: ProjectSession) -> None:
        with session_scope(self.session_factory) as session:
            record = session.get(ProjectSessionRecord, project_session.session_id) or ProjectSessionRecord(session_id=project_session.session_id)
            record.project_id = project_session.project_id
            record.workspace_path = project_session.workspace_path
            record.conversation = project_session.conversation
            record.base_url = project_session.base_url
            record.llm_provider = project_session.llm_provider
            record.provider_session_ref = project_session.provider_session_ref
            record.status = project_session.status.value
            record.hermes_session_ref = project_session.hermes_session_ref
            record.created_at = project_session.created_at
            record.updated_at = project_session.updated_at
            session.add(record)

    def list_sessions(self, project_id: str) -> list[ProjectSession]:
        with session_scope(self.session_factory) as session:
            records = session.query(ProjectSessionRecord).filter(ProjectSessionRecord.project_id == project_id).order_by(ProjectSessionRecord.created_at).all()
            return [self._session_from_record(record) for record in records]

    def get_session(self, session_id: str) -> ProjectSession | None:
        with session_scope(self.session_factory) as session:
            record = session.get(ProjectSessionRecord, session_id)
            return self._session_from_record(record) if record is not None else None

    def upsert_run(self, run: ProjectRun) -> None:
        with session_scope(self.session_factory) as session:
            record = session.get(ProjectRunRecord, run.run_id) or ProjectRunRecord(run_id=run.run_id)
            record.project_id = run.project_id
            record.session_id = run.session_id
            record.phase_id = run.phase_id.value
            record.phase_name = run.phase_name
            record.skill_name = run.skill_name
            record.status = run.status.value
            record.started_at = run.started_at
            record.ended_at = run.ended_at
            record.error_message = run.error_message
            record.log_path = run.log_path
            record.output_path = run.output_path
            record.result_summary_path = run.result_summary_path
            record.detail_path = run.detail_path
            session.add(record)

    def list_runs(self, project_id: str, session_id: str | None = None) -> list[ProjectRun]:
        with session_scope(self.session_factory) as session:
            query = session.query(ProjectRunRecord).filter(ProjectRunRecord.project_id == project_id)
            if session_id is not None:
                query = query.filter(ProjectRunRecord.session_id == session_id)
            records = query.order_by(ProjectRunRecord.started_at).all()
            return [self._run_from_record(record) for record in records]

    def get_run(self, run_id: str) -> ProjectRun | None:
        with session_scope(self.session_factory) as session:
            record = session.get(ProjectRunRecord, run_id)
            return self._run_from_record(record) if record is not None else None

    def upsert_workflow(self, workflow: WorkflowRun) -> None:
        with session_scope(self.session_factory) as session:
            record = session.get(WorkflowRecord, workflow.workflow_id) or WorkflowRecord(workflow_id=workflow.workflow_id)
            record.project_id = workflow.project_id
            record.session_id = workflow.session_id
            record.status = workflow.status.value
            record.current_phase_id = workflow.current_phase_id.value if workflow.current_phase_id is not None else None
            record.created_at = workflow.created_at
            record.started_at = workflow.started_at
            record.ended_at = workflow.ended_at
            record.error_message = workflow.error_message
            record.log_path = workflow.log_path
            record.detail_path = workflow.detail_path
            session.add(record)

    def get_workflow(self, workflow_id: str) -> WorkflowRun | None:
        with session_scope(self.session_factory) as session:
            record = session.get(WorkflowRecord, workflow_id)
            if record is None:
                return None
            return WorkflowRun(
                workflow_id=record.workflow_id,
                project_id=record.project_id,
                session_id=record.session_id,
                status=WorkflowStatus(record.status),
                current_phase_id=PhaseId(record.current_phase_id) if record.current_phase_id else None,
                created_at=record.created_at,
                started_at=record.started_at,
                ended_at=record.ended_at,
                error_message=record.error_message,
                log_path=record.log_path,
                detail_path=record.detail_path,
            )

    def _session_from_record(self, record: ProjectSessionRecord) -> ProjectSession:
        return ProjectSession(
            session_id=record.session_id,
            project_id=record.project_id,
            workspace_path=record.workspace_path,
            conversation=record.conversation,
            base_url=record.base_url,
            llm_provider=record.llm_provider,
            provider_session_ref=record.provider_session_ref,
            status=SessionStatus(record.status),
            hermes_session_ref=record.hermes_session_ref,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def _run_from_record(self, record: ProjectRunRecord) -> ProjectRun:
        return ProjectRun(
            run_id=record.run_id,
            project_id=record.project_id,
            session_id=record.session_id,
            phase_id=PhaseId(record.phase_id),
            phase_name=record.phase_name,
            skill_name=record.skill_name,
            status=RunStatus(record.status),
            started_at=record.started_at,
            ended_at=record.ended_at,
            error_message=record.error_message,
            log_path=record.log_path,
            output_path=record.output_path,
            result_summary_path=record.result_summary_path,
            detail_path=record.detail_path,
        )
