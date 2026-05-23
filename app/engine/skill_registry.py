from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.models.run import PhaseId
from app.runtime_core.skills.definitions import SkillDefinition, load_skill_prompt


@dataclass(frozen=True)
class WorkflowSkillDefinition:
    phase_id: PhaseId
    phase_name: str
    input_files: tuple[str, ...]
    expected_outputs: tuple[str, ...]
    supports_parallelism: bool = False
    runtime_skill: SkillDefinition = SkillDefinition(skill_name="", allowed_tools=())

    @property
    def skill_name(self) -> str:
        return self.runtime_skill.skill_name

    @property
    def prompt_file(self) -> str | None:
        return self.runtime_skill.prompt_file

    @property
    def system_prompt(self) -> str:
        return self.runtime_skill.system_prompt

    @property
    def allowed_tools(self) -> tuple[str, ...]:
        return self.runtime_skill.allowed_tools

    @property
    def execution_timeout(self) -> int:
        return self.runtime_skill.execution_timeout


SKILL_DEFINITIONS: tuple[WorkflowSkillDefinition, ...] = (
    WorkflowSkillDefinition(
        phase_id=PhaseId.PHASE1,
        phase_name="需求录入与结构化",
        input_files=(),
        expected_outputs=("需求结构化.md",),
        supports_parallelism=False,
        runtime_skill=SkillDefinition(
            skill_name="requirement-intake-structuring",
            system_prompt="你是需求结构化助手。请读取用户需求并输出结构化需求文档，必要时使用文件工具把结果写入 需求结构化.md。",
            prompt_file=".claude/skills/phase2-requirement-intake-structuring/SKILL.md",
            allowed_tools=("read_file", "write_file", "list_files"),
        ),
    ),
    WorkflowSkillDefinition(
        phase_id=PhaseId.PHASE2,
        phase_name="系统功能设计与页面规划",
        input_files=("需求结构化.md",),
        expected_outputs=(
            "系统全局功能描述与设计.md",
            "系统的功能点设计.md",
            "页面详细设计/",
            "第二阶段设计检查报告.md",
        ),
        supports_parallelism=True,
        runtime_skill=SkillDefinition(
            skill_name="system-function-design-planning",
            system_prompt="你是系统设计与页面规划助手。请基于现有需求文档拆解功能、页面与设计产物，并使用文件工具生成第二阶段文档。",
            prompt_file=".claude/skills/phase1-system-function-design-planning/SKILL.md",
            allowed_tools=("read_file", "write_file", "list_files"),
        ),
    ),
    WorkflowSkillDefinition(
        phase_id=PhaseId.PHASE3,
        phase_name="原型生成",
        input_files=(
            "系统全局功能描述与设计.md",
            "系统的功能点设计.md",
            "页面详细设计/",
            "第二阶段设计检查报告.md",
        ),
        expected_outputs=(
            "prototype/index.html",
            "prototype/README.md",
            "prototype/assets/css/styles.css",
            "prototype/assets/js/app.js",
            "prototype/assets/js/mock-data.js",
            "generation-report.md",
            "validation-report.md",
            "prototype/pages/*.html",
        ),
        supports_parallelism=True,
        runtime_skill=SkillDefinition(
            skill_name="prototype-generator",
            system_prompt="你是原型生成助手。请读取设计文档并生成 prototype 目录下的 HTML/CSS/JS 文件及生成报告。",
            prompt_file=".claude/skills/phase3-prototype-generator/SKILL.md",
            allowed_tools=("read_file", "write_file", "list_files"),
        ),
    ),
)


def list_skill_definitions() -> list[WorkflowSkillDefinition]:
    return list(SKILL_DEFINITIONS)


def get_skill_definition(phase_id: PhaseId) -> WorkflowSkillDefinition:
    for definition in SKILL_DEFINITIONS:
        if definition.phase_id == phase_id:
            return definition
    raise KeyError(phase_id)


__all__ = [
    "WorkflowSkillDefinition",
    "SkillDefinition",
    "get_skill_definition",
    "list_skill_definitions",
    "load_skill_prompt",
]
