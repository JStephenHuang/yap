"""
LLM provider factory.
"""

from typing import Literal, Type, TypeVar
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable

from .providers import OllamaProvider, OpenAIProvider, GroqProvider, BaseLLMProvider

T = TypeVar("T")

# Provider registry
_providers: dict[str, BaseLLMProvider] = {
    "ollama": OllamaProvider(),
    "openai": OpenAIProvider(),
    "groq": GroqProvider(),
}

# Cache for loaded models
_cache: dict[str, BaseChatModel] = {}

Provider = Literal["ollama", "openai", "groq"]


def create_llm(provider: Provider, model: str, **kwargs) -> BaseChatModel:
    """
    Create LLM client for specified provider and model.

    Args:
        provider: "ollama" (local), "anthropic", "openai", or "groq"
        model: Model name for that provider
        **kwargs: Additional args (temperature, etc.)

    Returns:
        LangChain chat model instance
    """
    cache_key = f"{provider}:{model}"

    if cache_key in _cache:
        return _cache[cache_key]

    if provider not in _providers:
        raise ValueError(f"Unknown provider: {provider}")

    llm = _providers[provider].create(model, **kwargs)
    _cache[cache_key] = llm
    return llm


def create_structured_llm(
    provider: Provider,
    model: str,
    schema: Type[T],
    **kwargs,
) -> Runnable:
    """
    Create LLM with structured output for specified schema.

    Args:
        provider: "ollama", "openai", or "groq"
        model: Model name for that provider
        schema: TypedDict or Pydantic model for structured output
        **kwargs: Additional args (temperature, etc.)

    Returns:
        LangChain runnable that outputs structured data
    """
    base_llm = create_llm(provider, model, **kwargs)
    return base_llm.with_structured_output(schema)


def unload_llm(provider: Provider, model: str | None = None) -> None:
    """
    Unload LLM to free resources.

    Args:
        provider: Provider to unload from
        model: Specific model to unload (None = all for provider)
    """
    if model:
        _providers[provider].unload(model)
        cache_key = f"{provider}:{model}"
        _cache.pop(cache_key, None)
    else:
        # Unload all for this provider
        keys_to_remove = [k for k in _cache if k.startswith(provider)]
        for key in keys_to_remove:
            model_name = key.split(":")[1]
            _providers[provider].unload(model_name)
            del _cache[key]
