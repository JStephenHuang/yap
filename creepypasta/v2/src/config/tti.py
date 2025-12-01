"""
TTI configuration for image generation.
"""


class TTIConfig:
    """TTI node configuration."""

    # Provider settings
    PROVIDER: str = "juggernaut"

    # Image dimensions (YouTube landscape)
    WIDTH: int = 1280
    HEIGHT: int = 720

    # Generation settings
    NUM_INFERENCE_STEPS: int = 30
    GUIDANCE_SCALE: float = 7.0

    # Default negative prompt
    NEGATIVE_PROMPT: str = "text, watermark, logo, blurry, low quality, cartoon, anime"


tti_config = TTIConfig()
