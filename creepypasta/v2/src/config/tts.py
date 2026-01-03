"""
TTS configuration with speaker definitions.
"""

from pathlib import Path
from dataclasses import dataclass


@dataclass
class Speaker:
    """Voice reference for TTS cloning."""
    name: str
    audio: Path
    transcript: str


class TTSConfig:
    """TTS node configuration."""

    # Provider settings
    PROVIDER: str = "neutts"
    MODEL: str = "neuphonic/neutts-air"
    DEVICE: str = "cuda"

    # Output settings
    SAMPLE_RATE: int = 24000

    # Chunking settings
    CHUNK_BY_SENTENCE: bool = True  # If True, chunks by sentence; if False, chunks by max chars
    MAX_CHUNK_SENTENCES: int = 2     # Max sentences per chunk (only used if CHUNK_BY_SENTENCE=True)
    MAX_CHUNK_CHARS: int = 250  # Max chars per chunk (only used if CHUNK_BY_SENTENCE=False)

    # Concatenation settings
    SILENCE_PADDING_MS: int = 300  # Silence between chunks in milliseconds

    # Available speakers
    SPEAKERS: dict[str, Speaker] = {
        "ghoul": Speaker(
            name="ghoul",
            audio=Path("assets/narrators/ghoul.mp3"),
            transcript="You. You tell the others. Tell them that this is the voice of a serial killer. One so evil that the devil himself... is afraid.",
        ),
        # Add more speakers here:
        "stephen_1": Speaker(
            name="stephen_1",
            audio=Path("assets/narrators/stephen_1.mp3"),
            transcript="I think something is inside of me. I woke up to a puff of smoke and instinctively clawed at my throat to pull out whatever was snaking its way down to my stomach, to no avail. As a desperate act I attempted to make myself gag and throw up whatever creature crawled into me but that once again was met with failure.",
        ),
        "stephen_2": Speaker(
            name="stephen_2",
            audio=Path("assets/narrators/stephen_2.mp3"),
            transcript="I woke up to the sound of breathing beside my bed, slow and wet, even though I live alone.",
        ),
    }

    # Default speaker for narration
    DEFAULT_SPEAKER: str = "stephen_1"


tts_config = TTSConfig()
