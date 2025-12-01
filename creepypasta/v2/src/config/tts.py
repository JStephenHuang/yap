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

    # Available speakers
    SPEAKERS: dict[str, Speaker] = {
        "ghoul": Speaker(
            name="ghoul",
            audio=Path("assets/narrators/ghoul.mp3"),
            transcript="You. You tell the others. Tell them that this is the voice of a serial killer. One so evil that the devil himself... is afraid.",
        ),
        # Add more speakers here:
        # "narrator2": Speaker(
        #     name="narrator2",
        #     audio=Path("assets/narrators/narrator2.wav"),
        #     transcript="The transcript of what narrator2 says in the reference audio.",
        # ),
    }

    # Default speaker for narration
    DEFAULT_SPEAKER: str = "ghoul"


tts_config = TTSConfig()
