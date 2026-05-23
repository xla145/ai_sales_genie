"""Hermes OpenAI 兼容 API 客户端。"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Iterator


@dataclass
class HermesStreamEvent:
    event_type: str
    data: dict[str, Any]
from uuid import uuid4

DEFAULT_BASE_URL = os.environ.get("HERMES_BASE_URL", "http://127.0.0.1:8642")
HERMES_API_KEY = os.environ.get("HERMES_API_KEY", "")


@dataclass
class HermesResponse:
    status: int
    data: Any

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300


def _encode_multipart(
    fields: dict[str, str],
    files: dict[str, tuple[str, BinaryIO, str | None]],
) -> tuple[bytes, str]:
    boundary = f"----hermes-{uuid4().hex}"
    lines: list[bytes] = []

    for name, value in fields.items():
        lines.append(f"--{boundary}\r\n".encode())
        lines.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        lines.append(f"{value}\r\n".encode())

    for name, (filename, stream, content_type) in files.items():
        ctype = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        lines.append(f"--{boundary}\r\n".encode())
        lines.append(
            (
                f'Content-Disposition: form-data; name="{name}"; '
                f'filename="{filename}"\r\n'
                f"Content-Type: {ctype}\r\n\r\n"
            ).encode()
        )
        lines.append(stream.read())
        lines.append(b"\r\n")

    lines.append(f"--{boundary}--\r\n".encode())
    body = b"".join(lines)
    return body, f"multipart/form-data; boundary={boundary}"


def _iter_sse(resp: Any) -> Iterator[dict[str, Any]]:
    for raw_line in resp:
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line or not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            return
        try:
            yield json.loads(payload)
        except json.JSONDecodeError:
            continue


def _extract_delta(chunk: dict[str, Any]) -> str:
    try:
        delta = chunk["choices"][0].get("delta") or {}
        return delta.get("content") or ""
    except (KeyError, IndexError, TypeError):
        return ""


def _extract_response_text(data: dict[str, Any] | None) -> str:
    if not isinstance(data, dict):
        return ""

    output = data.get("output")
    if isinstance(output, list):
        parts: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for entry in content:
                if not isinstance(entry, dict):
                    continue
                text = entry.get("text")
                if isinstance(text, str) and text:
                    parts.append(text)
        if parts:
            return "\n".join(parts)

    text = data.get("output_text")
    if isinstance(text, str):
        return text
    return ""


def _extract_response_delta(event: dict[str, Any]) -> str:
    if not isinstance(event, dict):
        return ""
    if event.get("type") != "response.output_text.delta":
        return ""
    delta = event.get("delta")
    return delta if isinstance(delta, str) else ""


class HermesClient:
    """Hermes API 调用封装，便于后续扩展文件上传。"""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = (base_url or os.environ.get("HERMES_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key if api_key is not None else os.environ.get("HERMES_API_KEY", HERMES_API_KEY)
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _auth_headers(
        self,
        *,
        accept: str = "application/json",
        content_type: str | None = None,
    ) -> dict[str, str]:
        headers = {"Accept": accept}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> HermesResponse:
        req = urllib.request.Request(
            self._url(path),
            data=body,
            headers=headers or self._auth_headers(),
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw) if raw else None
                return HermesResponse(resp.status, data)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                data = json.loads(raw) if raw else {"error": exc.reason}
            except json.JSONDecodeError:
                data = {"raw": raw or exc.reason}
            return HermesResponse(exc.code, data)

    def request_json(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> HermesResponse:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = self._auth_headers(content_type="application/json" if body else None)
        return self._request(method, path, body=data, headers=headers)

    def request_multipart(
        self,
        method: str,
        path: str,
        fields: dict[str, str],
        files: dict[str, tuple[str, BinaryIO, str | None]],
    ) -> HermesResponse:
        body, content_type = _encode_multipart(fields, files)
        headers = self._auth_headers(content_type=content_type)
        return self._request(method, path, body=body, headers=headers)

    def list_models(self) -> HermesResponse:
        return self.request_json("GET", "/v1/models")

    def model_ids(self) -> list[str]:
        resp = self.list_models()
        if not resp.ok:
            return []
        return [m["id"] for m in resp.data.get("data", []) if m.get("id")]

    def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> HermesResponse:
        body: dict[str, Any] = {
            "model": model or self._default_model(),
            "messages": messages,
            "stream": stream,
            **kwargs,
        }
        return self.request_json("POST", "/v1/chat/completions", body)

    def response(
        self,
        input_text: str,
        *,
        model: str | None = None,
        conversation: str | None = None,
        **kwargs: Any,
    ) -> HermesResponse:
        body: dict[str, Any] = {
            "model": model or self._default_model(),
            "input": input_text,
            **kwargs,
        }
        if conversation:
            body["conversation"] = conversation
        return self.request_json("POST", "/v1/responses", body)

    def response_stream(
        self,
        input_text: str,
        *,
        model: str | None = None,
        conversation: str | None = None,
        **kwargs: Any,
    ) -> Iterator[HermesStreamEvent]:
        body: dict[str, Any] = {
            "model": model or self._default_model(),
            "input": input_text,
            "stream": True,
            **kwargs,
        }
        if conversation:
            body["conversation"] = conversation

        headers = self._auth_headers(
            accept="text/event-stream",
            content_type="application/json",
        )
        req = urllib.request.Request(
            self._url("/v1/responses"),
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                for chunk in _iter_sse(resp):
                    event_type = chunk.get("type") if isinstance(chunk, dict) else None
                    if isinstance(event_type, str) and event_type:
                        yield HermesStreamEvent(event_type=event_type, data=chunk)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            detail = raw.strip() or exc.reason
            raise RuntimeError(f"Hermes responses stream failed with HTTP {exc.code}: {detail}") from exc

    def response_text(
        self,
        input_text: str,
        *,
        model: str | None = None,
        conversation: str | None = None,
        **kwargs: Any,
    ) -> tuple[HermesResponse, str]:
        resp = self.response(
            input_text,
            model=model,
            conversation=conversation,
            **kwargs,
        )
        return resp, _extract_response_text(resp.data)

    def response_text_stream(
        self,
        input_text: str,
        *,
        model: str | None = None,
        conversation: str | None = None,
        **kwargs: Any,
    ) -> tuple[HermesResponse, str]:
        final_event: dict[str, Any] | None = None
        parts: list[str] = []
        for event in self.response_stream(
            input_text,
            model=model,
            conversation=conversation,
            **kwargs,
        ):
            delta = _extract_response_delta(event.data)
            if delta:
                parts.append(delta)
            if event.event_type == "response.completed":
                final_event = event.data

        if final_event is None:
            raise RuntimeError("Hermes streaming response ended before response.completed")

        response_data = final_event.get("response")
        if not isinstance(response_data, dict):
            raise RuntimeError("Hermes response.completed missing response payload")

        content = "".join(parts).strip() or _extract_response_text(response_data)
        return HermesResponse(200, response_data), content

    def chat_stream(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        body: dict[str, Any] = {
            "model": model or self._default_model(),
            "messages": messages,
            "stream": True,
            **kwargs,
        }
        headers = self._auth_headers(
            accept="text/event-stream",
            content_type="application/json",
        )
        req = urllib.request.Request(
            self._url("/v1/chat/completions"),
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            for chunk in _iter_sse(resp):
                text = _extract_delta(chunk)
                if text:
                    yield text

    def _default_model(self) -> str:
        ids = self.model_ids()
        if not ids:
            raise RuntimeError("No model available from /v1/models")
        return ids[0]

    def upload_file(
        self,
        file_path: str | Path,
        *,
        purpose: str = "assistants",
    ) -> HermesResponse:
        path = Path(file_path)
        with path.open("rb") as f:
            return self.request_multipart(
                "POST",
                "/v1/files",
                fields={"purpose": purpose},
                files={"file": (path.name, f, mimetypes.guess_type(path.name)[0])},
            )

    def list_files(self) -> HermesResponse:
        return self.request_json("GET", "/v1/files")

    def get_file(self, file_id: str) -> HermesResponse:
        return self.request_json("GET", f"/v1/files/{file_id}")

    def delete_file(self, file_id: str) -> HermesResponse:
        return self.request_json("DELETE", f"/v1/files/{file_id}")

    @staticmethod
    def text_message(role: str, text: str) -> dict[str, Any]:
        return {"role": role, "content": text}

    @staticmethod
    def user_message_with_files(
        text: str,
        *,
        file_ids: list[str] | None = None,
        image_paths: list[str | Path] | None = None,
    ) -> dict[str, Any]:
        parts: list[dict[str, Any]] = [{"type": "text", "text": text}]

        for fid in file_ids or []:
            parts.append({"type": "file", "file": {"file_id": fid}})

        for img_path in image_paths or []:
            path = Path(img_path)
            mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
            b64 = base64.b64encode(path.read_bytes()).decode("ascii")
            parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                }
            )

        if len(parts) == 1:
            return {"role": "user", "content": text}
        return {"role": "user", "content": parts}
