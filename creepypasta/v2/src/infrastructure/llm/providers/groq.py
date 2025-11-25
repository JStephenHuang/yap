"""
Groq LLM provider (API - fast inference).
"""

from langchain_groq import ChatGroq
from langchain_core.language_models import BaseChatModel

from config.base import BaseConfig
from .base import BaseLLMProvider

_config = BaseConfig()

class GroqProvider(BaseLLMProvider):
    """Groq API provider."""

    def create(self, model: str, **kwargs) -> BaseChatModel:
        return ChatGroq(
            model=model,
            temperature=kwargs.get("temperature", 0.7),
            api_key=_config.GROQ_API_KEY,
        )

    def unload(self, model: str) -> None:
        """No-op for API providers."""
        pass
