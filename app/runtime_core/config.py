from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

DEFAULT_PROVIDER = "hermes"
DEFAULT_BASE_URL = "http://127.0.0.1:8642"
DEFAULT_TIMEOUT = 120.0


@dataclass(frozen=True)
class ModelConfiguration:
    provider: str = DEFAULT_PROVIDER
    model: str | None = None
    base_url: str = DEFAULT_BASE_URL
    api_key: str | None = None
    timeout: float = DEFAULT_TIMEOUT
    enabled: bool = True
    name: str = "default"
    config_id: str = "default"

    def masked_api_key(self) -> str:
        if not self.api_key:
            return "未配置"
        trimmed = self.api_key.strip()
        if len(trimmed) <= 8:
            return "已配置"
        return f"{trimmed[:4]}...{trimmed[-4:]}"


@dataclass(frozen=True)
class EngineConfigSnapshot:
    active_model_config_id: str
    provider: str
    model: str | None
    base_url: str
    timeout: float
    api_key_masked: str
    configurations: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class EngineConfig:
    active_model_config_id: str = "default"
    configurations: tuple[ModelConfiguration, ...] = field(default_factory=lambda: (ModelConfiguration(),))

    @property
    def active_model(self) -> ModelConfiguration:
        for config in self.configurations:
            if config.config_id == self.active_model_config_id and config.enabled:
                return config
        for config in self.configurations:
            if config.enabled:
                return config
        return self.configurations[0]

    @property
    def provider(self) -> str:
        return self.active_model.provider

    @property
    def base_url(self) -> str:
        return self.active_model.base_url

    @property
    def api_key(self) -> str | None:
        return self.active_model.api_key

    @property
    def model(self) -> str | None:
        return self.active_model.model

    @property
    def timeout(self) -> float:
        return self.active_model.timeout

    def snapshot(self) -> EngineConfigSnapshot:
        active = self.active_model
        return EngineConfigSnapshot(
            active_model_config_id=active.config_id,
            provider=active.provider,
            model=active.model,
            base_url=active.base_url,
            timeout=active.timeout,
            api_key_masked=active.masked_api_key(),
            configurations=[
                {
                    "id": config.config_id,
                    "name": config.name,
                    "provider": config.provider,
                    "model": config.model,
                    "base_url": config.base_url,
                    "timeout": config.timeout,
                    "enabled": config.enabled,
                    "api_key_masked": config.masked_api_key(),
                }
                for config in self.configurations
            ],
        )

    @classmethod
    def from_env(cls) -> "EngineConfig":
        provider = str(os.environ.get("LLM_PROVIDER") or DEFAULT_PROVIDER).strip().lower()
        base_url = str(os.environ.get("LLM_BASE_URL") or os.environ.get("HERMES_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        api_key = os.environ.get("LLM_API_KEY") or os.environ.get("HERMES_API_KEY")
        model = os.environ.get("LLM_MODEL")
        timeout = float(os.environ.get("LLM_TIMEOUT") or DEFAULT_TIMEOUT)
        return cls(
            active_model_config_id="default",
            configurations=(
                ModelConfiguration(
                    provider=provider,
                    base_url=base_url,
                    api_key=api_key,
                    model=model,
                    timeout=timeout,
                    enabled=True,
                    name="default",
                    config_id="default",
                ),
            ),
        )

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None = None) -> "EngineConfig":
        data = dict(payload or {})
        configs_raw = data.get("model_configurations") or data.get("configurations") or []
        active_id = str(data.get("active_model_config_id") or data.get("active_model_id") or "default")
        configurations: list[ModelConfiguration] = []

        if isinstance(configs_raw, list):
            for index, item in enumerate(configs_raw):
                if not isinstance(item, dict):
                    continue
                provider = str(item.get("provider") or data.get("llm_provider") or DEFAULT_PROVIDER).strip().lower()
                base_url = str(item.get("base_url") or data.get("llm_base_url") or DEFAULT_BASE_URL).rstrip("/")
                timeout = float(item.get("timeout") or data.get("llm_timeout") or DEFAULT_TIMEOUT)
                configurations.append(
                    ModelConfiguration(
                        provider=provider,
                        model=_as_optional_string(item.get("model")),
                        base_url=base_url,
                        api_key=_as_optional_string(item.get("api_key")),
                        timeout=timeout,
                        enabled=bool(item.get("enabled", True)),
                        name=str(item.get("name") or f"config-{index + 1}"),
                        config_id=str(item.get("id") or f"config-{index + 1}"),
                    )
                )

        if not configurations:
            provider_config = dict(data.get("llm_provider_config") or {})
            provider = str(data.get("llm_provider") or DEFAULT_PROVIDER).strip().lower()
            base_url = str(provider_config.get("base_url") or data.get("llm_base_url") or DEFAULT_BASE_URL).rstrip("/")
            api_key = provider_config.get("api_key") or data.get("llm_api_key")
            model = provider_config.get("model") or data.get("llm_model")
            timeout = float(provider_config.get("timeout") or data.get("llm_timeout") or DEFAULT_TIMEOUT)
            configurations = [
                ModelConfiguration(
                    provider=provider,
                    model=_as_optional_string(model),
                    base_url=base_url,
                    api_key=_as_optional_string(api_key),
                    timeout=timeout,
                    enabled=True,
                    name="default",
                    config_id="default",
                )
            ]
            active_id = "default"

        return cls(active_model_config_id=active_id, configurations=tuple(configurations))


def _as_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
