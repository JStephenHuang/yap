"""
LangChain-based Ollama provider (local).
"""

import subprocess
from typing import Type, TypeVar

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from .base import BaseLLMProvider

T = TypeVar("T")


class LangchainOllamaProvider(BaseLLMProvider):
    """Local Ollama provider using LangChain."""

    def __init__(self):
        self._model: ChatOllama | None = None
        self._model_name: str | None = None

    def load(self, model: str, **kwargs) -> None:
        self._model_name = model
        self._model = ChatOllama(
            model=model,
            temperature=kwargs.get("temperature", 0.7),
        )

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        if not self._model:
            raise RuntimeError("Model not loaded. Call load() first.")

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        response = self._model.invoke(messages)
        return response.content

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: str | None = None,
        **kwargs,
    ) -> T:
        if not self._model:
            raise RuntimeError("Model not loaded. Call load() first.")

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        structured_llm = self._model.with_structured_output(schema)
        return structured_llm.invoke(messages)

    def unload(self) -> None:
        """Stop model in Ollama server to free VRAM."""
        if self._model_name:
            subprocess.run(["ollama", "stop", self._model_name], capture_output=True)
        self._model = None
        self._model_name = None
