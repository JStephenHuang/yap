"""
TTS provider factory.
"""

from typing import Literal
from pathlib import Path

from .providers.base import BaseTTSProvider
from .providers.neutts import NeuTTSProvider

# Provider registry
_providers: dict[str, type[BaseTTSProvider]] = {
    "neutts": NeuTTSProvider,
}

# Cache for loaded provider instances
_cache: dict[str, BaseTTSProvider] = {}

Provider = Literal["neutts", "styletts"]


def register_provider(name: str, provider_class: type[BaseTTSProvider]) -> None:
    """Register a TTS provider."""
    _providers[name] = provider_class


def create_tts(provider: Provider, model: str, **kwargs) -> BaseTTSProvider:
    """
    Create/get TTS provider instance.

    Args:
        provider: "neutts" or "styletts"
        model: Model name/path for that provider
        **kwargs: Additional args (device, etc.)

    Returns:
        TTS provider instance (cached)
    """
    cache_key = f"{provider}:{model}"

    if cache_key in _cache:
        return _cache[cache_key]

    if provider not in _providers:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(_providers.keys())}")

    instance = _providers[provider]()
    instance.load(model, **kwargs)
    _cache[cache_key] = instance
    return instance

def unload_tts(provider: Provider, model: str) -> None:
    """Unload a specific TTS model to free VRAM."""
    cache_key = f"{provider}:{model}"
    if cache_key in _cache:
        _cache[cache_key].unload()
        del _cache[cache_key]


def unload_all_tts() -> None:
    """Unload all cached TTS instances to free VRAM."""
    for cache_key in list(_cache.keys()):
        _cache[cache_key].unload()
        del _cache[cache_key]
