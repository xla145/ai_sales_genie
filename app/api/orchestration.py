from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_workflow_service
from app.models.run import CreateWorkflowRequest, SubtaskRun, WorkflowRun
from app.services.orchestrator_service import MissingWorkflowInputError, WorkflowService


router = APIRouter(prefix="/projects", tags=["workflows"])

WorkflowServiceDep = Annotated[WorkflowService, Depends(get_workflow_service)]


@router.post("/{project_id}/workflows", response_model=WorkflowRun)
async def create_workflow(
    project_id: str,
    payload: CreateWorkflowRequest,
    workflow_service: WorkflowServiceDep,
) -> WorkflowRun:
    try:
        return await workflow_service.create_workflow(project_id, payload)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project or session not found") from None
    except MissingWorkflowInputError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{project_id}/workflows/{workflow_id}", response_model=WorkflowRun)
def get_workflow(
    project_id: str,
    workflow_id: str,
    session_id: str | None = None,
    workflow_service: WorkflowServiceDep = Depends(get_workflow_service),
) -> WorkflowRun:
    try:
        return workflow_service.get_workflow(project_id, workflow_id, session_id=session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found") from None


@router.get("/{project_id}/workflows/{workflow_id}/tasks", response_model=list[SubtaskRun])
def list_workflow_subtasks(
    project_id: str,
    workflow_id: str,
    session_id: str | None = None,
    workflow_service: WorkflowServiceDep = Depends(get_workflow_service),
) -> list[SubtaskRun]:
    try:
        return workflow_service.list_subtasks(project_id, workflow_id, session_id=session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found") from None
