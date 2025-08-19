import asyncio
import csv
import json
import logging
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging

from ollama import AsyncClient
import pandas as pd
from pydantic import BaseModel

from creepypastas.config import Settings
from creepypastas.utils import save


class OllamaSanitizedText(BaseModel):
    """Result of the triage process."""

    sanitized_text: str


class OllamaSanitizedText(BaseModel):
    sanitized_text: str


class OllamaYouTubeTitle(BaseModel):
    youtube_title: str


class OllamaImagePrompts(BaseModel):
    image_1_prompt: str
    image_2_prompt: str
    image_3_prompt: str


class OllamaThumbnailPrompt(BaseModel):
    thumbnail_prompt: str


class Sanitizer:
    """
    Handles the sanitization of creepypasta stories.
    """

    def __init__(self, csv_path: Path, settings: Settings, rerun: bool = False):
        self.settings = settings
        self.csv_path = csv_path
        self.ollama = AsyncClient()
        self.settings = settings
        self.rerun = rerun
        # Load CSV, ensure required columns exist
        self.df = pd.read_csv(self.csv_path)
        for col in [
            "sanitized_text",
            "sanitized",
            "youtube_title",
            "youtube_description",
            "image_1_prompt",
            "image_2_prompt",
            "image_3_prompt",
            "thumbnail_prompt",
        ]:
            if col not in self.df.columns:
                self.df[col] = ""
        logging.info(f"Loaded {len(self.df)} rows from {self.csv_path}")

    # ----------------------
    # Ollama helpers
    # ----------------------
    async def _sanitize_text(self, story: str) -> str:
        response = await self.ollama.chat(
            model=self.settings.SANITIZER_LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": self.settings.SANITIZER_PROMPT.format(story=story),
                }
            ],
            format="json",
            options={"temperature": self.settings.SANITIZER_LLM_TEMPERATURE},
        )
        result = OllamaSanitizedText.model_validate_json(response.message.content)
        return result.sanitized_text

    async def _generate_title(self, story_sample: str) -> str:
        response = await self.ollama.chat(
            model=self.settings.SANITIZER_LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": self.settings.YOUTUBE_TITLE_PROMPT.format(
                        story_sample=story_sample[:500]  # prevent prompt bloat
                    ),
                }
            ],
            format="json",
            options={"temperature": 0.5},
        )
        result = OllamaYouTubeTitle.model_validate_json(response.message.content)
        return result.youtube_title

    async def _generate_image_prompts(
        self, story: str, num_images: int = 3
    ) -> OllamaImagePrompts:
        response = await self.ollama.chat(
            model=self.settings.SANITIZER_LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": self.settings.IMAGE_PROMPTS_GENERATION_PROMPT.format(
                        story=story, num_images=num_images
                    ),
                }
            ],
            format="json",
            options={"temperature": 0.6},
        )

        # Expect numbered list format, split by lines
        result = OllamaImagePrompts.model_validate_json(response.message.content)
        return result

    async def _generate_thumbnail_prompt(self, story_sample: str, title: str) -> str:
        response = await self.ollama.chat(
            model=self.settings.SANITIZER_LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": self.settings.THUMBNAIL_PROMPT_GENERATION_PROMPT.format(
                        story_sample=story_sample[:500],
                        title=title,
                    ),
                }
            ],
            format="json",
            options={"temperature": 0.6},
        )
        result = OllamaThumbnailPrompt.model_validate_json(response.message.content)
        return result.thumbnail_prompt

    # ----------------------
    # Main runner
    # ----------------------
    async def run(self):
        logging.info("Starting content preparation process")

        for idx, row in self.df.iterrows():
            thread_id = row.get("thread_id", "unknown")
            if (
                row.get("status") == "triaged"
                and bool(row.get("sanitized", False))
                or (row.get("status") != "rejected" and self.rerun)
            ):
                raw_text = row.get("raw_text", "")

                if not raw_text:
                    logging.warning(f"Thread {thread_id} has no raw text.")
                    continue

                logging.info(f"Processing thread {thread_id}...")

                try:
                    # 1. Sanitize story
                    sanitized = await self._sanitize_text(raw_text)
                    self.df.at[idx, "sanitized_text"] = sanitized

                    # 2. Generate YouTube title
                    title = await self._generate_title(sanitized)
                    self.df.at[idx, "youtube_title"] = title

                    # 3. Generate image prompts
                    image_prompts = await self._generate_image_prompts(
                        sanitized, num_images=3
                    )
                    self.df.at[idx, "image_1_prompt"] = image_prompts.image_1_prompt
                    self.df.at[idx, "image_2_prompt"] = image_prompts.image_2_prompt
                    self.df.at[idx, "image_3_prompt"] = image_prompts.image_3_prompt

                    # 4. Generate thumbnail prompt
                    thumbnail_prompt = await self._generate_thumbnail_prompt(
                        sanitized, title
                    )
                    self.df.at[idx, "thumbnail_prompt"] = thumbnail_prompt

                    self.df.at[idx, "sanitized"] = True
                    self.df.at[idx, "status"] = "sanitized"

                    # Save progress incrementally
                    save(self.csv_path, self.df)
                    logging.info(f"Thread {thread_id} prepared successfully.")

                except Exception as e:
                    logging.error(f"Error preparing thread {thread_id}: {e}")
            else:
                logging.info(
                    f"Thread {thread_id} already sanitized or status not triaged."
                )

        logging.info("Sanitization completed.")
