from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI


@dataclass(frozen=True)
class LLMDiagnostics:
    env_path: Path
    api_key_present: bool
    model: str
    base_url_configured: bool
    timeout: float | None
    issues: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class LLMConfig:
    api_key: str | None
    model: str
    base_url: str | None = None
    timeout: float = 120.0
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "LLMConfig":
        diagnostics = diagnose_llm_config()
        if diagnostics.issues:
            raise RuntimeError("LLM configuration invalid: " + "; ".join(diagnostics.issues))
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=diagnostics.model,
            base_url=os.getenv("OPENAI_BASE_URL") or None,
            timeout=diagnostics.timeout or 300.0,
            enabled=True,
        )


def diagnose_llm_config() -> LLMDiagnostics:
    env_path = _project_env_path()
    load_dotenv(env_path)
    issues: list[str] = []
    warnings: list[str] = []
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.2")
    timeout_raw = os.getenv("OPENAI_TIMEOUT", "300")
    timeout: float | None
    try:
        timeout = float(timeout_raw)
    except ValueError:
        timeout = None
        issues.append(f"OPENAI_TIMEOUT must be a number, got {timeout_raw!r}")
    if not api_key:
        issues.append(f"OPENAI_API_KEY is required; set it in {env_path}")
    if not env_path.exists():
        warnings.append(f"env file not found: {env_path}")
    return LLMDiagnostics(
        env_path=env_path,
        api_key_present=bool(api_key),
        model=model,
        base_url_configured=bool(os.getenv("OPENAI_BASE_URL")),
        timeout=timeout,
        issues=tuple(issues),
        warnings=tuple(warnings),
    )


def _project_env_path() -> Path:
    return Path(__file__).resolve().parents[2] / ".env"


async def complete_text(config: LLMConfig, system_prompt: str, user_prompt: str) -> str:
    return await _complete_text(config, system_prompt, user_prompt)


async def complete_json(config: LLMConfig, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    json_prompt = f"{user_prompt}\n\n返回值必须是严格 JSON 对象，且顶层必须包含 files 数组。"
    content = await _complete_text(config, system_prompt, json_prompt, json_mode=True)
    payload = _extract_json(content)
    if payload is not None:
        return payload

    repair_prompt = (
        "将下面的模型输出转换为严格 JSON 对象。只返回 JSON，不要解释，不要 Markdown 代码围栏。"
        "格式必须是 {\"files\":[{\"path\":\"相对路径\",\"content\":\"完整文件内容\"}]}。\n\n"
        f"模型输出：\n{content}"
    )
    repaired = await _complete_text(config, system_prompt, repair_prompt, json_mode=True)
    payload = _extract_json(repaired)
    if payload is None:
        raise RuntimeError("OpenAI response did not contain valid JSON")
    return payload


async def _complete_text(config: LLMConfig, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    client = _get_client(config.api_key or "", config.base_url, config.timeout)
    kwargs: dict[str, Any] = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = await client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("OpenAI returned empty content")
    return content


@lru_cache(maxsize=8)
def _get_client(api_key: str, base_url: str | None, timeout: float) -> AsyncOpenAI:
    return AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout)


def _extract_json(content: str) -> dict[str, Any] | None:
    candidates = [content.strip()]
    if "```" in content:
        segments = content.split("```")
        for segment in segments[1::2]:
            stripped = segment.strip()
            if stripped.startswith("json"):
                stripped = stripped[4:].lstrip()
            candidates.append(stripped)
    for candidate in candidates:
        if not candidate:
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None
