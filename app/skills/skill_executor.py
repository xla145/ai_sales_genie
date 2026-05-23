from __future__ import annotations

from pathlib import Path

from app.engine.skill_registry import WorkflowSkillDefinition
from app.models.run import PhaseId
from app.models.session import ProjectSession
from app.runtime_core.context import RuntimeContext
from app.runtime_core.llm.base_client import BaseLLMClient
from app.runtime_core.skills.executor import execute_skill as execute_runtime_skill
from app.storage.logger import ProjectLogger


def _build_business_constraints(skill: WorkflowSkillDefinition, expected_outputs: list[str]) -> list[str]:
    constraints = [
        "最终必须产出预期文件。",
        "如果 Skill 文档定义了标准交付物结构、章节、表格字段或编号，必须严格遵守，不得自行改写标题体系、章节顺序或字段名称。",
        "信息不足时可以补充内容，但不得删除 Skill 要求的固定章节，也不得改用自由格式替代模板格式。",
        "完成写文件后，最终回复只需简洁说明已写入哪些文件，不要输出新的概览版、改写版或另一套自由格式正文。",
    ]
    if skill.phase_id == PhaseId.PHASE1 and "需求结构化.md" in expected_outputs:
        constraints.append(
            "对于 `需求结构化.md`，必须严格遵循 Skill 文档中第 6 节 `需求结构化.md 标准结构` 生成，文档标题、章节编号、表格字段名必须与模板保持一致。"
        )
    if skill.phase_id == PhaseId.PHASE3:
        constraints.extend(
            [
                "第三阶段的唯一目标是生成 prototype 原型文件和第三阶段报告；除非它明确出现在 expected_outputs 中，否则禁止改写 `第二阶段设计检查报告.md`。",
                "即使输入页面设计存在缺口，也必须优先基于已有页面设计生成可运行的 HTML/CSS/JS 原型骨架，不得把任务退化为补检查报告或仅输出问题清单。",
                "若本次子任务只负责单个页面，则只写入该页面对应的 HTML 文件；不要改写其他页面或共享资源文件。",
                "若本次子任务负责收尾汇总，则必须生成入口页、公共 assets、README、generation-report.md、validation-report.md，不要回写第二阶段文件。",
            ]
        )
    return constraints


def _build_business_context(
    skill: WorkflowSkillDefinition,
    *,
    workspace_dir: Path,
    expected_outputs: list[str],
) -> list[str]:
    return [
        f"当前阶段: {skill.phase_id.value} / {skill.phase_name}",
        f"预期产物: {', '.join(expected_outputs) if expected_outputs else '无'}",
        f"工作目录确认: {workspace_dir}",
    ]


async def execute_skill(
    *,
    llm_client: BaseLLMClient,
    base_dir: Path,
    skill: WorkflowSkillDefinition,
    user_prompt: str,
    workspace_dir: Path,
    input_files: list[str],
    expected_outputs: list[str],
    logger: ProjectLogger,
    model: str | None = None,
    max_iterations: int = 8,
    input_summary: str | None = None,
    session: ProjectSession | None = None,
    runtime_metadata: dict[str, str] | None = None,
) -> str:
    engine_session = session.to_engine_session(metadata=runtime_metadata) if session is not None else None
    runtime_context = RuntimeContext.from_session(engine_session, metadata=runtime_metadata) if engine_session is not None else None
    result = await execute_runtime_skill(
        llm_client=llm_client,
        base_dir=base_dir,
        skill=skill.runtime_skill,
        user_prompt=user_prompt,
        workspace_dir=workspace_dir,
        input_files=input_files,
        logger=logger,
        model=model,
        max_iterations=max_iterations,
        input_summary=input_summary,
        session=engine_session,
        runtime_context=runtime_context,
        extra_constraints=_build_business_constraints(skill, expected_outputs),
        extra_context=_build_business_context(skill, workspace_dir=workspace_dir, expected_outputs=expected_outputs),
    )
    if session is not None and engine_session is not None:
        session.sync_from_engine_session(engine_session)
    return result
