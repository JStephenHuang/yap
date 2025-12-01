"""
Base TTI provider interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image


class BaseTTIProvider(ABC):
    """Base class for TTI (text-to-image) providers."""

    @abstractmethod
    def load(self, model: str, **kwargs) -> None:
        """Load model into VRAM."""
        ...

    @abstractmethod
    def generate(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        width: int = 1280,
        height: int = 720,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.0,
        seed: int | None = None,
        output_path: Path | None = None,
    ) -> Image.Image:
        """Generate an image from a text prompt."""
        ...

    @abstractmethod
    def unload(self) -> None:
        """Unload model to free VRAM."""
        ...
