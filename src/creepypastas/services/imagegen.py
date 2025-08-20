from pathlib import Path
import logging

import pandas as pd
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

from creepypastas.config import Settings
from creepypastas.utils import save


class ImageGen:
    def __init__(
        self,
        csv_path: Path,
        settings: Settings,
        thread_id: str | None = None,
    ):
        self.csv_path = csv_path
        self.settings = settings
        self.thread_id = thread_id
        self.google_client = genai.Client(api_key=self.settings.GOOGLE_AI_STUDIO_KEY)
        # Load CSV, ensure required columns exist
        self.df = pd.read_csv(csv_path)

        # Ensure necessary columns exist
        for col in ["image_1_path", "image_2_path", "image_3_path", "thumbnail_path"]:
            if col not in self.df.columns:
                self.df[col] = ""

        logging.info(f"Loaded {len(self.df)} rows from {self.csv_path}")

    def _generate_image(self, prompt: str, output_path: Path) -> None:
        response = self.google_client.models.generate_images(
            model="imagen-4.0-generate-001",  # Use Imagen 3 model; adjust as needed
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9"),
        )

        if not response.generated_images:
            raise ValueError("No images generated")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        for generated_image in response.generated_images:
            generated_image.image.save(str(output_path))

    def _generate_images_for_thread(
        self, idx: int, thread_id: str, is_update: bool = False
    ) -> None:
        row = self.df.iloc[idx]
        try:
            prompts = [
                row.get("image_1_prompt"),
                row.get("image_2_prompt"),
                row.get("image_3_prompt"),
            ]

            for i, prompt in enumerate(prompts, start=1):
                if not prompt:
                    logging.warning(
                        f"Prompt {i} is missing for thread {thread_id}, skipping."
                    )
                    continue

                output_path = self.settings.DATA_DIR / thread_id / f"scene_{i}.png"
                self._generate_image(prompt, output_path)
                self.df.at[idx, f"image_{i}_path"] = str(output_path)

            thumbnail_prompt = row.get("thumbnail_prompt")
            if thumbnail_prompt:
                logging.info(
                    f"{'Updating' if is_update else 'Generating'} thumbnail for thread {thread_id}..."
                )
                output_path = self.settings.DATA_DIR / thread_id / "thumbnail.png"
                self._generate_image(thumbnail_prompt, output_path)
                self.df.at[idx, "thumbnail_path"] = str(output_path)

            # Mark as image-populated
            self.df.at[idx, "image_populated"] = True

            # Save progress incrementally
            save(self.csv_path, self.df)
            logging.info(
                f"Images and thumbnail {'updated' if is_update else 'generated'} for thread {thread_id}"
            )

        except Exception as e:
            logging.error(
                f"Error {'updating' if is_update else 'generating'} images for thread {thread_id}: {e}"
            )

    def run(self) -> None:
        logging.info("Starting image generation process")
        try:
            if self.thread_id:
                row_idx = self.df.index[self.df["thread_id"] == self.thread_id].tolist()
                if not row_idx:
                    logging.warning(f"No row found for thread {self.thread_id}")
                    return

                idx = row_idx[0]
                row = self.df.iloc[idx]

                if bool(row.get("image_populated")) and row.get("status") != "rejected":
                    logging.info(f"Updating images for thread {self.thread_id}...")
                    self._generate_images_for_thread(
                        idx, self.thread_id, is_update=True
                    )
                return

            for idx, row in self.df.iterrows():
                thread_id = row.get("thread_id", f"row{idx}")

                if row.get("status") == "sanitized" and not bool(
                    row.get("image_populated")
                ):
                    logging.info(f"Generating images for thread {thread_id}...")
                    self._generate_images_for_thread(idx, thread_id)
                else:
                    logging.info(
                        f"Thread {thread_id} is either not sanitized or already image-populated, skipping."
                    )
        except Exception as e:
            logging.error(f"Error in image generation process: {e}")

        logging.info("Image generation process completed.")
