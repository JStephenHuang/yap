import asyncio
import logging
from pathlib import Path

import pandas as pd
from ollama import AsyncClient
from pydantic import BaseModel

from creepypastas.config import Settings
from creepypastas.utils import save


class OllamaSanitizedText(BaseModel):
    sanitized_text: str


class OllamaYouTubeTitle(BaseModel):
    youtube_title: str


class OllamaImagePrompts(BaseModel):
    image_1_prompt: str
    image_2_prompt: str
    image_3_prompt: str


class OllamaYouTubeDescription(BaseModel):
    youtube_description: str


class OllamaThumbnailPrompt(BaseModel):
    thumbnail_prompt: str


class Sanitizer:
    """
    Handles the sanitization of creepypasta stories.
    """

    def __init__(
        self,
        csv_path: Path,
        settings: Settings,
        thread_id: str | None = None,
        pipeline: bool = False,
    ):
        self.csv_path = csv_path
        self.settings = settings
        self.thread_id = thread_id
        self.ollama = AsyncClient()
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
                self.df[col] = None
        logging.info(f"Loaded {len(self.df)} rows from {self.csv_path}")

    # ----------------------
    # Ollama helpers
    # ----------------------
    def _sanitize_text(self, story: str) -> str:
        response = self.ollama.chat(
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
        result = OllamaSanitizedText.model_validate_json(response["message"]["content"])
        return result.sanitized_text

    def _generate_title(self, story_sample: str) -> str:
        response = self.ollama.chat(
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
        result = OllamaYouTubeTitle.model_validate_json(response["message"]["content"])
        return result.youtube_title

    def _generate_description(
        self, story_sample: str, author: str, thread_link: str
    ) -> str:
        response = self.ollama.chat(
            model=self.settings.SANITIZER_LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": self.settings.YOUTUBE_DESCRIPTION_PROMPT.format(
                        story_sample=story_sample[
                            :500
                        ],  # longer window for description
                        author=author,
                        thread_link=thread_link,
                    ),
                }
            ],
            format="json",
            options={"temperature": 0.6},
        )
        result = OllamaYouTubeDescription.model_validate_json(
            response["message"]["content"]
        )
        return result.youtube_description

    def _generate_image_prompts(
        self, story: str, num_images: int = 3
    ) -> OllamaImagePrompts:
        response = self.ollama.chat(
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

        result = OllamaImagePrompts.model_validate_json(response["message"]["content"])
        return result

    def _generate_thumbnail_prompt(self, story_sample: str, title: str) -> str:
        response = self.ollama.chat(
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
        result = OllamaThumbnailPrompt.model_validate_json(
            response["message"]["content"]
        )
        return result.thumbnail_prompt

    def _process_thread(self, idx: int, thread_id: str) -> None:
        row = self.df.iloc[idx]
        raw_text = row.get("raw_text")
        if not raw_text:
            raise Exception(f"No raw_text found for thread {thread_id}")

        logging.info(f"Processing thread {thread_id}...")

        # 1. Sanitize story
        sanitized_text = self._sanitize_text(raw_text)
        self.df.at[idx, "sanitized_text"] = sanitized_text

        # 2. Generate YouTube title
        title = self._generate_title(sanitized_text)
        self.df.at[idx, "youtube_title"] = title

        # Generate youtube description
        author = row.get("author")
        thread_link = row.get("url")
        description = self._generate_description(sanitized_text, author, thread_link)
        self.df.at[idx, "youtube_description"] = description

        # 3. Generate image prompts
        image_prompts = self._generate_image_prompts(sanitized_text, num_images=3)
        self.df.at[idx, "image_1_prompt"] = image_prompts.image_1_prompt
        self.df.at[idx, "image_2_prompt"] = image_prompts.image_2_prompt
        self.df.at[idx, "image_3_prompt"] = image_prompts.image_3_prompt

        # 4. Generate thumbnail prompt
        thumbnail_prompt = self._generate_thumbnail_prompt(sanitized_text, title)
        self.df.at[idx, "thumbnail_prompt"] = thumbnail_prompt

        self.df.at[idx, "sanitized"] = True
        self.df.at[idx, "status"] = "sanitized"

        # Save progress incrementally
        save(self.csv_path, self.df)
        logging.info(f"Thread {thread_id} prepared successfully.")

    # ----------------------
    # Main runner
    # ----------------------

    def run(self) -> None:

        logging.info("Starting content preparation process")
        try:
            if self.thread_id:
                # Process only the specified thread_id
                row_idx = self.df.index[self.df["thread_id"] == self.thread_id].tolist()
                if not row_idx:
                    logging.warning(f"No row found for thread {self.thread_id}")
                    return

                idx = row_idx[0]
                row = self.df.iloc[idx]

                if row.get("status") != "rejected":
                    self._process_thread(idx, self.thread_id)
                else:
                    logging.info(
                        f"Thread {self.thread_id} already sanitized or status not triaged."
                    )
                return

            # Process all eligible threads
            for idx, row in self.df.iterrows():
                thread_id = row.get("thread_id", f"thread_{idx}")
                if row.get("status") == "triaged" and bool(row.get("sanitized", False)):
                    self._process_thread(idx, thread_id)
                else:
                    logging.info(
                        f"Thread {thread_id} already sanitized or status not triaged."
                    )
            logging.info("Starting content preparation process")

        except Exception as e:
            logging.error(f"Error during sanitization: {e}")
