"""
Base TTS provider interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseTTSProvider(ABC):
    """Base class for TTS providers."""

    @abstractmethod
    def load(self, model: str, device: str = "cpu", **kwargs) -> None:
        """
        Load model into memory/VRAM.

        Args:
            model: Model name/path
            device: "cpu" or "cuda"
        """
        ...

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice_id: str | None = None,
        output_path: Path | None = None,
    ) -> bytes:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            voice_id: Optional voice/speaker ID
            output_path: Optional path to save audio file

        Returns:
            Raw audio bytes (WAV format)
        """
        ...

    @abstractmethod
    def unload(self) -> None:
        """Unload model from memory to free VRAM."""
        ...

    @abstractmethod
    def list_voices(self) -> list[str]:
        """List available voices/speakers."""
        ...

    @abstractmethod
    def register_voice(
        self,
        voice_id: str,
        audio_path: str | Path,
        transcript: str,
    ) -> None:
        """
        Register a reference voice for cloning.

        Args:
            voice_id: Unique identifier for this voice
            audio_path: Path to reference audio file
            transcript: Text spoken in the reference audio
        """
        ...
