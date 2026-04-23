from typing import Any

import httpx

from app.llm.base import LLMMessage, LLMResponse


class OpenAICompatibleProvider:
    """Adapter for OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        provider_name: str,
        model_name: str,
        api_key: str | None,
        base_url: str,
        timeout_seconds: float,
        temperature: float,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        if not api_key:
            raise RuntimeError(f"{provider_name} API key is not configured.")

        self._provider_name = provider_name
        self._model_name = model_name
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._temperature = temperature
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if default_headers:
            self._headers.update(default_headers)

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(self, messages: list[LLMMessage]) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self._model_name,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "temperature": self._temperature,
        }
        with httpx.Client(timeout=self._timeout_seconds) as client:
            response = client.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage") or {}
        return LLMResponse(
            content=choice,
            model=data.get("model", self._model_name),
            provider=self._provider_name,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
        )

