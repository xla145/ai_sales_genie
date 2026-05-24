from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agent_runner.config import settings
from agent_runner.services.artifact_service import ArtifactService
from agent_runner.services.event_service import EventService
from agent_runner.services.hermes_service import HermesService
from agent_runner.services.run_service import RunService
from agent_runner.storage.local_storage import LocalStorage


LEGACY_DOCUMENT_PATHS = {
    "requirements.md": "需求结构化.md",
    "prd.md": "PRD.md",
    "feature-points.md": "系统的功能点设计.md",
}

ALLOWED_WORKSPACE_FILES = {
    "需求结构化.md",
    "PRD.md",
    "系统全局功能描述与设计.md",
    "系统的功能点设计.md",
    "系统的功能点设计.json",
    "第二阶段设计检查报告.md",
    "generation-report.md",
    "validation-report.md",
}

ALLOWED_WORKSPACE_PREFIXES = (
    "页面详细设计/",
)


class Runner:
    def __init__(self) -> None:
        self.run_service = RunService()
        self.event_service = EventService()
        self.hermes_service = HermesService()
        self.artifact_service = ArtifactService()
        self.storage = LocalStorage(settings.storage_base_path)

    def _build_workspace_prompt(
        self,
        *,
        prompt: str,
        project_id: str,
        session_id: str | None,
        run_id: str,
        workspace_path: str,
        workspace_context: str,
        prototype_version: dict | None,
        run_type: str | None,
    ) -> str:
        artifact_rule = self._build_artifact_rule(run_type, prototype_version)
        return (
            f"当前 project_id: {project_id}\n"
            f"当前 session_id: {session_id or '无'}\n"
            f"当前 run_id: {run_id}\n"
            f"当前 run_type: {run_type or 'unknown'}\n"
            f"当前项目 workspace: {workspace_path}\n"
            "该 workspace 由宿主系统按项目隔离创建，只能作为当前项目的用户空间使用。\n"
            "不得读取、复用、覆盖或删除其他项目、其他 run/session 的文件。\n"
            "所有产物路径、最终回复中的文件路径都必须是相对当前 workspace 的相对路径。\n"
            "禁止使用 /opt/data、/opt/hermes、/tmp、/workspace 或任何其他绝对路径作为真实读写路径。\n"
            "如果输入材料中包含绝对路径，只能作为历史描述，不得作为真实写入位置。\n"
            "如果你生成、修改或删除了文件，最终必须只返回 JSON，不要返回 Markdown 总结。\n"
            "JSON 格式必须是：{\"files\":[{\"path\":\"相对路径\",\"content\":\"完整文件内容\"}],\"deleted_files\":[\"相对路径\"]}。\n"
            "files[].content 必须包含完整文件内容；不得只描述文件已生成，也不得只给产物清单。\n"
            "如果没有文件变更，也返回：{\"files\":[],\"deleted_files\":[]}。\n"
            f"{artifact_rule}\n"
            f"当前 workspace 已有文件内容：\n{workspace_context}\n\n"
            f"用户任务：{prompt}"
        )

    def _guess_mime_type(self, relative_path: str) -> str:
        suffix = Path(relative_path).suffix.lower()
        if suffix == ".md":
            return "text/markdown"
        if suffix == ".html":
            return "text/html"
        if suffix == ".css":
            return "text/css"
        if suffix == ".js":
            return "application/javascript"
        if suffix == ".json":
            return "application/json"
        return "text/plain"

    def _build_artifact_rule(self, run_type: str | None, prototype_version: dict | None) -> str:
        if run_type == "phase2_design":
            return (
                "本次是第二阶段设计产物生成。必须保留所有第二阶段文件，files[].path 使用项目相对路径原名："
                "`系统全局功能描述与设计.md`、`系统的功能点设计.md`、`系统的功能点设计.json`、"
                "`页面详细设计/页面名称.md`、`第二阶段设计检查报告.md`；不得改名为英文别名。"
                "`系统的功能点设计.json` 用于后续表格展示，必须包含功能点列表数组，"
                "每项至少包含模块、名称、说明、优先级、状态等可展示字段。"
            )
        if run_type == "phase3_prototype":
            version_text = f"本次原型输出版本: {prototype_version['version']}。" if prototype_version else ""
            return (
                f"本次是第三阶段原型生成。{version_text}"
                "返回路径必须以 `prototype/` 开头，runner 会写入当前原型版本目录。"
                "如生成 `generation-report.md`、`validation-report.md`，按项目相对路径返回。"
            )
        if run_type == "prototype_edit":
            version_text = ""
            if prototype_version is not None:
                version_text = (
                    f"本次原型输出版本: {prototype_version['version']}，"
                    f"已基于上一版本 {prototype_version.get('base_version') or '无'} 复制出完整目录。"
                )
            return (
                f"本次是原型修改。{version_text}"
                "返回路径必须以 `prototype/` 开头；可以只返回变更文件，runner 会保留上一版本并生成新版本。"
            )
        return "系统保存项目最终产物；返回文件必须使用项目相对路径，不能使用绝对路径。"

    def _build_workspace_context(self, workspace_dir: Path, prototype_dir: Path | None = None) -> str:
        sections: list[str] = []
        if not workspace_dir.exists() and prototype_dir is None:
            return "（无）"

        for path in sorted(workspace_dir.rglob("*")) if workspace_dir.exists() else []:
            if not path.is_file():
                continue
            relative_path = path.relative_to(workspace_dir)
            if any(part.startswith(".") for part in relative_path.parts):
                continue
            if path.stat().st_size > 80_000:
                sections.append(f"## {relative_path}\n（文件过大，已省略内容）")
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            sections.append(f"## {relative_path}\n\n{content}")

        if prototype_dir is not None and prototype_dir.is_dir():
            for path in sorted(prototype_dir.rglob("*")):
                if not path.is_file():
                    continue
                relative_path = Path("prototype") / path.relative_to(prototype_dir)
                if path.stat().st_size > 80_000:
                    sections.append(f"## {relative_path}\n（文件过大，已省略内容）")
                    continue
                try:
                    content = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                sections.append(f"## {relative_path}\n\n{content}")
        return "\n\n".join(sections) if sections else "（无）"

    def _extract_json_payload(self, content: str) -> dict[str, Any] | None:
        candidates = [content.strip()]
        if "```" in content:
            segments = content.split("```")
            for segment in segments[1::2]:
                stripped = segment.strip()
                if stripped.startswith("json"):
                    stripped = stripped[4:].lstrip()
                if stripped:
                    candidates.append(stripped)

        for candidate in candidates:
            try:
                payload = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                return payload
        return None

    def _is_final_document_path(self, relative_path: str) -> bool:
        if relative_path in ALLOWED_WORKSPACE_FILES or relative_path in LEGACY_DOCUMENT_PATHS:
            return True
        if relative_path.startswith("prototype/"):
            return True
        return any(relative_path.startswith(prefix) for prefix in ALLOWED_WORKSPACE_PREFIXES)

    def _target_for_output_path(self, workspace_root: Path, relative_path: str, prototype_dir: Path | None) -> tuple[Path, str]:
        mapped_path = LEGACY_DOCUMENT_PATHS.get(relative_path, relative_path)
        if mapped_path.startswith("prototype/"):
            if prototype_dir is None:
                raise ValueError(f"prototype output is not allowed for this run: {relative_path}")
            return prototype_dir / mapped_path.removeprefix("prototype/"), mapped_path
        return workspace_root / mapped_path, mapped_path

    def _materialize_response_files(
        self,
        workspace_dir: Path,
        content: str,
        *,
        prototype_dir: Path | None = None,
    ) -> tuple[list[dict], list[str]]:
        payload = self._extract_json_payload(content)
        if payload is None:
            return [], []

        files = payload.get("files")
        if not isinstance(files, list):
            files = []
        deleted_files = payload.get("deleted_files")
        if not isinstance(deleted_files, list):
            deleted_files = []

        workspace_root = workspace_dir.resolve()
        prototype_root = prototype_dir.resolve() if prototype_dir is not None else None
        written_files: list[dict] = []
        for item in files:
            if not isinstance(item, dict):
                continue
            relative_path = item.get("path")
            file_content = item.get("content")
            if not isinstance(relative_path, str) or not relative_path:
                continue
            if not isinstance(file_content, str):
                continue

            candidate = Path(relative_path)
            if candidate.is_absolute():
                raise ValueError(f"absolute path is not allowed: {relative_path}")
            if not self._is_final_document_path(relative_path):
                continue

            target, mapped_path = self._target_for_output_path(workspace_root, relative_path, prototype_dir)
            target = target.resolve()
            if prototype_root is not None and mapped_path.startswith("prototype/"):
                if target != prototype_root and prototype_root not in target.parents:
                    raise ValueError(f"path escapes prototype version: {relative_path}")
            elif target != workspace_root and workspace_root not in target.parents:
                raise ValueError(f"path escapes workspace: {relative_path}")

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(file_content, encoding="utf-8")
            written_files.append(
                {
                    "path": mapped_path,
                    "storage_path": str(target),
                    "size_bytes": target.stat().st_size,
                }
            )

        deleted_paths: list[str] = []
        for item in deleted_files:
            if not isinstance(item, str) or not item:
                continue
            candidate = Path(item)
            if candidate.is_absolute():
                raise ValueError(f"absolute path is not allowed: {item}")
            if not self._is_final_document_path(item):
                continue
            target, mapped_path = self._target_for_output_path(workspace_root, item, prototype_dir)
            target = target.resolve()
            if prototype_root is not None and mapped_path.startswith("prototype/"):
                if target != prototype_root and prototype_root not in target.parents:
                    raise ValueError(f"path escapes prototype version: {item}")
            elif target != workspace_root and workspace_root not in target.parents:
                raise ValueError(f"path escapes workspace: {item}")
            if target.is_file():
                target.unlink()
                deleted_paths.append(mapped_path)

        return written_files, deleted_paths

    async def run_once(
        self,
        db: AsyncSession,
        run_id: str,
        project_id: str,
        prompt: str,
        *,
        session_id: str | None = None,
        run_type: str | None = None,
    ) -> dict:
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
            paths = self.storage.build_project_paths(project_id)
            workspace_dir = Path(paths["current"])
            is_prototype_run = run_type in {"phase3_prototype", "prototype_edit"}
            prototype_version = None
            prototype_dir = None
            if is_prototype_run:
                prototype_version = self.storage.create_next_prototype_version(
                    project_id,
                    run_id=run_id,
                    user_instruction=prompt,
                )
                prototype_dir = Path(prototype_version["storage_path"])
            workspace_prompt = self._build_workspace_prompt(
                prompt=prompt,
                project_id=project_id,
                session_id=session_id,
                run_id=run_id,
                workspace_path=paths["current"],
                workspace_context=self._build_workspace_context(workspace_dir, prototype_dir=prototype_dir),
                prototype_version=prototype_version,
                run_type=run_type,
            )
            result = await self.hermes_service.plan(workspace_prompt)
            patch_text = result.get("patch") or ""

            written_files, deleted_files = self._materialize_response_files(
                workspace_dir,
                patch_text,
                prototype_dir=prototype_dir,
            )

            run_dir = Path(paths["runs"]) / run_id
            run_dir.mkdir(parents=True, exist_ok=True)

            output_file = run_dir / "hermes_output.md"
            output_file.write_text(patch_text, encoding="utf-8")

            patch_path = run_dir / "patch.diff"
            patch_path.write_text(patch_text, encoding="utf-8")

            manifest_file = run_dir / "manifest.json"
            project_relative_files = [item["path"] for item in written_files]
            manifest_file.write_text(
                json.dumps(
                    {
                        "project_id": project_id,
                        "run_id": run_id,
                        "run_type": run_type,
                        "workspace_path": str(workspace_dir),
                        "legacy_workspace_path": paths.get("legacy_current"),
                        "project_relative_files": project_relative_files,
                        "prototype_version": prototype_version,
                        "base_version": prototype_version.get("base_version") if prototype_version else None,
                        "version_storage_path": prototype_version.get("storage_path") if prototype_version else None,
                        "copied_from_previous_version": prototype_version.get("copied_from_previous_version") if prototype_version else False,
                        "written_files": written_files,
                        "deleted_files": deleted_files,
                        "json_payload_found": bool(written_files or deleted_files or self._extract_json_payload(patch_text) is not None),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            materialized_artifacts = []
            for written_file in written_files:
                materialized_artifacts.append(
                    await self.artifact_service.save_artifact(
                        db,
                        {
                            "project_id": project_id,
                            "run_id": run_id,
                            "artifact_type": "materialized_file",
                            "name": written_file["path"],
                            "storage_path": written_file["storage_path"],
                            "mime_type": self._guess_mime_type(written_file["path"]),
                            "size_bytes": written_file["size_bytes"],
                            "metadata": {
                                "source": "hermes",
                                "project_relative_path": written_file["path"],
                                "prototype_version": prototype_version["version"] if prototype_version else None,
                            },
                        },
                    )
                )

            output_artifact = await self.artifact_service.save_artifact(
                db,
                {
                    "project_id": project_id,
                    "run_id": run_id,
                    "artifact_type": "generated_file",
                    "name": output_file.name,
                    "storage_path": str(output_file),
                    "mime_type": "text/markdown",
                    "size_bytes": output_file.stat().st_size,
                    "metadata": {"source": "hermes"},
                },
            )

            patch_artifact = await self.artifact_service.save_artifact(
                db,
                {
                    "project_id": project_id,
                    "run_id": run_id,
                    "artifact_type": "patch",
                    "name": patch_path.name,
                    "storage_path": str(patch_path),
                    "mime_type": "text/x-diff",
                    "size_bytes": patch_path.stat().st_size,
                    "metadata": {"source": "hermes"},
                },
            )

            manifest_artifact = await self.artifact_service.save_artifact(
                db,
                {
                    "project_id": project_id,
                    "run_id": run_id,
                    "artifact_type": "manifest",
                    "name": manifest_file.name,
                    "storage_path": str(manifest_file),
                    "mime_type": "application/json",
                    "size_bytes": manifest_file.stat().st_size,
                    "metadata": {"source": "runner"},
                },
            )

            await self.event_service.emit(
                db,
                {
                    "project_id": project_id,
                    "run_id": run_id,
                    "event_type": "generated_file_created",
                    "message": "hermes output file generated",
                    "payload": {
                        "path": str(output_file),
                        "artifact_id": output_artifact["artifact_id"],
                    },
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
                        "artifact_id": patch_artifact["artifact_id"],
                    },
                },
            )

            await self.event_service.emit(
                db,
                {
                    "project_id": project_id,
                    "run_id": run_id,
                    "event_type": "workspace_files_materialized",
                    "message": "hermes files materialized into project workspace",
                    "payload": {
                        "workspace_path": str(workspace_dir),
                        "prototype_version": prototype_version,
                        "written_files": written_files,
                        "deleted_files": deleted_files,
                        "manifest_artifact_id": manifest_artifact["artifact_id"],
                    },
                },
            )

            if prototype_version is not None:
                self.storage.finalize_prototype_version(project_id, prototype_version["version"])
                prototype_version["status"] = "success"

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
                "generated_files": written_files,
                "deleted_files": deleted_files,
                "prototype_version": prototype_version,
                "artifacts": [
                    *[
                        {
                            "artifact_id": item["artifact_id"],
                            "name": item["name"],
                            "artifact_type": item["artifact_type"],
                            "storage_path": item["storage_path"],
                        }
                        for item in materialized_artifacts
                    ],
                    {
                        "artifact_id": output_artifact["artifact_id"],
                        "name": output_file.name,
                        "artifact_type": output_artifact["artifact_type"],
                        "storage_path": str(output_file),
                    },
                    {
                        "artifact_id": patch_artifact["artifact_id"],
                        "name": patch_path.name,
                        "artifact_type": patch_artifact["artifact_type"],
                        "storage_path": str(patch_path),
                    },
                    {
                        "artifact_id": manifest_artifact["artifact_id"],
                        "name": manifest_file.name,
                        "artifact_type": manifest_artifact["artifact_type"],
                        "storage_path": str(manifest_file),
                    },
                ],
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
