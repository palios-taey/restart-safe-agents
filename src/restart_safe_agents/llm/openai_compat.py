from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger("restart_safe_agents.llm")


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_calls: int = 0
    total_latency_ms: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class OpenAILLMClient:
    def __init__(
        self,
        api_url: str,
        model: str,
        timeout: float = 120.0,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        self.api_url = api_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = httpx.AsyncClient(timeout=timeout)
        self.usage = TokenUsage()

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": self.max_tokens if max_tokens is None else max_tokens,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        if tools:
            payload["tools"] = tools

        start = time.monotonic()
        response = await self._client.post(f"{self.api_url}/chat/completions", json=payload)
        response.raise_for_status()
        elapsed_ms = (time.monotonic() - start) * 1000
        data = response.json()
        usage = data.get("usage", {})
        self.usage.prompt_tokens += usage.get("prompt_tokens", 0)
        self.usage.completion_tokens += usage.get("completion_tokens", 0)
        self.usage.total_calls += 1
        self.usage.total_latency_ms += elapsed_ms
        logger.info(
            "LLM: %d+%d tokens in %.0fms",
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
            elapsed_ms,
        )
        return data

    async def chat_text(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        data = await self.chat(messages, **kwargs)
        message = data["choices"][0]["message"]
        content = message.get("content")
        if not content:
            content = message.get("reasoning") or message.get("reasoning_content") or ""
        return content

    async def close(self) -> None:
        await self._client.aclose()
