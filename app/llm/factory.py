from app.core.config import Settings
from app.llm.base import LLMProvider
from app.llm.mock import MockLLMProvider
from app.llm.openai_compatible import OpenAICompatibleProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "mock":
        return MockLLMProvider()
    if provider == "openrouter":
        headers = {"HTTP-Referer": settings.openrouter_site_url or "", "X-Title": settings.openrouter_app_name}
        return OpenAICompatibleProvider(
            provider_name="openrouter",
            model_name=settings.llm_model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
            temperature=settings.llm_temperature,
            default_headers={key: value for key, value in headers.items() if value},
        )
    if provider == "openai":
        return OpenAICompatibleProvider(
            provider_name="openai",
            model_name=settings.llm_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
            temperature=settings.llm_temperature,
        )
    if provider == "groq":
        return OpenAICompatibleProvider(
            provider_name="groq",
            model_name=settings.llm_model,
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
            temperature=settings.llm_temperature,
        )
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

