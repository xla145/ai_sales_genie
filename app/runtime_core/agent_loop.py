from __future__ import annotations

from app.runtime_core.context import RuntimeContext
from app.runtime_core.llm.base_client import LLMMessage
from app.runtime_core.session import EngineSession, SessionMode
from app.runtime_core.tools.base import ToolRiskLevel
from app.runtime_core.tools.registry import ToolRegistry
from app.storage.logger import ProjectLogger


async def run_agent_loop(
    *,
    llm_client,
    system_prompt: str,
    user_prompt: str,
    tool_registry: ToolRegistry,
    logger: ProjectLogger,
    model: str | None = None,
    max_iterations: int = 8,
    session: EngineSession | None = None,
    runtime_context: RuntimeContext | None = None,
) -> str:
    messages: list[LLMMessage] = [
        LLMMessage(role="system", content=system_prompt),
        LLMMessage(role="user", content=user_prompt),
    ]
    active_mode = session.mode if session is not None else (runtime_context.mode if runtime_context else SessionMode.ACT)
    available_tools = tool_registry.list_tools_for_mode(active_mode)
    tool_defs = [tool.to_openai_schema()["function"] for tool in available_tools]
    formatted_tools = [
        type("ToolDef", (), {"name": tool["name"], "description": tool["description"], "parameters": tool["parameters"]})()
        for tool in tool_defs
    ]

    if session is not None:
        session.record_message(2)
        if model:
            session.current_model = model

    for iteration in range(max_iterations):
        logger.info(f"Agent loop iteration {iteration + 1} mode={active_mode.value if isinstance(active_mode, SessionMode) else active_mode}")
        response = llm_client.chat(messages, model=model, tools=formatted_tools)
        if session is not None:
            session.record_usage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                model=model,
            )
        if not response.tool_calls:
            logger.info("Agent loop completed without further tool calls")
            if session is not None:
                session.record_message(1)
            return response.content

        messages.append(
            LLMMessage(
                role="assistant",
                content=response.content or "",
                tool_calls=response.tool_calls,
                reasoning_content=response.reasoning_content,
            )
        )
        if session is not None:
            session.record_message(1)
        for tool_call in response.tool_calls:
            logger.info(f"Execute tool call: {tool_call.name}")
            tool = tool_registry.get(tool_call.name)
            if active_mode == SessionMode.PLAN and tool.risk_level != ToolRiskLevel.SAFE:
                raise PermissionError(f"Tool {tool_call.name} is not allowed in plan mode")
            result = tool.handler(**tool_call.arguments)
            messages.append(
                LLMMessage(
                    role="tool",
                    content=result,
                    tool_call_id=tool_call.id,
                    name=tool_call.name,
                )
            )
            if session is not None:
                session.record_message(1)

    raise RuntimeError("Agent loop exceeded max iterations")
