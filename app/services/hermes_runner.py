from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.runtime_core.llm.base_client import BaseLLMClient, LLMMessage

from app.engine.skill_registry import WorkflowSkillDefinition
from app.skills.skill_executor import execute_skill

from app.models.project import Project
from app.models.run import PhaseId, ProjectRun, RunStatus, SubtaskRun
from app.models.session import ProjectSession
from app.services.session_service import SessionService
from app.storage.logger import ProjectLogger


def _build_runtime_metadata(
    *,
    project_id: str,
    phase_id: str,
    conversation: str,
    workflow_id: str | None = None,
    subtask_id: str | None = None,
) -> dict[str, str]:
    metadata = {
        "conversation": conversation,
        "project_id": project_id,
        "phase_id": phase_id,
    }
    if workflow_id:
        metadata["workflow_id"] = workflow_id
    if subtask_id:
        metadata["subtask_id"] = subtask_id
    return metadata


async def run_project(
    project: Project,
    session: ProjectSession,
    run: ProjectRun,
    logger: ProjectLogger,
    session_service: SessionService,
    llm_client: BaseLLMClient,
    base_dir: Path,
    skill_definition: WorkflowSkillDefinition | None = None,
) -> dict[str, Any]:
    result = await execute_prompt_task(
        project=project,
        session=session,
        logger=logger,
        session_service=session_service,
        llm_client=llm_client,
        base_dir=base_dir,
        prompt=str(project.config.get("prompt") or "请返回一段简短验证文本"),
        phase_id=run.phase_id.value,
        phase_name=run.phase_name,
        skill_name=run.skill_name,
        input_files=run.input_files,
        expected_outputs=run.expected_outputs,
        output_name=f"{run.run_id}.txt",
        conversation=session.conversation,
        skill_definition=skill_definition,
        runtime_metadata=_build_runtime_metadata(
            project_id=project.project_id,
            phase_id=run.phase_id.value,
            conversation=session.conversation,
            workflow_id=run.run_id,
        ),
    )
    return {
        "phase_id": run.phase_id.value,
        "phase_name": run.phase_name,
        "skill_name": run.skill_name,
        **result,
    }


async def run_subtask(
    project: Project,
    session: ProjectSession,
    subtask: SubtaskRun,
    logger: ProjectLogger,
    session_service: SessionService,
    llm_client: BaseLLMClient,
    base_dir: Path,
    skill_definition: WorkflowSkillDefinition | None = None,
) -> dict[str, Any]:
    subtask.status = RunStatus.RUNNING
    subtask.started_at = datetime.now()
    result = await execute_prompt_task(
        project=project,
        session=session,
        logger=logger,
        session_service=session_service,
        llm_client=llm_client,
        base_dir=base_dir,
        prompt=subtask.prompt,
        phase_id=subtask.phase_id.value,
        phase_name=subtask.phase_name,
        skill_name=subtask.skill_name,
        input_files=subtask.input_files,
        expected_outputs=subtask.expected_outputs,
        output_name=f"{subtask.subtask_id}.txt",
        conversation=f"{session.conversation}:{subtask.subtask_id}",
        skill_definition=skill_definition,
        runtime_metadata=_build_runtime_metadata(
            project_id=project.project_id,
            phase_id=subtask.phase_id.value,
            conversation=f"{session.conversation}:{subtask.subtask_id}",
            workflow_id=subtask.workflow_id,
            subtask_id=subtask.subtask_id,
        ),
    )
    subtask.status = RunStatus.SUCCESS
    subtask.ended_at = datetime.now()
    subtask.input_tokens = session.input_tokens
    subtask.output_tokens = session.output_tokens
    subtask.result_summary = {
        "phase_id": subtask.phase_id.value,
        "phase_name": subtask.phase_name,
        "skill_name": subtask.skill_name,
        **result,
    }
    return subtask.result_summary


