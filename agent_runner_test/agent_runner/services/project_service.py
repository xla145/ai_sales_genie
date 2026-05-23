from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from agent_runner.db.models import Project


class ProjectService:
    async def create_project(self, db: AsyncSession, payload: dict) -> dict:
        now = datetime.utcnow()
        item = Project(
            project_id=payload["project_id"],
            name=payload.get("name"),
            description=payload.get("description"),
            status="active",
            current_version=0,
            created_at=now,
            updated_at=now,
        )
        db.add(item)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise ValueError("project_id already exists")
        await db.refresh(item)
        return {
            "project_id": item.project_id,
            "name": item.name,
            "description": item.description,
            "status": item.status,
            "current_version": item.current_version,
        }

    async def get_project(self, db: AsyncSession, project_id: str) -> dict | None:
        row = await db.scalar(select(Project).where(Project.project_id == project_id))
        if row is None:
            return None
        return {
            "project_id": row.project_id,
            "name": row.name,
            "description": row.description,
            "status": row.status,
            "current_version": row.current_version,
            "storage_path": row.storage_path,
        }
