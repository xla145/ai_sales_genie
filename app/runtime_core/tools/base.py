from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class ToolRiskLevel(str, Enum):
    SAFE = "safe"
    WRITE = "write"


@dataclass(frozen=True)
class ToolExecutionContext:
    workspace_dir: Path
    session_mode: str = "act"
    session_id: str | None = None
    conversation: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters_schema: dict[str, Any]
    handler: Callable[..., str]
    risk_level: ToolRiskLevel = ToolRiskLevel.SAFE

    def to_openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
            "risk_level": self.risk_level.value,
        }
