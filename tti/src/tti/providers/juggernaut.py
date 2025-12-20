"""
Juggernaut XI provider - CUDA only.
"""

import gc
import logging
from pathlib import Path

import torch
from diffusers import StableDiffusionXLPipeline
from huggingface_hub import hf_hub_download
from PIL import Image

from tti.providers.base import BaseTTIProvider

logger = logging.getLogger(__name__)

MODEL_REPO = "RunDiffusion/Juggernaut-XI-v11"
MODEL_FILE = "Juggernaut-XI-byRunDiffusion.safetensors"


class JuggernautProvider(BaseTTIProvider):
    """Juggernaut XI image generation (CUDA only)."""

    def __init__(self):
        self._pipe: StableDiffusionXLPipeline | None = None

    def load(self, model: str = MODEL_REPO, **kwargs) -> None:
        """Load Juggernaut XI on CUDA with configurable precision."""
        device = kwargs.get("device", "cuda")
        torch_dtype_str = kwargs.get("torch_dtype", "float16")
        torch_dtype = torch.float16 if torch_dtype_str == "float16" else torch.float32

        logger.info(f"Downloading: {MODEL_FILE}")
        local_path = hf_hub_download(repo_id=model, filename=MODEL_FILE)

        logger.info(f"Loading Juggernaut XI on {device} ({torch_dtype_str})...")
        self._pipe = StableDiffusionXLPipeline.from_single_file(
            local_path,
            torch_dtype=torch_dtype,
            use_safetensors=True,
        ).to(device)

        self._pipe.enable_attention_slicing()
        self._pipe.vae.enable_slicing()
        self._pipe.vae.enable_tiling()  # Helps with large images
        logger.info("Model loaded")

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
        if self._pipe is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        generator = None
        if seed is not None:
            generator = torch.Generator(device="cuda").manual_seed(seed)

        logger.info(f"Generating: {width}x{height}, steps={num_inference_steps}")

        result = self._pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator,
        )

        image = result.images[0]

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(str(output_path))
            logger.info(f"Saved to {output_path}")

        return image

    def unload(self) -> None:
        """Unload model to free VRAM."""
        self._pipe = None
        gc.collect()
        torch.cuda.empty_cache()
        logger.info("Model unloaded")
