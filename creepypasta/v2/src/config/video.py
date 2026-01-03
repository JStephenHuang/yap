"""
Video generation configuration.
"""

from pathlib import Path


class VideoConfig:
    """Video node configuration."""

    # Timing
    INTRO_DURATION: float = 5.0
    CROSSFADE_DURATION: float = 2.0  # Used for intro fade-in and image crossfades

    # Video settings
    WIDTH: int = 1280
    HEIGHT: int = 720
    FRAMERATE: int = 25

    # Encoding (NVIDIA GPU - hevc_nvenc or h264_nvenc)
    VCODEC: str = "hevc_nvenc"
    ACODEC: str = "aac"
    PIX_FMT: str = "yuv420p"
    
    # NVENC quality preset (p1=fastest, p7=slowest/best quality)
    # p4 is a good balance
    PRESET: str = "p4"

    # Font for title
    FONT_PATH: str = "assets/fonts/FoulFiend.ttf"
    TITLE_FONT_SIZE: int = 32

    # Audio levels
    NARRATION_VOLUME: float = 5.0  # Boost narration (1.0 = original)
    AMBIENT_VOLUME: float = 1.5   # Background ambient level
    AMBIENT_PATH: Path | None = Path("assets/ambient/hanging_garden.mp3")  # Set to None to disable
    AUDIO_END_PADDING : float = 2.0  # Extra audio at end to avoid abrupt cut-off


video_config = VideoConfig()
