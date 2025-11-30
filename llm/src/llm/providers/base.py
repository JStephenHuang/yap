"""
Base LLM provider interface - framework agnostic.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Type

T = TypeVar("T")


class BaseLLMProvider(ABC):
    """
    Base class for LLM providers.

    Framework-agnostic interface. Implementations can use
    LangChain, raw SDKs, or any other backend.
    """

    @abstractmethod
    def load(self, model: str, **kwargs) -> None:
        """
        Load/initialize the model.

        Args:
            model: Model identifier (e.g., "gpt-4", "llama3")
            **kwargs: Provider-specific options (api_key, temperature, etc.)
        """
        ...

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        """
        Generate text completion.

        Args:
            prompt: User prompt/message
            system_prompt: Optional system instructions
            **kwargs: Generation options (temperature, max_tokens, etc.)

        Returns:
            Generated text response
        """
        ...

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: str | None = None,
        **kwargs,
    ) -> T:
        """
        Generate and parse into structured output.

        Args:
            prompt: User prompt/message
            schema: Pydantic model or TypedDict to parse into
            system_prompt: Optional system instructions
            **kwargs: Generation options

        Returns:
            Parsed response matching schema
        """
        ...

    @abstractmethod
    def unload(self) -> None:
        """Unload model from memory to free resources."""
        ...
