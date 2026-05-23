from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_runner.db.models import Artifact


class ArtifactService:
    async def save_artifact(self, db: AsyncSession, payload: dict) -> dict:
        item = Artifact(
            artifact_id=payload.get("artifact_id") or f"art_{uuid4().hex[:16]}",
            project_id=payload["project_id"],
            run_id=payload["run_id"],
            artifact_type=payload["artifact_type"],
            name=payload.get("name"),
            storage_url=payload.get("storage_url"),
            storage_path=payload.get("storage_path"),
            mime_type=payload.get("mime_type"),
            size_bytes=payload.get("size_bytes"),
            sha256=payload.get("sha256"),
            metadata_json=payload.get("metadata"),
            created_at=payload.get("created_at") or datetime.utcnow(),
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return self._to_dict(item)

    async def list_run_artifacts(self, db: AsyncSession, run_id: str) -> list[dict]:
        rows = (
            await db.scalars(
                select(Artifact).where(Artifact.run_id == run_id).order_by(Artifact.created_at.asc(), Artifact.id.asc())
            )
        ).all()
        return [self._to_dict(row) for row in rows]

    async def get_artifact(self, db: AsyncSession, run_id: str, artifact_id: str) -> dict | None:
        row = await db.scalar(
            select(Artifact).where(Artifact.run_id == run_id, Artifact.artifact_id == artifact_id)
        )
        if row is None:
            return None
        return self._to_dict(row)

    @staticmethod
    def _to_dict(item: Artifact) -> dict:
        return {
            "artifact_id": item.artifact_id,
            "project_id": item.project_id,
            "run_id": item.run_id,
            "artifact_type": item.artifact_type,
            "name": item.name,
            "storage_path": item.storage_path,
            "storage_url": item.storage_url,
            "mime_type": item.mime_type,
            "size_bytes": item.size_bytes,
            "sha256": item.sha256,
            "metadata": item.metadata_json,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
