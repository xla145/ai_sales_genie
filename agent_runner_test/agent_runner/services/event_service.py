from datetime import datetime
from uuid import uuid4

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_runner.db.models import RunEvent


class EventService:
    async def emit(self, db: AsyncSession, payload: dict) -> dict:
        item = RunEvent(
            event_id=payload.get("event_id") or f"evt_{uuid4().hex[:16]}",
            project_id=payload["project_id"],
            run_id=payload["run_id"],
            event_type=payload["event_type"],
            level=payload.get("level", "info"),
            message=payload.get("message"),
            payload=payload.get("payload"),
            created_at=payload.get("created_at") or datetime.utcnow(),
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return self._to_dict(item)

    async def list_events(self, db: AsyncSession, run_id: str, after_id: int = 0, limit: int = 200) -> list[dict]:
        stmt = (
            select(RunEvent)
            .where(and_(RunEvent.run_id == run_id, RunEvent.id > after_id))
            .order_by(RunEvent.id.asc())
            .limit(limit)
        )
        rows = (await db.scalars(stmt)).all()
        return [self._to_dict(row) for row in rows]

    @staticmethod
    def _to_dict(row: RunEvent) -> dict:
        return {
            "id": row.id,
            "event_id": row.event_id,
            "project_id": row.project_id,
            "run_id": row.run_id,
            "event_type": row.event_type,
            "level": row.level,
            "message": row.message,
            "payload": row.payload,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
