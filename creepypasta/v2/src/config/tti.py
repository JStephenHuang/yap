"""
TTI configuration for image generation.
"""


class TTIConfig:
    """TTI node configuration."""

    # Provider settings
    PROVIDER: str = "juggernaut"
    DEVICE: str = "cuda"

    # Model precision (float16 = faster, float32 = slightly more precise)
    TORCH_DTYPE: str = "float16"

    # Image dimensions (YouTube landscape)
    WIDTH: int = 1280
    HEIGHT: int = 720

    # Generation settings
    NUM_INFERENCE_STEPS: int = 25
    GUIDANCE_SCALE: float = 7.0

    # Default negative prompt
    NEGATIVE_PROMPT: str = "text, watermark, logo, blurry, low quality, cartoon, anime, nsfw, 18+"


tti_config = TTIConfig()
