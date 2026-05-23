from __future__ import annotations

import json
from typing import Any

from app.clients.hermes_client import HermesClient
from app.runtime_core.llm.base_client import BaseLLMClient, LLMMessage, LLMResponse, TokenUsage, ToolCall, ToolDefinition


class OpenAICompatibleClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.client = HermesClient(base_url=base_url, api_key=api_key, timeout=timeout)
        self.default_model = model

    def list_models(self) -> list[str]:
        return self.client.model_ids()

    def chat(
        self,
        messages: list[LLMMessage],
        *,
        model: str | None = None,
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
        payload_messages: list[dict[str, Any]] = []
        for message in messages:
            entry: dict[str, Any] = {"role": message.role, "content": message.content}
            if message.tool_call_id:
                entry["tool_call_id"] = message.tool_call_id
            if message.name:
                entry["name"] = message.name
            if message.reasoning_content:
                entry["reasoning_content"] = message.reasoning_content
            if message.tool_calls:
                entry["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": json.dumps(tool_call.arguments, ensure_ascii=False),
                        },
                    }
                    for tool_call in message.tool_calls
                ]
            payload_messages.append(entry)

        body_tools = []
        for tool in tools or []:
            body_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
            )

        response = self.client.chat(payload_messages, model=model or self.default_model, tools=body_tools or None)
        if not response.ok:
            raise RuntimeError(f"LLM request failed: {response.data}")

        choice = ((response.data or {}).get("choices") or [{}])[0]
        message = choice.get("message") or {}
        content = message.get("content") or ""
        reasoning_content = message.get("reasoning_content") or message.get("reasoning") or ""
        tool_calls_raw = message.get("tool_calls") or []
        tool_calls: list[ToolCall] = []
        for item in tool_calls_raw:
            function = item.get("function") or {}
            raw_args = function.get("arguments") or "{}"
            try:
                parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except json.JSONDecodeError:
                parsed_args = {}
            tool_calls.append(
                ToolCall(
                    id=item.get("id") or function.get("name") or "tool-call",
                    name=function.get("name") or "",
                    arguments=parsed_args if isinstance(parsed_args, dict) else {},
                )
            )
        usage_raw = (response.data or {}).get("usage") or {}
        usage = TokenUsage(
            input_tokens=int(usage_raw.get("prompt_tokens") or usage_raw.get("input_tokens") or 0),
            output_tokens=int(usage_raw.get("completion_tokens") or usage_raw.get("output_tokens") or 0),
        )
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            reasoning_content=reasoning_content if isinstance(reasoning_content, str) and reasoning_content else None,
            usage=usage,
            raw=response.data,
        )
