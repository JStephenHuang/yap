"""
Base LLM provider interface.
"""

import typing
from langchain_core.language_models import BaseChatModel


class BaseLLMProvider(typing.Protocol):
    """Base class for LLM providers."""

    def create(self, model: str, **kwargs) -> BaseChatModel:...
    def unload(self, model: str) -> None:...
