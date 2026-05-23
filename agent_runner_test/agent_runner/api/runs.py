from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agent_runner.db.session import get_db_session
from agent_runner.services.artifact_service import ArtifactService
from agent_runner.services.event_service import EventService
from agent_runner.services.run_service import RunService
from agent_runner.worker.runner import Runner

router = APIRouter(prefix="/runs", tags=["runs"])
run_service = RunService()
event_service = EventService()
artifact_service = ArtifactService()
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
    result = await runner.run_once(db, run_id, payload.project_id, payload.prompt, session_id=run.get("session_id"))
    patch_path = result.get("patch_path")
    if isinstance(patch_path, str) and patch_path:
        result["patch_download_url"] = f"/runs/{run_id}/patch"

    artifacts = await artifact_service.list_run_artifacts(db, run_id)
    result["artifacts"] = [
        {
            **item,
            "download_url": f"/runs/{run_id}/artifacts/{item['artifact_id']}",
        }
        for item in artifacts
    ]
    return result


@router.get("/{run_id}/patch")
async def download_patch(run_id: str, db: AsyncSession = Depends(get_db_session)):
    run = await run_service.get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    patch_path = run.get("patch_path")
    if not patch_path:
        raise HTTPException(status_code=404, detail="patch not found")
    file_path = Path(patch_path)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="patch file missing")
    return FileResponse(path=file_path, media_type="text/x-diff", filename=file_path.name)


@router.get("/{run_id}/artifacts")
async def list_run_artifacts(run_id: str, db: AsyncSession = Depends(get_db_session)):
    run = await run_service.get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    artifacts = await artifact_service.list_run_artifacts(db, run_id)
    return {
        "run_id": run_id,
        "artifacts": [
            {
                **item,
                "download_url": f"/runs/{run_id}/artifacts/{item['artifact_id']}",
            }
            for item in artifacts
        ],
    }


@router.get("/{run_id}/artifacts/{artifact_id}")
async def download_run_artifact(run_id: str, artifact_id: str, db: AsyncSession = Depends(get_db_session)):
    run = await run_service.get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    artifact = await artifact_service.get_artifact(db, run_id, artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="artifact not found")
    storage_path = artifact.get("storage_path")
    if not storage_path:
        raise HTTPException(status_code=404, detail="artifact path missing")
    file_path = Path(storage_path)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="artifact file missing")
    media_type = artifact.get("mime_type") or "application/octet-stream"
    filename = artifact.get("name") or file_path.name
    return FileResponse(path=file_path, media_type=media_type, filename=filename)
