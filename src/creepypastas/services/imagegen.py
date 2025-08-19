from pathlib import Path

# from diffusers import DiffusionPipeline, StableDiffusionPipeline
import pandas as pd
import logging

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

from creepypastas.config import Settings
from creepypastas.utils import save


class ImageGen:
    def __init__(self, csv_path: Path, settings: Settings, rerun: bool = False):
        self.csv_path = csv_path
        self.settings = settings
        self.rerun = rerun
        self.google_client = genai.Client(api_key=self.settings.GOOGLE_AI_STUDIO_KEY)
        # Load CSV, ensure required columns exist
        self.df = pd.read_csv(csv_path)

        # Ensure necessary columns exist
        for col in ["image_1_path", "image_2_path", "image_3_path", "thumbnail_path"]:
            if col not in self.df.columns:
                self.df[col] = ""

        logging.info(f"Loaded {len(self.df)} rows from {self.csv_path}")

        # Load Flux Diffuser model using settings
        # self.image_pipe = StableDiffusionPipeline.from_pretrained(
        #     pretrained_model_name_or_path=self.settings.IMAGEGEN_MODEL,
        #     torch_dtype=self.settings.IMAGEGEN_TORCH_DTYPE,
        # ).to(self.settings.IMAGEGEN_TORCH_DEVICE)

        # self.image_pipe.enable_model_cpu_offload()

    async def _generate_image(self, prompt, output_dir: Path):
        # image = self.image_pipe(
        #     prompt,
        #     height=self.setting.IMAGEGEN_HEIGHT,
        #     width=self.setting.IMAGEGEN_WIDTH,
        #     true_cfg_scale=self.setting.IMAGEGEN_GUIDANCE_SCALE,
        #     num_inference_steps=self.setting.IMAGEGEN_INFERENCE_STEPS,
        # ).images[0]

        # output_dir.parent.mkdir(parents=True, exist_ok=True)

        # image.save(str(output_dir))

        response = self.google_client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9"),
        )

        for generated_image in response.generated_images:

            # image_bytes = base64.b64decode(generated_image.image)
            # image = Image.open(BytesIO(image_bytes))

            output_dir.parent.mkdir(parents=True, exist_ok=True)

            generated_image.image.save(str(output_dir))

    async def run(self):
        logging.info("Starting image generation process")

        for idx, row in self.df.iterrows():
            thread_id = row.get("thread_id", f"row{idx}")

            if (
                row.get("status") == "sanitized"
                and not bool(row.get("image_populated"))
                or (row.get("status") != "rejected" and self.rerun)
            ):
                logging.info(f"Generating images for thread {thread_id}...")

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
                        output_dir = (
                            self.settings.DATA_DIR / thread_id / f"scene_{i}.png"
                        )
                        await self._generate_image(prompt, output_dir)

                        # Save the image path to the corresponding column
                        self.df.at[idx, f"image_{i}_path"] = str(output_dir)

                    # Generate thumbnail if prompt exists
                    thumbnail_prompt = row.get("thumbnail_prompt")
                    if thumbnail_prompt:
                        logging.info(f"Generating thumbnail for thread {thread_id}...")
                        output_dir = (
                            self.settings.DATA_DIR / thread_id / "thumbnail.png"
                        )
                        thumbnail_path = await self._generate_image(
                            thumbnail_prompt, output_dir
                        )
                        self.df.at[idx, "thumbnail_path"] = str(thumbnail_path)

                    # Mark as image-populated
                    self.df.at[idx, "image_populated"] = True

                    # Save progress incrementally
                    save(self.csv_path, self.df)
                    logging.info(f"Images and thumbnail saved for thread {thread_id}")

                    return

                except Exception as e:
                    logging.error(
                        f"Error generating images for thread {thread_id}: {e}"
                    )
            else:
                logging.info(
                    f"Thread {thread_id} is either not sanitized or already image-readied, skipping."
                )

        logging.info("Image generation process completed.")
