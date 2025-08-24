from pathlib import Path
import logging
import torch

import pandas as pd
from google import genai
from google.genai import types

from diffusers import DiffusionPipeline, StableDiffusionXLPipeline
from huggingface_hub import hf_hub_download

from creepypastas.config import Settings
from creepypastas.utils import find_thread, save

logger = logging.getLogger(__name__)


class ImageGen:
    def __init__(
        self,
        csv_path: Path,
        settings: Settings,
        thread_id: str | None = None,
        update: bool = False,
    ):
        self.csv_path = csv_path
        self.settings = settings
        self.thread_id = thread_id
        self.google_client = genai.Client(api_key=self.settings.GOOGLE_AI_STUDIO_KEY)
        self.update = update
        self.df = pd.read_csv(csv_path)

        repo_id = "RunDiffusion/Juggernaut-XI-v11"
        filename = "Juggernaut-XI-byRunDiffusion.safetensors"

        local_model_path = hf_hub_download(repo_id=repo_id, filename=filename)

        self.pipe = StableDiffusionXLPipeline.from_single_file(
            pretrained_model_link_or_path=local_model_path,
            torch_dtype=self.settings.IMAGEGEN_TORCH_DTYPE,
        ).to("cuda")

        logger.info(f"Loaded {len(self.df)} rows from {self.csv_path}")

    def _generate_image(
        self, prompt: str, output_path: Path, google: bool = False
    ) -> None:
        if google:
            response = self.google_client.models.generate_images(
                model=self.settings.GOOGLE_IMAGEGEN_MODEL,  # Use Imagen 3 model; adjust as needed
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1, aspect_ratio="16:9"
                ),
            )

            if not response.generated_images:
                raise Exception("No images generated")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            for generated_image in response.generated_images:
                generated_image.image.save(str(output_path))
        else:
            image = self.pipe(
                prompt,
                height=self.settings.IMAGEGEN_HEIGHT,
                width=self.settings.IMAGEGEN_WIDTH,
                guidance_scale=self.settings.IMAGEGEN_GUIDANCE_SCALE,
                num_inference_steps=self.settings.IMAGEGEN_INFERENCE_STEPS,
            ).images[0]

            image.save(str(output_path))

    def _process_thread(self, row: pd.Series, idx: int, thread_id: str) -> None:
        # generate images for different scenes
        status = row.get("status")
        sanitized = bool(row.get("sanitized"))

        if not sanitized or status == "rejected":
            logger.info(
                f"Thread {thread_id}'s status: {status}, sanitized: {sanitized}, skipping."
            )
            return

        prompts = [
            row.get("image_1_prompt"),
            row.get("image_2_prompt"),
            row.get("image_3_prompt"),
        ]

        for i, prompt in enumerate(prompts, start=1):
            scene_output_path = self.settings.DATA_DIR / thread_id / f"scene_{i}.png"
            scene_output_path_exists = scene_output_path.exists()

            if scene_output_path_exists and not self.update:
                logger.info(
                    f"Scene {i} already exists for thread {thread_id}, update: {self.update} skipping."
                )
                continue

            logger.info(
                f"{'Updating' if self.update and scene_output_path_exists else 'Generating'} scene {i} for thread {thread_id}..."
            )

            self._generate_image(prompt, scene_output_path)
            self.df.at[idx, f"image_{i}_path"] = str(scene_output_path)

        # generate thumbnail
        thumbnail_prompt = row.get("thumbnail_prompt")
        thumbnail_output_path = self.settings.DATA_DIR / thread_id / "thumbnail.png"
        thumbnail_output_path_exists = thumbnail_output_path.exists()

        if thumbnail_output_path_exists and not self.update:
            logger.info(f"Thumbnail already exists for thread {thread_id}, skipping.")
            return

        logger.info(
            f"{'Updating' if self.update and thumbnail_output_path_exists else 'Generating'} thumbnail for thread {thread_id}..."
        )

        self._generate_image(thumbnail_prompt, thumbnail_output_path)
        self.df.at[idx, "thumbnail_path"] = str(thumbnail_output_path)

        self.df.at[idx, "status"] = "image_populated"
        self.df.at[idx, "image_populated"] = True

        save(self.csv_path, self.df)

        logger.info(f"Images populated and saved for thread {thread_id}")

    def run(self) -> None:
        logger.info("Starting image generation process")
        try:
            if self.thread_id:
                row, idx = find_thread(self.thread_id, self.df)

                self._process_thread(row, idx, self.thread_id)

                return

            for idx, row in self.df.iterrows():
                thread_id = row.get("thread_id")

                self._process_thread(row, idx, thread_id)

        except Exception as e:
            logger.error(f"Error in image generation process: {e}")

        logger.info("Image generation process completed.")
        return


class ImageGenSingleton:
    """Singleton wrapper for ImageGen class"""

    _instance = None

    def __new__(
        cls,
        csv_path: Path = None,
        settings: Settings = None,
        thread_id: str | None = None,
        update: bool = False,
    ):
        if cls._instance is None:
            cls._instance = ImageGen(
                csv_path=csv_path,
                settings=settings,
                thread_id=thread_id,
                update=update,
            )
        return cls._instance

    def reset(
        self,
        csv_path: Path = None,
        settings: Settings = None,
        thread_id: str | None = None,
    ):
        """Reset the ImageGen instance with new parameters"""
        if self._instance is None:
            raise RuntimeError(
                "ImageGenSingleton not initialized. Call initialize() first."
            )

        # Update parameters if provided
        if csv_path is not None:
            self._instance.csv_path = csv_path
            self._instance.df = pd.read_csv(csv_path)
            logger.info(f"Reloaded {len(self._instance.df)} rows from {csv_path}")

        if settings is not None:
            self._instance.settings = settings
            logger.info("Updated settings and Google client")

        if thread_id is not None:
            self._instance.thread_id = thread_id
            logger.info(f"Updated thread_id to {thread_id}")
