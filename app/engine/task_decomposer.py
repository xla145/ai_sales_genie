from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from pathlib import Path
import re

from app.engine.skill_registry import SkillDefinition
from app.models.run import PhaseId, SubtaskRun


@dataclass(frozen=True)
class DecompositionContext:
    workflow_id: str
    project_id: str
    session_id: str
    prompt: str
    max_parallel_subagents: int
    discovered_targets: list[str]
    log_dir: str


def build_subtasks(
    definition: SkillDefinition,
    context: DecompositionContext,
) -> list[SubtaskRun]:
    targets = [target.strip() for target in context.discovered_targets if target.strip()]
    if definition.phase_id == PhaseId.PHASE3:
        return _build_phase3_subtasks(definition, context, targets)

    groups = _group_targets(targets, context.max_parallel_subagents) if definition.supports_parallelism else []
    if not groups:
        groups = [[]]

    subtasks: list[SubtaskRun] = []
    for index, group in enumerate(groups, start=1):
        target_suffix = f"，聚焦：{', '.join(group)}" if group else ""
        prompt = f"{context.prompt}\n\n当前阶段：{definition.phase_name}\n当前 skill：{definition.skill_name}{target_suffix}"
        subtasks.append(
            SubtaskRun(
                subtask_id=f"subtask_{definition.phase_id.value}_{index}",
                workflow_id=context.workflow_id,
                project_id=context.project_id,
                session_id=context.session_id,
                phase_id=definition.phase_id,
                phase_name=definition.phase_name,
                skill_name=definition.skill_name,
                title=f"{definition.phase_name} 子任务 {index}",
                prompt=prompt,
                input_files=list(definition.input_files),
                expected_outputs=list(definition.expected_outputs),
                log_path=f"{context.log_dir}/{definition.phase_id.value}_{index}.log",
                order=index,
            )
        )
    return subtasks


def discover_targets(definition: SkillDefinition, prompt: str) -> list[str]:
    if not definition.supports_parallelism:
        return []
    if definition.phase_id == PhaseId.PHASE3:
        return _discover_phase3_targets(prompt)

    markers = ["页面：", "页面:", "pages:", "pages："]
    for marker in markers:
        if marker in prompt:
            _, raw = prompt.split(marker, 1)
            return [item.strip(" -，,\n") for item in raw.replace("\n", ",").split(",") if item.strip(" -，,\n")]
    return []


def _group_targets(targets: list[str], max_parallel_subagents: int) -> list[list[str]]:
    if len(targets) <= 1:
        return [targets] if targets else []

    worker_count = min(max_parallel_subagents, len(targets))
    group_size = ceil(len(targets) / worker_count)
    return [targets[i : i + group_size] for i in range(0, len(targets), group_size)]


def _discover_phase3_targets(prompt: str) -> list[str]:
    marker = "页面详细设计/"
    if marker not in prompt:
        return []
    matches = re.findall(r"页面详细设计/([^\n,]+?)(?:\.md)?(?=[,\n]|$)", prompt)
    return [item.strip(" -，,") for item in matches if item.strip(" -，,")]


def _build_phase3_subtasks(
    definition: SkillDefinition,
    context: DecompositionContext,
    targets: list[str],
) -> list[SubtaskRun]:
    if not targets:
        return [
            SubtaskRun(
                subtask_id=f"subtask_{definition.phase_id.value}_1",
                workflow_id=context.workflow_id,
                project_id=context.project_id,
                session_id=context.session_id,
                phase_id=definition.phase_id,
                phase_name=definition.phase_name,
                skill_name=definition.skill_name,
                title=f"{definition.phase_name} 汇总子任务",
                prompt=(
                    f"{context.prompt}\n\n当前阶段：{definition.phase_name}\n当前 skill：{definition.skill_name}\n"
                    "当前任务：生成完整 prototype 目录与最终报告。"
                ),
                input_files=list(definition.input_files),
                expected_outputs=list(definition.expected_outputs),
                log_path=f"{context.log_dir}/{definition.phase_id.value}_1.log",
                order=1,
            )
        ]

    subtasks: list[SubtaskRun] = []
    for index, target in enumerate(targets, start=1):
        slug = _slugify_page_target(target)
        subtasks.append(
            SubtaskRun(
                subtask_id=f"subtask_{definition.phase_id.value}_page_{index}",
                workflow_id=context.workflow_id,
                project_id=context.project_id,
                session_id=context.session_id,
                phase_id=definition.phase_id,
                phase_name=definition.phase_name,
                skill_name=definition.skill_name,
                title=f"{definition.phase_name} 页面子任务 {target}",
                prompt=(
                    f"{context.prompt}\n\n当前阶段：{definition.phase_name}\n当前 skill：{definition.skill_name}"
                    f"\n当前任务：仅根据 页面详细设计/{target}.md 生成该页面原型。"
                    f"\n只允许写入：prototype/pages/{slug}.html"
                ),
                input_files=[*definition.input_files, f"页面详细设计/{target}.md"],
                expected_outputs=[f"prototype/pages/{slug}.html"],
                log_path=f"{context.log_dir}/{definition.phase_id.value}_page_{index}.log",
                order=index,
            )
        )

    finalize_order = len(subtasks) + 1
    subtasks.append(
        SubtaskRun(
            subtask_id=f"subtask_{definition.phase_id.value}_finalize",
            workflow_id=context.workflow_id,
            project_id=context.project_id,
            session_id=context.session_id,
            phase_id=definition.phase_id,
            phase_name=definition.phase_name,
            skill_name=definition.skill_name,
            title=f"{definition.phase_name} 汇总子任务",
            prompt=(
                f"{context.prompt}\n\n当前阶段：{definition.phase_name}\n当前 skill：{definition.skill_name}"
                "\n当前任务：基于已生成的 prototype/pages/*.html，统一生成 index、README、公共 assets、generation-report.md、validation-report.md。"
            ),
            input_files=list(definition.input_files),
            expected_outputs=[
                "prototype/index.html",
                "prototype/README.md",
                "prototype/assets/css/styles.css",
                "prototype/assets/js/app.js",
                "prototype/assets/js/mock-data.js",
                "generation-report.md",
                "validation-report.md",
            ],
            log_path=f"{context.log_dir}/{definition.phase_id.value}_finalize.log",
            order=finalize_order,
        )
    )
    return subtasks


def _slugify_page_target(target: str) -> str:
    cleaned = re.sub(r"\.md$", "", target.strip())
    cleaned = cleaned.replace("/", "-")
    cleaned = re.sub(r"\s+", "-", cleaned)
    return cleaned or "page"
