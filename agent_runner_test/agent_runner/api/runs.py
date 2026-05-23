from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agent_runner.db.session import get_db_session
from agent_runner.services.event_service import EventService
from agent_runner.services.run_service import RunService
from agent_runner.worker.runner import Runner

router = APIRouter(prefix="/runs", tags=["runs"])
run_service = RunService()
event_service = EventService()
runner = Runner()


class CreateRunRequest(BaseModel):
    run_id: str
    project_id: str
    session_id: str
    run_type: str
    user_message: str | None = None


@router.post("")
async def create_run(payload: CreateRunRequest, db: AsyncSession = Depends(get_db_session)):
    try:
        run = await run_service.create_run(db, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    await event_service.emit(
        db,
        {
            "project_id": run["project_id"],
            "run_id": run["run_id"],
            "event_type": "run_created",
            "message": "run accepted",
            "payload": {"run_type": run["run_type"]},
        },
    )
    return {
        "message": "run accepted",
        **run,
    }


@router.get("/{run_id}")
async def get_run(run_id: str, db: AsyncSession = Depends(get_db_session)):
    run = await run_service.get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return run


class ExecuteRunRequest(BaseModel):
    project_id: str
    prompt: str


@router.post("/{run_id}/execute")
async def execute_run(run_id: str, payload: ExecuteRunRequest, db: AsyncSession = Depends(get_db_session)):
    run = await run_service.get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    if run["project_id"] != payload.project_id:
        raise HTTPException(status_code=400, detail="project_id mismatch")
    result = await runner.run_once(db, run_id, payload.project_id, payload.prompt)
    return result
