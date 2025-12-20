"""
Video generation configuration.
"""


class VideoConfig:
    """Video node configuration."""

    # Timing
    INTRO_DURATION: float = 5.0
    CROSSFADE_DURATION: float = 2.0

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
    CREDIT_FONT_SIZE: int = 16


video_config = VideoConfig()
