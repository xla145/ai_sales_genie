from __future__ import annotations

from app.runtime_core.session import SessionMode
from app.runtime_core.tools.base import ToolRiskLevel, ToolSpec


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, tool: ToolSpec) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolSpec:
        return self._tools[name]

    def list_tools(self) -> list[ToolSpec]:
        return list(self._tools.values())

    def list_tools_for_mode(self, mode: SessionMode | str) -> list[ToolSpec]:
        normalized_mode = mode.value if isinstance(mode, SessionMode) else str(mode)
        if normalized_mode == SessionMode.PLAN.value:
            return [tool for tool in self._tools.values() if tool.risk_level == ToolRiskLevel.SAFE]
        return list(self._tools.values())

    def metadata(self, mode: SessionMode | str | None = None) -> list[dict[str, object]]:
        tools = self.list_tools_for_mode(mode or SessionMode.ACT)
        return [tool.metadata() for tool in tools]
