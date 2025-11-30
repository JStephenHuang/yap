"""
Base LLM provider interface.
"""

from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def create(self, model: str, **kwargs) -> BaseChatModel:
        """Create and return an LLM instance."""
        ...

    @abstractmethod
    def unload(self, model: str) -> None:
        """Unload model from memory (no-op for API providers)."""
        ...