async def execute_prompt_task(
    project: Project,
    session: ProjectSession,
    logger: ProjectLogger,
    session_service: SessionService,
    llm_client: BaseLLMClient,
    base_dir: Path,
    *,
    prompt: str,
    phase_id: str,
    phase_name: str,
    skill_name: str,
    input_files: list[str],
    expected_outputs: list[str],
    output_name: str,
    conversation: str,
    skill_definition: WorkflowSkillDefinition | None = None,
    runtime_metadata: dict[str, str] | None = None,
) -> dict[str, Any]:
    logger.info(f"[阶段 {phase_id}] 开始：{phase_name}")
    logger.info(f"Skill: {skill_name}")
    if input_files:
        logger.info(f"依赖输入: {', '.join(input_files)}")
    if expected_outputs:
        logger.info(f"预期产物: {', '.join(expected_outputs)}")
    logger.info(f"Run started for project={project.project_id}")
    logger.info("Load project config")
    await asyncio.sleep(0.2)

    if project.config.get("fail"):
        logger.error("Configured failure triggered")
        raise RuntimeError("Configured failure triggered")

    sleep_seconds = float(project.config.get("sleep_seconds") or 0.0)
    if sleep_seconds > 0:
        logger.info(f"Sleep for {sleep_seconds} seconds before Hermes request")
        await asyncio.sleep(sleep_seconds)

    workspace_dir = Path(session.workspace_path)
    if skill_definition is not None:
        input_summary = _build_skill_input_summary(
            workspace_dir=workspace_dir,
            phase_id=phase_id,
            input_files=input_files,
            expected_outputs=expected_outputs,
        )
        content = await execute_skill(
            llm_client=llm_client,
            base_dir=base_dir,
            skill=skill_definition,
            user_prompt=prompt,
            workspace_dir=workspace_dir,
            input_files=input_files,
            expected_outputs=expected_outputs,
            input_summary=input_summary,
            logger=logger,
            model=project.config.get("llm_model"),
            max_iterations=int(project.config.get("agent_loop_max_iterations") or 8),
            session=session,
            runtime_metadata=runtime_metadata,
        )
        materialized_files = _collect_workspace_files(workspace_dir, expected_outputs)
        _validate_expected_outputs(workspace_dir, phase_name, expected_outputs)
        deleted_files: list[str] = []
        output_path = workspace_dir / "outputs" / output_name
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Output written to {output_path.name}")
        logger.info(f"[阶段 {phase_id}] 完成：{phase_name}")
        logger.info("Run finished successfully")
        return {
            "output_file": output_path.name,
            "content_preview": content[:200],
            "materialized_files": materialized_files,
            "deleted_files": deleted_files,
        }

    request_prompt = _build_workspace_prompt(prompt, workspace_dir)
    logger.info("Prepare Hermes client")

    content = ""
    partial_content = ""
    input_tokens = 0
    output_tokens = 0
    materialized_files: list[str] = []
    deleted_files: list[str] = []
    timeout_seconds = _stream_timeout_seconds(project.config)
    try:
        logger.info("Resolve model")
        model = _resolve_model(llm_client, project.config.get("model") or project.config.get("llm_model"))
        logger.info(f"Use injected llm client model={model}")
        logger.info(f"Request chat completions with conversation={conversation}")

        def _chat_once() -> tuple[str, int, int]:
            response = llm_client.chat([LLMMessage(role="user", content=request_prompt)], model=model)
            generated = (response.content or "").strip()
            if not generated:
                raise RuntimeError("LLM chat returned empty content")
            logger.stream_chunk(generated)
            return generated, response.usage.input_tokens, response.usage.output_tokens

        content, input_tokens, output_tokens = await asyncio.wait_for(asyncio.to_thread(_chat_once), timeout=timeout_seconds)
    except Exception as exc:
        logger.error(f"LLM request failed ({type(exc).__name__}): {exc}")
        logger.error("Fallback to mock output")
        content = f"mock result for {project.project_id}: {prompt}"
    else:
        session.hermes_session_ref = conversation
        session.record_message(1)
        session.record_usage(input_tokens=input_tokens, output_tokens=output_tokens, model=model)
        session.metadata["last_task_context"] = runtime_metadata or {
            "conversation": conversation,
            "mode": session.mode.value,
        }
        try:
            session_service.save_session(project, session)
            logger.info("Saved Hermes session")
        except Exception as exc:
            logger.error(f"Session save failed ({type(exc).__name__}): {exc}")
            raise

        logger.info("LLM response received")

    try:
        materialized_files, deleted_files = _materialize_response_files(content, workspace_dir, logger)
    except Exception as exc:
        logger.error(f"Response materialization failed ({type(exc).__name__}): {exc}")
        raise

    output_path = workspace_dir / "outputs" / output_name
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"Output written to {output_path.name}")
    logger.info(f"[阶段 {phase_id}] 完成：{phase_name}")
    logger.info("Run finished successfully")
    return {
        "output_file": output_path.name,
        "content_preview": content[:200],
        "materialized_files": materialized_files,
        "deleted_files": deleted_files,
    }


