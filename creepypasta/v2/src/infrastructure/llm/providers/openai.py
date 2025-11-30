"""
OpenAI LLM provider (API).
"""

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""

    def create(self, model: str, **kwargs) -> BaseChatModel:
        return ChatOpenAI(
            model=model,
            temperature=kwargs.get("temperature", 0.7),
        )

    def unload(self, model: str) -> None:
        """No-op for API providers."""
        pass
