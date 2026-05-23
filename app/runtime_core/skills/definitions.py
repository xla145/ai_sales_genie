from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SkillDefinition:
    skill_name: str
    prompt_file: str | None = None
    system_prompt: str = ""
    allowed_tools: tuple[str, ...] = ()
    execution_timeout: int = 300


def load_skill_prompt(base_dir: Path, skill: SkillDefinition) -> str:
    if skill.prompt_file:
        prompt_path = base_dir / skill.prompt_file
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
    return skill.system_prompt