def _collect_workspace_files(workspace_dir: Path, expected_outputs: list[str]) -> list[str]:
    collected: list[str] = []
    for relative_path in expected_outputs:
        candidate = workspace_dir / relative_path
        if candidate.is_file():
            collected.append(str(candidate.relative_to(workspace_dir.resolve())))
        elif candidate.is_dir():
            collected.extend(
                str(item.relative_to(workspace_dir.resolve()))
                for item in sorted(candidate.rglob("*"))
                if item.is_file()
            )
    return collected


def _build_skill_input_summary(
    *,
    workspace_dir: Path,
    phase_id: str,
    input_files: list[str],
    expected_outputs: list[str],
) -> str | None:
    if phase_id != PhaseId.PHASE3.value:
        return None

    page_dir = workspace_dir / "页面详细设计"
    page_files = sorted(page_dir.glob("*.md")) if page_dir.exists() else []
    non_empty_files = [item for item in page_files if item.is_file() and item.stat().st_size > 0]
    empty_files = [item.name for item in page_files if item.is_file() and item.stat().st_size == 0]
    expected_page_outputs = [item for item in expected_outputs if item.startswith("prototype/pages/")]

    if page_dir.exists() and page_files and not non_empty_files:
        raise RuntimeError("原型生成 缺少可用页面设计：页面详细设计目录内文件均为空")

    summary_lines = [
        f"phase3 输入文件: {', '.join(input_files) if input_files else '无'}",
        f"页面设计文件总数: {len(page_files)}",
        f"可用页面设计数: {len(non_empty_files)}",
        f"空页面设计文件: {', '.join(empty_files) if empty_files else '无'}",
        f"页面级预期产物数: {len(expected_page_outputs)}",
    ]
    if expected_page_outputs:
        summary_lines.append(f"页面级目标: {', '.join(expected_page_outputs)}")
    if non_empty_files:
        summary_lines.append(
            "可用页面设计样例: " + ", ".join(item.name for item in non_empty_files[:8])
        )
    return "\n".join(summary_lines)


def _validate_expected_outputs(workspace_dir: Path, phase_name: str, expected_outputs: list[str]) -> None:
    missing_outputs = [relative_path for relative_path in expected_outputs if not (workspace_dir / relative_path).exists()]
    if missing_outputs:
        missing = ", ".join(missing_outputs)
        raise RuntimeError(f"{phase_name} 未生成预期产物: {missing}")


def _stream_timeout_seconds(config: dict[str, Any]) -> float:
    configured = config.get("stream_timeout_seconds")
    if isinstance(configured, (int, float)) and configured > 0:
        return float(configured)
    return 30.0


