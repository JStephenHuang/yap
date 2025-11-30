"""
LangChain-based Groq provider (API - fast inference).
"""

import os
from typing import Type, TypeVar

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from .base import BaseLLMProvider

T = TypeVar("T")


class LangchainGroqProvider(BaseLLMProvider):
    """Groq API provider using LangChain."""

    def __init__(self):
        self._model: ChatGroq | None = None

    def load(self, model: str, **kwargs) -> None:
        self._model = ChatGroq(
            model=model,
            temperature=kwargs.get("temperature", 0.7),
            api_key=kwargs.get("api_key") or os.environ.get("GROQ_API_KEY"),
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
        """No-op for API providers."""
        self._model = None
