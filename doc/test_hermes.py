#!/usr/bin/env python3
"""Hermes 接口测试入口。"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
from uuid import uuid4

from app.clients.hermes_client import DEFAULT_BASE_URL, HERMES_API_KEY, HermesClient, HermesStreamEvent

DEFAULT_BASE_URL = "http://127.0.0.1:8643"
HERMES_API_KEY = "fiskzcVqn3frVcd"

def print_result(name: str, ok: bool, detail: str) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}")
    if detail:
        print(detail.rstrip())
    print()


def fmt_response(resp) -> str:
    return json.dumps(resp.data, ensure_ascii=False, indent=2)


def _response_delta(event: HermesStreamEvent) -> str:
    if event.event_type != "response.output_text.delta":
        return ""
    delta = event.data.get("delta")
    return delta if isinstance(delta, str) else ""


def test_models(client: HermesClient) -> tuple[bool, list[str]]:
    resp = client.list_models()
    if not resp.ok:
        print_result("GET /v1/models", False, f"HTTP {resp.status}\n{fmt_response(resp)}")
        return False, []

    models = client.model_ids()
    print_result(
        "GET /v1/models",
        True,
        f"HTTP {resp.status}, models={len(models)}\n"
        + "\n".join(f"  - {m}" for m in models),
    )
    return True, models


def test_chat_stream(client: HermesClient, model: str, prompt: str) -> bool:
    print(f"[RUN ] POST /v1/chat/completions ({model}) [stream]")
    print("assistant: ", end="", flush=True)

    parts: list[str] = []
    try:
        for text in client.chat_stream(
            [HermesClient.text_message("user", prompt)],
            model=model,
            max_tokens=256,
            temperature=0.7,
        ):
            print(text, end="", flush=True)
            parts.append(text)
    except urllib.error.HTTPError as exc:
        print()
        print_result(
            f"POST /v1/chat/completions ({model}) [stream]",
            False,
            f"HTTP {exc.code}",
        )
        return False
    except Exception as exc:
        print()
        print_result(
            f"POST /v1/chat/completions ({model}) [stream]",
            False,
            str(exc),
        )
        return False

    print()
    full = "".join(parts)
    print_result(
        f"POST /v1/chat/completions ({model}) [stream]",
        bool(full.strip()),
        f"chars={len(full)}",
    )
    return bool(full.strip())


def test_chat(client: HermesClient, model: str, prompt: str) -> bool:
    resp = client.chat(
        [HermesClient.text_message("user", prompt)],
        model=model,
        max_tokens=16,
        temperature=0,
        stream=False,
    )
    if not resp.ok:
        print_result(
            f"POST /v1/chat/completions ({model})",
            False,
            f"HTTP {resp.status}\n{fmt_response(resp)}",
        )
        return False

    try:
        content = resp.data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        print_result(
            f"POST /v1/chat/completions ({model})",
            False,
            f"Unexpected response:\n{fmt_response(resp)}",
        )
        return False

    print_result(
        f"POST /v1/chat/completions ({model})",
        True,
        f"HTTP {resp.status}\nassistant: {content!r}",
    )
    return True


def test_upload(client: HermesClient, file_path: str) -> bool:
    print(f"[RUN ] POST /v1/files ({file_path})")
    resp = client.upload_file(file_path)
    if not resp.ok:
        print_result(
            "POST /v1/files",
            False,
            f"HTTP {resp.status}\n{fmt_response(resp)}",
        )
        return False

    file_id = resp.data.get("id", "")
    print_result(
        "POST /v1/files",
        True,
        f"HTTP {resp.status}\nfile_id={file_id!r}\n{fmt_response(resp)}",
    )
    return True


def _stream_response_turn(
    client: HermesClient,
    *,
    model: str,
    prompt: str,
    conversation: str | None,
    max_tokens: int,
    temperature: float,
) -> str:
    print("assistant: ", end="", flush=True)
    parts: list[str] = []
    for event in client.response_stream(
        prompt,
        model=model,
        conversation=conversation,
        max_tokens=max_tokens,
        temperature=temperature,
    ):
        delta = _response_delta(event)
        if delta:
            print(delta, end="", flush=True)
            parts.append(delta)
    print()
    return "".join(parts)


def _stream_chat_turn(
    client: HermesClient,
    *,
    model: str,
    messages: list[dict],
    max_tokens: int,
    temperature: float,
) -> str:
    print("assistant: ", end="", flush=True)
    parts: list[str] = []
    for text in client.chat_stream(
        messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    ):
        print(text, end="", flush=True)
        parts.append(text)
    print()
    return "".join(parts)


def run_interactive(
    client: HermesClient,
    model: str,
    *,
    api: str,
    conversation: str,
    max_tokens: int,
    temperature: float,
) -> int:
    use_responses = api == "responses"
    conversation_id = conversation
    messages: list[dict] = []

    api_label = "/v1/responses" if use_responses else "/v1/chat/completions"
    print(f"Multi-turn mode ({api_label})")
    print(f"model={model}")
    if use_responses:
        print(f"conversation={conversation_id}")
    print("Commands: /exit /quit /q to quit, /clear to reset context\n")

    turn = 0
    while True:
        try:
            user_input = input("user: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0

        if not user_input:
            continue

        lowered = user_input.lower()
        if lowered in {"/exit", "/quit", "/q", "exit", "quit"}:
            print("Bye.")
            return 0

        if lowered == "/clear":
            if use_responses:
                conversation_id = f"conv-{uuid4().hex[:12]}"
                print(f"Context cleared. conversation={conversation_id}\n")
            else:
                messages.clear()
                print("Context cleared.\n")
            continue

        turn += 1
        print(f"[turn {turn}] ", end="")

        try:
            if use_responses:
                assistant_text = _stream_response_turn(
                    client,
                    model=model,
                    prompt=user_input,
                    conversation=conversation_id,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            else:
                messages.append(HermesClient.text_message("user", user_input))
                assistant_text = _stream_chat_turn(
                    client,
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                if assistant_text.strip():
                    messages.append(HermesClient.text_message("assistant", assistant_text))
        except Exception as exc:
            print(f"\n[ERROR] {exc}\n")
            if not use_responses and messages and messages[-1].get("role") == "user":
                messages.pop()
            continue

        if not assistant_text.strip():
            print("[WARN] empty assistant response\n")
        else:
            print()

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Hermes OpenAI-compatible API")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("HERMES_BASE_URL", DEFAULT_BASE_URL),
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("HERMES_API_KEY", HERMES_API_KEY),
    )
    parser.add_argument("--model", default=os.environ.get("HERMES_MODEL"))
    parser.add_argument("--prompt", default="用一句话介绍你自己")
    parser.add_argument("--skip-chat", action="store_true")
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="进入多轮对话模式（默认使用 /v1/responses + conversation）",
    )
    parser.add_argument(
        "--api",
        choices=("responses", "chat"),
        default="responses",
        help="多轮对话使用的 API（默认 responses）",
    )
    parser.add_argument(
        "--conversation",
        default=None,
        help="多轮会话 ID（仅 responses API；默认自动生成）",
    )
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument(
        "--upload",
        metavar="FILE",
        help="上传文件到 /v1/files（服务端支持后可用）",
    )
    parser.add_argument(
        "--upload-only",
        action="store_true",
        help="仅测试文件上传，跳过 models/chat",
    )
    args = parser.parse_args()

    client = HermesClient(base_url=args.base_url, api_key=args.api_key)

    print(f"Base URL: {client.base_url}")
    print(f"API key: {'(set)' if client.api_key else '(missing)'}\n")

    if args.upload_only:
        if not args.upload:
            print("Error: --upload-only requires --upload FILE")
            return 1
        return 0 if test_upload(client, args.upload) else 1

    ok, models = test_models(client)
    if not ok:
        return 1

    if args.upload:
        test_upload(client, args.upload)

    if args.skip_chat:
        return 0

    model = args.model or (models[0] if models else None)
    if not model:
        print_result("POST /v1/chat/completions", False, "No model available.")
        return 1

    if args.interactive:
        conversation = args.conversation or f"conv-{uuid4().hex[:12]}"
        return run_interactive(
            client,
            model,
            api=args.api,
            conversation=conversation,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )

    if args.no_stream:
        return 0 if test_chat(client, model, args.prompt) else 1
    return 0 if test_chat_stream(client, model, args.prompt) else 1


if __name__ == "__main__":
    sys.exit(main())