def _resolve_model(client: BaseLLMClient, configured_model: Any) -> str:
    if isinstance(configured_model, str) and configured_model.strip():
        return configured_model.strip()

    model_ids = client.list_models()
    if model_ids:
        return model_ids[0]

    raise RuntimeError("No model available from provider")


def _build_workspace_prompt(user_prompt: str, workspace_dir: Path) -> str:
    return (
        f"你当前绑定的唯一工作目录是：{workspace_dir}\n"
        "该工作目录由宿主系统按当前项目/当前会话隔离创建，你只能在该 workspace 内工作，不得读取、复用、覆盖或删除其他项目、其他 session 的文件。\n"
        "如果你创建、修改或删除了文件，请在最终答案中只返回 JSON，不要附加解释。\n"
        "JSON 格式必须是：\n"
        '{"files":[{"path":"相对路径","content":"文件内容"}],"deleted_files":["相对路径"]}\n'
        "硬性要求：files[].path 和 deleted_files[] 必须是相对当前 workspace 的相对路径，例如 `需求结构化.md`、`页面详细设计/首页.md`、`prototype/index.html`。\n"
        "禁止返回 /opt/data、/opt/hermes、/tmp、/workspace 或任何其他绝对路径；工作目录字段只用于隔离确认，不得拼进 path。\n"
        "如果输入材料中包含绝对路径，只能视为历史描述，不得作为真实读写路径。\n"
        "如果没有文件变更，也返回合法 JSON：{\"files\":[],\"deleted_files\":[]}。\n\n"
        f"用户任务：{user_prompt}"
    )


def _materialize_response_files(
    content: str,
    workspace_dir: Path,
    logger: ProjectLogger,
) -> tuple[list[str], list[str]]:
    payload = _extract_json_payload(content)
    if payload is None:
        logger.info("Hermes response has no parseable JSON payload; skip file materialization")
        return [], []

    files = payload.get("files")
    deleted = payload.get("deleted_files")
    if not isinstance(files, list):
        files = []
    if not isinstance(deleted, list):
        deleted = []
    if not files and not deleted:
        logger.info("Hermes response JSON has no files or deleted_files; skip file materialization")
        return [], []

    written_paths: list[str] = []
    for item in files:
        if not isinstance(item, dict):
            continue
        relative_path = item.get("path")
        file_content = item.get("content")
        if not isinstance(relative_path, str) or not relative_path:
            continue
        if not isinstance(file_content, str):
            continue

        target_path = _resolve_workspace_path(workspace_dir, relative_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(file_content, encoding="utf-8")
        written_paths.append(str(target_path.relative_to(workspace_dir.resolve())))
        logger.info(f"Materialized file: {written_paths[-1]}")

    deleted_paths: list[str] = []
    for item in deleted:
        if not isinstance(item, str) or not item:
            continue
        target_path = _resolve_workspace_path(workspace_dir, item)
        if target_path.exists() and target_path.is_file():
            target_path.unlink()
            deleted_paths.append(str(target_path.relative_to(workspace_dir.resolve())))
            logger.info(f"Deleted file: {deleted_paths[-1]}")

    return written_paths, deleted_paths


def _extract_json_payload(content: str) -> dict[str, Any] | None:
    candidates = [content.strip()]

    fence_marker = "```"
    if fence_marker in content:
        segments = content.split(fence_marker)
        for segment in segments[1::2]:
            stripped = segment.strip()
            if not stripped:
                continue
            if stripped.startswith("json"):
                stripped = stripped[4:].lstrip()
            candidates.append(stripped)

    for candidate in candidates:
        if not candidate:
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _resolve_workspace_path(workspace_dir: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError(f"Absolute path is not allowed: {relative_path}")

    normalized = (workspace_dir / candidate).resolve()
    workspace_root = workspace_dir.resolve()
    if normalized != workspace_root and workspace_root not in normalized.parents:
        raise ValueError(f"Path escapes workspace: {relative_path}")
    return normalized
