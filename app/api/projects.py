from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from pydantic import BaseModel

from app.api.auth import CurrentUserDep
from app.api.deps import get_project_service, get_run_service, get_session_service, get_workflow_service
from app.models.project import (
    CreateProjectRequest,
    Project,
    RequirementAttachmentItem,
    RunPhase1Request,
    RunPhase1Response,
    UpdateProjectOverviewRequest,
    UpdateProjectRequest,
    UpdateRequirementAnalysisRequest,
)
from app.models.run import CreateRunRequest, PhaseId, ProjectRun
from app.models.session import ProjectSession
from app.services.orchestrator_service import WorkflowService
from app.services.project_service import ProjectService
from app.services.run_service import MissingRunInputError, RunService
from app.services.session_service import SessionService
from app.tools.tool_registry import ToolRegistry
from app.tools.workspace_tools import build_workspace_tools


class ToolInfoResponse(BaseModel):
    name: str
    description: str
    parameters: dict


class LogsResponse(BaseModel):
    content: str


class SessionInfoResponse(BaseModel):
    session_id: str
    project_id: str
    conversation: str
    base_url: str | None = None
    workspace_path: str
    hermes_session_ref: str | None = None
    status: str


router = APIRouter(prefix="/projects", tags=["projects"])

ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
RunServiceDep = Annotated[RunService, Depends(get_run_service)]
SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
WorkflowServiceDep = Annotated[WorkflowService, Depends(get_workflow_service)]


@router.post("", response_model=Project)
def create_project(
    payload: CreateProjectRequest,
    project_service: ProjectServiceDep,
    session_service: SessionServiceDep,
    _current_user: CurrentUserDep,
) -> Project:
    project = project_service.create_project(payload, _current_user.user_id)
    session = session_service.create_session(project)
    project.current_session_id = session.session_id
    project_service.save_project(project, user_id=_current_user.user_id)
    return project


@router.get("", response_model=list[Project])
def list_projects(project_service: ProjectServiceDep, _current_user: CurrentUserDep) -> list[Project]:
    return project_service.list_projects_for_user(_current_user.user_id)


