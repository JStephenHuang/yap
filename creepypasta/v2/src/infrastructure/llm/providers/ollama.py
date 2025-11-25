"""
Ollama LLM provider (local).
"""

import subprocess
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel

from .base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Local Ollama provider."""

    def create(self, model: str, **kwargs) -> BaseChatModel:
        return ChatOllama(
            model=model,
            temperature=kwargs.get("temperature", 0.7),
        )

    def unload(self, model: str) -> None:
        """Stop model in Ollama server to free VRAM."""
        subprocess.run(["ollama", "stop", model], capture_output=True)
