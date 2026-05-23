from datetime import datetime
from uuid import uuid4

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
        return {
            "artifact_id": item.artifact_id,
            "project_id": item.project_id,
            "run_id": item.run_id,
            "artifact_type": item.artifact_type,
            "name": item.name,
            "storage_path": item.storage_path,
            "size_bytes": item.size_bytes,
            "sha256": item.sha256,
            "metadata": item.metadata_json,
        }
