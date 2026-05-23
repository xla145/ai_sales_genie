import asyncio
import json
import urllib.error
import urllib.request

from agent_runner.config import settings


class HermesService:
    async def plan(self, message: str) -> dict:
        payload = {
            "model": "",
            "input": message,
        }

        def _request() -> dict:
            req = urllib.request.Request(
                f"{settings.hermes_base_url.rstrip('/')}/v1/responses",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {settings.hermes_api_key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read().decode("utf-8")
                if not raw:
                    return {}
                return json.loads(raw)

        try:
            data = await asyncio.to_thread(_request)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Hermes HTTP {exc.code}: {body}") from exc

        patch_text = ""
        output_text = data.get("output_text")
        if isinstance(output_text, str):
            patch_text = output_text
        elif isinstance(data.get("output"), list):
            parts: list[str] = []
            for item in data["output"]:
                if not isinstance(item, dict):
                    continue
                for content in item.get("content", []):
                    if isinstance(content, dict) and isinstance(content.get("text"), str):
                        parts.append(content["text"])
            patch_text = "\n".join(parts)

        return {
            "raw": data,
            "patch": patch_text,
        }
