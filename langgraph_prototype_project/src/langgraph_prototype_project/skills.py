from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path


@lru_cache(maxsize=None)
def load_skill(skill_name: str) -> str:
    skill_path = skill_file_path(skill_name)
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill not found: {skill_path}")
    return skill_path.read_text(encoding="utf-8")


def skill_file_path(skill_name: str) -> Path:
    return skills_root() / skill_name / "SKILL.md"


def skills_root() -> Path:
    configured = os.getenv("LANGGRAPH_PROTOTYPE_SKILLS_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return _repo_root() / ".claude" / "skills"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
