from __future__ import annotations

from typing import Any, Protocol


class LLMClientProtocol(Protocol):
    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]: ...

    async def chat_text(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str: ...

    async def close(self) -> None: ...
