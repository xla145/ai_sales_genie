from __future__ import annotations

from app.runtime_core.config import EngineConfig
from app.runtime_core.llm.base_client import BaseLLMClient
from app.runtime_core.llm.openai_client import OpenAICompatibleClient


def create_llm_client_from_engine_config(engine_config: EngineConfig) -> BaseLLMClient:
    active_model = engine_config.active_model
    if active_model.provider in {"hermes", "openai-compatible", "openai"}:
        return OpenAICompatibleClient(
            base_url=active_model.base_url,
            api_key=active_model.api_key,
            model=active_model.model,
            timeout=active_model.timeout,
        )
    raise ValueError(f"Unsupported llm provider: {active_model.provider}")


def create_llm_client(config: dict | None = None) -> BaseLLMClient:
    engine_config = EngineConfig.from_dict(config)
    return create_llm_client_from_engine_config(engine_config)
