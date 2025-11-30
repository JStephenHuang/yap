"""
LLM provider factory.
"""

from typing import Literal

from .providers.base import BaseLLMProvider
from .providers.langchain_ollama import LangchainOllamaProvider
from .providers.langchain_openai import LangchainOpenAIProvider
from .providers.langchain_groq import LangchainGroqProvider

# Provider class registry
_provider_classes: dict[str, type[BaseLLMProvider]] = {
    "langchain-ollama": LangchainOllamaProvider,
    "langchain-openai": LangchainOpenAIProvider,
    "langchain-groq": LangchainGroqProvider,
}

# Cache for loaded provider instances
_cache: dict[str, BaseLLMProvider] = {}

Provider = Literal["langchain-ollama", "langchain-openai", "langchain-groq"]


def create_llm(provider: Provider, model: str, **kwargs) -> BaseLLMProvider:
    """
    Create/get LLM provider instance.

    Args:
        provider: Provider identifier (e.g., "langchain-ollama", "langchain-groq")
        model: Model name for that provider
        **kwargs: Additional args (temperature, api_key, etc.)

    Returns:
        LLM provider instance (cached)
    """
    cache_key = f"{provider}:{model}"

    if cache_key in _cache:
        return _cache[cache_key]

    if provider not in _provider_classes:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(_provider_classes.keys())}")

    instance = _provider_classes[provider]()
    instance.load(model, **kwargs)
    _cache[cache_key] = instance
    return instance


def unload_llm(provider: Provider, model: str) -> None:
    """Unload a specific LLM model."""
    cache_key = f"{provider}:{model}"
    if cache_key in _cache:
        _cache[cache_key].unload()
        del _cache[cache_key]


def unload_all_llms() -> None:
    """Clear all cached LLM instances."""
    for cache_key in list(_cache.keys()):
        _cache[cache_key].unload()
        del _cache[cache_key]
