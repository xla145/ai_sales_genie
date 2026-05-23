from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMMessage:
    role: str
    content: str
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    reasoning_content: str | None = None


@dataclass
class LLMResponse:
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    reasoning_content: str | None = None
    usage: TokenUsage = field(default_factory=TokenUsage)
    raw: Any = None


class BaseLLMClient(Protocol):
    def list_models(self) -> list[str]: ...

    def chat(
        self,
        messages: list[LLMMessage],
        *,
        model: str | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse: ...
