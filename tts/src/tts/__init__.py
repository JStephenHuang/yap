"""
Shared TTS package with pluggable providers.
"""

from .factory import create_tts, unload_tts, unload_all_tts
from .providers.base import BaseTTSProvider
from .providers.neutts import NeuTTSProvider

__all__ = [
    "create_tts",
    "unload_tts",
    "unload_all_tts",
    "BaseTTSProvider",
    "NeuTTSProvider",
]
