from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agent_runner.db.session import get_db_session
from agent_runner.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])
project_service = ProjectService()


class CreateProjectRequest(BaseModel):
    project_id: str
    name: str | None = None
    description: str | None = None


@router.post("")
async def create_project(payload: CreateProjectRequest, db: AsyncSession = Depends(get_db_session)):
    try:
        created = await project_service.create_project(db, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "message": "project created",
        **created,
    }


@router.get("/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db_session)):
    project = await project_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    return project
