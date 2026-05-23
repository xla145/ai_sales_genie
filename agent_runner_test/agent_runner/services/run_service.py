from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from agent_runner.db.models import ProjectRun


class RunService:
    async def create_run(self, db: AsyncSession, payload: dict) -> dict:
        now = datetime.utcnow()
        item = ProjectRun(
            run_id=payload["run_id"],
            project_id=payload["project_id"],
            session_id=payload["session_id"],
            run_type=payload["run_type"],
            user_message=payload.get("user_message"),
            status="queued",
            progress=0,
            created_at=now,
            updated_at=now,
        )
        db.add(item)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise ValueError("run_id already exists")
        await db.refresh(item)
        return {
            "run_id": item.run_id,
            "project_id": item.project_id,
            "session_id": item.session_id,
            "run_type": item.run_type,
            "status": item.status,
            "progress": item.progress,
        }

    async def get_run(self, db: AsyncSession, run_id: str) -> dict | None:
        row = await db.scalar(select(ProjectRun).where(ProjectRun.run_id == run_id))
        if row is None:
            return None
        return {
            "run_id": row.run_id,
            "project_id": row.project_id,
            "session_id": row.session_id,
            "run_type": row.run_type,
            "status": row.status,
            "current_step": row.current_step,
            "progress": row.progress,
            "error_message": row.error_message,
            "patch_path": row.patch_path,
        }

    async def update_run_status(
        self,
        db: AsyncSession,
        run_id: str,
        status: str,
        *,
        current_step: str | None = None,
        progress: int | None = None,
        error_message: str | None = None,
        patch_path: str | None = None,
    ) -> dict | None:
        row = await db.scalar(select(ProjectRun).where(ProjectRun.run_id == run_id))
        if row is None:
            return None
        row.status = status
        if current_step is not None:
            row.current_step = current_step
        if progress is not None:
            row.progress = progress
        if error_message is not None:
            row.error_message = error_message
        if patch_path is not None:
            row.patch_path = patch_path
        now = datetime.utcnow()
        row.updated_at = now
        if status == "running" and row.started_at is None:
            row.started_at = now
        if status in {"success", "failed"}:
            row.finished_at = now
        await db.commit()
        await db.refresh(row)
        return {
            "run_id": row.run_id,
            "status": row.status,
            "current_step": row.current_step,
            "progress": row.progress,
            "error_message": row.error_message,
            "patch_path": row.patch_path,
        }
