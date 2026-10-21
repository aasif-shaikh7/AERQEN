"""Ollama adapter (ADR-005). Uses only the standard library (urllib), no extra package.

Talks to Ollama's HTTP API: ``POST /api/chat`` with native tool calling. The URL and model
come from settings (``AERQEN_OLLAMA_URL`` / ``AERQEN_OLLAMA_MODEL``), so the same code
works with a local Ollama or one on another PC on the LAN.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from integrations.ai.provider import LLMError, LLMProvider, LLMReply, ToolCall


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5:7b",
        timeout: float = 120.0,
        temperature: float = 0.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.name = f"ollama:{model}"

    # ------------------------------------------------------------------ public

    def is_available(self) -> bool:
        try:
            self._request("GET", "/api/version", timeout=3)
            return True
        except LLMError:
            return False

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMReply:
        payload = {
            "model": self.model,
            "stream": False,
            "options": {"temperature": self.temperature},
            "messages": [self._to_ollama_message(m) for m in messages],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"],
                    },
                }
                for t in tools
            ],
        }
        data = self._request("POST", "/api/chat", payload)
        message = data.get("message")
        if not isinstance(message, dict):
            raise LLMError(f"Ollama reply has no 'message': {str(data)[:200]}")

        calls = []
        for raw in message.get("tool_calls") or []:
            fn = (raw or {}).get("function") or {}
            args = fn.get("arguments", {})
            if isinstance(args, str):  # some models return JSON text
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    pass  # leave as str; the tool schema check will reject it
            calls.append(ToolCall(name=str(fn.get("name", "")), arguments=args))
        return LLMReply(content=message.get("content") or "", tool_calls=calls)

    # ----------------------------------------------------------------- helpers

    @staticmethod
    def _to_ollama_message(m: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {"role": m["role"], "content": m.get("content", "")}
        if m.get("tool_calls"):
            out["tool_calls"] = [
                {"function": {"name": c.name, "arguments": c.arguments}} for c in m["tool_calls"]
            ]
        if m.get("tool_name"):
            out["tool_name"] = m["tool_name"]
        return out

    def _request(self, method: str, path: str, payload: Any = None, timeout: float | None = None):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + path,
            data=body,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            raise LLMError(f"Ollama HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise LLMError(f"Cannot reach Ollama at {self.base_url}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise LLMError(f"Ollama returned invalid JSON: {exc}") from exc