@router.get("/{project_id}", response_model=Project)
def get_project(project_id: str, project_service: ProjectServiceDep, _current_user: CurrentUserDep) -> Project:
    try:
        return project_service.get_project_for_user(project_id, _current_user.user_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None


@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: str,
    payload: UpdateProjectRequest,
    project_service: ProjectServiceDep,
    _current_user: CurrentUserDep,
) -> Project:
    try:
        return project_service.update_project(project_id, payload, _current_user.user_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None


@router.patch("/{project_id}/overview", response_model=Project)
def update_project_overview(
    project_id: str,
    payload: UpdateProjectOverviewRequest,
    project_service: ProjectServiceDep,
    _current_user: CurrentUserDep,
) -> Project:
    try:
        return project_service.update_project_overview(project_id, payload, _current_user.user_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None


@router.patch("/{project_id}/requirement-analysis", response_model=Project)
def update_requirement_analysis(
    project_id: str,
    payload: UpdateRequirementAnalysisRequest,
    project_service: ProjectServiceDep,
    _current_user: CurrentUserDep,
) -> Project:
    try:
        return project_service.update_requirement_analysis(project_id, payload, _current_user.user_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None


@router.get("/{project_id}/requirement-uploads", response_model=list[RequirementAttachmentItem])
def list_requirement_uploads(
    project_id: str,
    project_service: ProjectServiceDep,
    _current_user: CurrentUserDep,
) -> list[dict]:
    try:
        return project_service.list_requirement_uploads(project_id, _current_user.user_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None


@router.post("/{project_id}/requirement-uploads", response_model=RequirementAttachmentItem)
async def upload_requirement_file(
    project_id: str,
    project_service: ProjectServiceDep,
    _current_user: CurrentUserDep,
    file: UploadFile = File(...),
) -> dict:
    try:
        return project_service.upload_requirement_file(
            project_id,
            _current_user.user_id,
            filename=file.filename or "upload",
            content_type=file.content_type,
            file_obj=file.file,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None
    except ValueError as exc:
        code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE if "too large" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    finally:
        await file.close()


@router.delete("/{project_id}/requirement-uploads/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_requirement_upload(
    project_id: str,
    upload_id: str,
    project_service: ProjectServiceDep,
    _current_user: CurrentUserDep,
) -> Response:
    try:
        project_service.delete_requirement_upload(project_id, _current_user.user_id, upload_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Upload not found") from None


@router.post("/{project_id}/phase1/run", response_model=RunPhase1Response)
async def run_phase1(
    project_id: str,
    payload: RunPhase1Request,
    run_service: RunServiceDep,
    project_service: ProjectServiceDep,
    session_service: SessionServiceDep,
    _current_user: CurrentUserDep,
) -> RunPhase1Response:
    try:
        project = project_service.get_project_for_user(project_id, _current_user.user_id)
        session_id = payload.session_id
        if not session_id:
            if project.current_session_id:
                session_id = project.current_session_id
            else:
                session = session_service.create_session(project)
                project.current_session_id = session.session_id
                project_service.save_project(project, user_id=_current_user.user_id)
                session_id = session.session_id
        run = await run_service.create_run(
            project_id,
            _current_user.user_id,
            CreateRunRequest(
                session_id=session_id,
                phase_id=PhaseId.PHASE1,
                phase_name="需求录入与结构化",
                skill_name="requirement-intake-structuring",
                prompt=payload.prompt,
                input_files=[],
                expected_outputs=["需求结构化.md"],
            ),
        )
        final_run = await run_service.wait_for_run(project_id, _current_user.user_id, run.run_id, run.session_id)
        project = project_service.sync_requirement_analysis_from_phase1(project_id, _current_user.user_id)
        return RunPhase1Response(
            project=project,
            run_id=final_run.run_id,
            session_id=final_run.session_id,
            status=final_run.status.value,
            result_summary=final_run.result_summary,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None
    except MissingRunInputError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{project_id}/sessions", response_model=ProjectSession)
def create_session(
    project_id: str,
    project_service: ProjectServiceDep,
    session_service: SessionServiceDep,
    _current_user: CurrentUserDep,
) -> ProjectSession:
    try:
        project = project_service.get_project_for_user(project_id, _current_user.user_id)
        session = session_service.create_session(project)
        project.current_session_id = session.session_id
        project_service.save_project(project, user_id=_current_user.user_id)
        return session
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None


@router.get("/{project_id}/sessions", response_model=list[ProjectSession])
def list_sessions(
    project_id: str,
    project_service: ProjectServiceDep,
    session_service: SessionServiceDep,
    _current_user: CurrentUserDep,
) -> list[ProjectSession]:
    try:
        project = project_service.get_project_for_user(project_id, _current_user.user_id)
        return session_service.list_sessions(project)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None


@router.get("/{project_id}/sessions/{session_id}", response_model=ProjectSession)
def get_session(
    project_id: str,
    session_id: str,
    project_service: ProjectServiceDep,
    session_service: SessionServiceDep,
    _current_user: CurrentUserDep,
) -> ProjectSession:
    try:
        project = project_service.get_project_for_user(project_id, _current_user.user_id)
        return session_service.get_session(project, session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found") from None


@router.get("/{project_id}/sessions/{session_id}/info", response_model=SessionInfoResponse)
def get_session_info(
    project_id: str,
    session_id: str,
    project_service: ProjectServiceDep,
    session_service: SessionServiceDep,
    _current_user: CurrentUserDep,
) -> SessionInfoResponse:
    try:
        project = project_service.get_project_for_user(project_id, _current_user.user_id)
        session = session_service.get_session(project, session_id)
        return SessionInfoResponse(
            session_id=session.session_id,
            project_id=session.project_id,
            conversation=session.conversation,
            base_url=session.base_url,
            workspace_path=session.workspace_path,
            hermes_session_ref=session.hermes_session_ref,
            status=session.status.value,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found") from None


@router.post("/{project_id}/sessions/{session_id}/resume", response_model=ProjectSession)
def resume_session(
    project_id: str,
    session_id: str,
    project_service: ProjectServiceDep,
    session_service: SessionServiceDep,
    _current_user: CurrentUserDep,
) -> ProjectSession:
    try:
        project = project_service.get_project_for_user(project_id, _current_user.user_id)
        session = session_service.resume_session(project, session_id)
        project.current_session_id = session.session_id
        project_service.save_project(project, user_id=_current_user.user_id)
        return session
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found") from None


@router.post("/{project_id}/sessions/{session_id}/runs", response_model=ProjectRun)
async def create_session_run(
    project_id: str,
    session_id: str,
    payload: CreateRunRequest,
    run_service: RunServiceDep,
    _current_user: CurrentUserDep,
) -> ProjectRun:
    try:
        payload.session_id = session_id
        return await run_service.create_run(project_id, _current_user.user_id, payload)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    except MissingRunInputError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{project_id}/runs", response_model=ProjectRun)
async def create_run(
    project_id: str,
    payload: CreateRunRequest,
    run_service: RunServiceDep,
    _current_user: CurrentUserDep,
) -> ProjectRun:
    try:
        return await run_service.create_run(project_id, _current_user.user_id, payload)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None
    except MissingRunInputError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/tools", response_model=list[ToolInfoResponse])
def list_tools() -> list[ToolInfoResponse]:
    registry = ToolRegistry()
    for tool in build_workspace_tools(Path(".")):
        registry.register(tool)
    return [
        ToolInfoResponse(name=tool.name, description=tool.description, parameters=tool.parameters_schema)
        for tool in registry.list_tools()
    ]


@router.get("/{project_id}/runs", response_model=list[ProjectRun])
def list_runs(
    project_id: str,
    run_service: RunServiceDep,
    _current_user: CurrentUserDep,
    session_id: str | None = None,
) -> list[ProjectRun]:
    try:
        return run_service.list_runs(project_id, _current_user.user_id, session_id=session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None


@router.get("/{project_id}/runs/{run_id}", response_model=ProjectRun)
def get_run(
    project_id: str,
    run_id: str,
    run_service: RunServiceDep,
    _current_user: CurrentUserDep,
    session_id: str | None = None,
) -> ProjectRun:
    try:
        return run_service.get_run(project_id, _current_user.user_id, run_id, session_id=session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Run not found") from None


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    project_service: ProjectServiceDep,
    run_service: RunServiceDep,
    workflow_service: WorkflowServiceDep,
    _current_user: CurrentUserDep,
) -> Response:
    try:
        if run_service.has_active_runs(project_id):
            raise HTTPException(status_code=409, detail="Project has active runs")
        if workflow_service.has_active_workflows(project_id):
            raise HTTPException(status_code=409, detail="Project has active workflows")
        project_service.delete_project(project_id, _current_user.user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found") from None


@router.get("/{project_id}/runs/{run_id}/logs", response_model=LogsResponse)
def get_logs(
    project_id: str,
    run_id: str,
    run_service: RunServiceDep,
    _current_user: CurrentUserDep,
    session_id: str | None = None,
) -> LogsResponse:
    try:
        return LogsResponse(content=run_service.read_logs(project_id, _current_user.user_id, run_id, session_id=session_id))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Run not found") from None
