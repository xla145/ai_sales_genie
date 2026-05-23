from __future__ import annotations

from pathlib import Path

from app.runtime_core.agent_loop import run_agent_loop
from app.runtime_core.context import RuntimeContext
from app.runtime_core.llm.base_client import BaseLLMClient
from app.runtime_core.session import EngineSession
from app.runtime_core.skills.definitions import SkillDefinition, load_skill_prompt
from app.runtime_core.tools.registry import ToolRegistry
from app.runtime_core.tools.workspace import build_workspace_tools
from app.storage.logger import ProjectLogger


def read_input_context(workspace_dir: Path, input_files: list[str]) -> str:
    sections: list[str] = []
    for relative_path in input_files:
        target = workspace_dir / relative_path
        if target.is_file():
            try:
                content = target.read_text(encoding="utf-8")
            except Exception:
                continue
            sections.append(f"## 输入文件: {relative_path}\n\n{content}")
    return "\n\n".join(sections)


def build_skill_execution_prompt(
    *,
    base_dir: Path,
    skill: SkillDefinition,
    user_prompt: str,
    workspace_dir: Path,
    input_files: list[str],
    input_summary: str | None = None,
    extra_constraints: list[str] | None = None,
    extra_context: list[str] | None = None,
) -> tuple[str, str]:
    skill_prompt = load_skill_prompt(base_dir, skill)
    input_context = read_input_context(workspace_dir, input_files)
    execution_constraints = [
        "执行约束：只能在当前 workspace 内工作；优先复用已有文件；若使用工具，严格按允许工具执行。",
        "所有工具参数中的 path 都必须是相对当前 workspace 的相对路径；禁止传入绝对路径；列出当前工作目录内容时请使用 `.`。",
    ]
    execution_constraints.extend(extra_constraints or [])
    system_prompt = "\n\n".join(part for part in (skill_prompt.strip(), *execution_constraints) if part)
    user_context = [
        f"Skill 名称: {skill.skill_name}",
        f"工作目录: {workspace_dir}",
        f"允许工具: {', '.join(skill.allowed_tools)}",
        f"用户任务:\n{user_prompt}",
    ]
    if input_files:
        user_context.insert(2, f"输入文件: {', '.join(input_files)}")
    if input_summary:
        user_context.append(f"\n输入工件摘要:\n{input_summary}")
    if input_context:
        user_context.append(f"\n已有输入内容:\n\n{input_context}")
    user_context.extend(extra_context or [])
    return system_prompt, "\n\n".join(user_context)


async def execute_skill(
    *,
    llm_client: BaseLLMClient,
    base_dir: Path,
    skill: SkillDefinition,
    user_prompt: str,
    workspace_dir: Path,
    input_files: list[str],
    logger: ProjectLogger,
    model: str | None = None,
    max_iterations: int = 8,
    input_summary: str | None = None,
    session: EngineSession | None = None,
    runtime_context: RuntimeContext | None = None,
    extra_constraints: list[str] | None = None,
    extra_context: list[str] | None = None,
) -> str:
    registry = ToolRegistry()
    for tool in build_workspace_tools(workspace_dir):
        if tool.name in skill.allowed_tools:
            registry.register(tool)

    system_prompt, execution_prompt = build_skill_execution_prompt(
        base_dir=base_dir,
        skill=skill,
        user_prompt=user_prompt,
        workspace_dir=workspace_dir,
        input_files=input_files,
        input_summary=input_summary,
        extra_constraints=extra_constraints,
        extra_context=extra_context,
    )

    return await run_agent_loop(
        llm_client=llm_client,
        system_prompt=system_prompt,
        user_prompt=execution_prompt,
        tool_registry=registry,
        logger=logger,
        model=model,
        max_iterations=max_iterations,
        session=session,
        runtime_context=runtime_context,
    )
