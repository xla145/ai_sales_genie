from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from agent_runner.config import settings
from agent_runner.services.artifact_service import ArtifactService
from agent_runner.services.event_service import EventService
from agent_runner.services.hermes_service import HermesService
from agent_runner.services.run_service import RunService
from agent_runner.storage.local_storage import LocalStorage


class Runner:
    def __init__(self) -> None:
        self.run_service = RunService()
        self.event_service = EventService()
        self.hermes_service = HermesService()
        self.artifact_service = ArtifactService()
        self.storage = LocalStorage(settings.storage_base_path)

    async def run_once(self, db: AsyncSession, run_id: str, project_id: str, prompt: str) -> dict:
        await self.run_service.update_run_status(
            db,
            run_id,
            "running",
            current_step="calling_hermes",
            progress=10,
        )
        await self.event_service.emit(
            db,
            {
                "project_id": project_id,
                "run_id": run_id,
                "event_type": "run_started",
                "message": "runner started",
                "payload": {"step": "calling_hermes"},
            },
        )

        try:
            result = await self.hermes_service.plan(prompt)
            patch_text = result.get("patch") or ""

            paths = self.storage.build_project_paths(project_id)
            run_dir = Path(paths["runs"]) / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            patch_path = run_dir / "patch.diff"
            patch_path.write_text(patch_text, encoding="utf-8")

            artifact = await self.artifact_service.save_artifact(
                db,
                {
                    "project_id": project_id,
                    "run_id": run_id,
                    "artifact_type": "patch",
                    "name": "patch.diff",
                    "storage_path": str(patch_path),
                    "mime_type": "text/x-diff",
                    "size_bytes": patch_path.stat().st_size,
                    "metadata": {"source": "hermes"},
                },
            )

            await self.event_service.emit(
                db,
                {
                    "project_id": project_id,
                    "run_id": run_id,
                    "event_type": "patch_created",
                    "message": "patch generated",
                    "payload": {
                        "path": str(patch_path),
                        "artifact_id": artifact["artifact_id"],
                    },
                },
            )

            run = await self.run_service.update_run_status(
                db,
                run_id,
                "success",
                current_step="completed",
                progress=100,
                patch_path=str(patch_path),
            )
            return {
                "run_id": run_id,
                "status": "success",
                "patch_path": str(patch_path),
                "run": run,
            }
        except Exception as exc:
            await self.run_service.update_run_status(
                db,
                run_id,
                "failed",
                current_step="failed",
                progress=100,
                error_message=str(exc),
            )
            await self.event_service.emit(
                db,
                {
                    "project_id": project_id,
                    "run_id": run_id,
                    "event_type": "run_failed",
                    "level": "error",
                    "message": "runner failed",
                    "payload": {"error": str(exc)},
                },
            )
            raise
