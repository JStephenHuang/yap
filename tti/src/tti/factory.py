"""
TTI provider factory.
"""

from typing import Literal

from .providers.base import BaseTTIProvider
from .providers.juggernaut import JuggernautProvider

_providers: dict[str, type[BaseTTIProvider]] = {
    "juggernaut": JuggernautProvider,
}

_cache: dict[str, BaseTTIProvider] = {}

Provider = Literal["juggernaut"]


def create_tti(provider: Provider, **kwargs) -> BaseTTIProvider:
    """
    Create/get TTI provider instance.

    Args:
        provider: "juggernaut" (more can be added)
        **kwargs: Provider-specific args

    Returns:
        TTI provider instance (cached)
    """
    if provider in _cache:
        return _cache[provider]

    if provider not in _providers:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(_providers.keys())}")

    instance = _providers[provider]()
    instance.load(**kwargs)
    _cache[provider] = instance
    return instance


def unload_tti(provider: Provider) -> None:
    """Unload a specific TTI provider to free VRAM."""
    if provider in _cache:
        _cache[provider].unload()
        del _cache[provider]


def unload_all_tti() -> None:
    """Unload all cached TTI instances to free VRAM."""
    for key in list(_cache.keys()):
        _cache[key].unload()
        del _cache[key]
