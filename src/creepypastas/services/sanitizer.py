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
    image_prompts: list[str]


class OllamaThumbnailPrompt(BaseModel):
    thumbnail_prompt: str


class Sanitizer:
    """
    Handles the sanitization of creepypasta stories.
    """

    def __init__(self, csv_path: str, settings: Settings):
        self.settings = settings
        self.csv_path = Path(csv_path)
        self.ollama = AsyncClient()
        self.settings = settings
        # Load CSV, ensure required columns exist
        self.df = pd.read_csv(self.csv_path)
        for col in [
            "sanitized_text",
            "sanitized",
            "youtube_title",
            "youtube_description",
            "image_prompts",
            "thumbnail_prompt",
        ]:
            if col not in self.df.columns:
                self.df[col] = None
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
    ) -> list[str]:
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
        return result.image_prompts

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
            if row.get("status") == "triaged" and not bool(row.get("sanitized", False)):
                thread_id = row.get("thread_id", "unknown")
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
                    self.df.at[idx, "image_prompts"] = json.dumps(image_prompts)

                    # 4. Generate thumbnail prompt
                    thumbnail_prompt = await self._generate_thumbnail_prompt(
                        sanitized, title
                    )
                    self.df.at[idx, "thumbnail_prompt"] = thumbnail_prompt

                    # self.df.at[idx, "sanitized"] = True

                    # Save progress incrementally
                    save(self.csv_path, self.df)
                    logging.info(f"Thread {thread_id} prepared successfully.")

                except Exception as e:
                    logging.error(f"Error preparing thread {thread_id}: {e}")

        logging.info("Content preparation completed.")
