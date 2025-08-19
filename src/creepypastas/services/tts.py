import asyncio
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from TTS.api import TTS

import soundfile

import nltk
from nltk.tokenize import sent_tokenize

from creepypastas.config import Settings
from creepypastas.utils import save


class Narrator:
    """
    Handles narration of sanitized creepypasta stories.
    """

    def __init__(self, csv_path: Path, settings: Settings, rerun: bool = False):
        self.settings = settings
        self.csv_path = csv_path
        self.rerun = rerun
        # Load CSV, ensure required columns exist
        self.df = pd.read_csv(csv_path)

        logging.info(f"Loaded {len(self.df)} rows from {self.csv_path}")

        # Load TTS model once
        self.tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        ).to("cuda")

        nltk.download("punkt")

    def _narrate_story(self, sanitized_text: str, output_dir: Path) -> str:
        """Generate narration for one story and return audio path."""
        output_dir.parent.mkdir(parents=True, exist_ok=True)

        logging.info(f"Sanitized text: {sanitized_text}")

        self.tts.tts_to_file(
            text=sanitized_text,
            file_path=str(output_dir),
            speaker_wav=self.settings.TTS_SPEAKER_PATH,
            language="en",
        )

    async def run(self):
        logging.info("Starting narration process")

        for idx, row in self.df.iterrows():
            sanitized_text = row.get("sanitized_text")
            thread_id = row.get("thread_id", f"row{idx}")

            if (row.get("status") == "sanitized" and not pd.isna(sanitized_text)) or (
                row.get("status") != "rejected" and self.rerun
            ):
                logging.info(f"Narrating thread {thread_id}...")

                try:
                    output_dir = self.settings.DATA_DIR / thread_id / "narration.wav"

                    self._narrate_story(sanitized_text, output_dir)
                    logging.info(f"Audio saved to {output_dir}")

                    self.df.at[idx, "audio_path"] = output_dir
                    self.df.at[idx, "narrated"] = True

                    # Save progress incrementally
                    save(self.csv_path, self.df)
                    logging.info(
                        f"Narration saved for thread {thread_id}: {output_dir}"
                    )
                    return  # break after first narration...

                except Exception as e:
                    logging.error(f"Error narrating thread {thread_id}: {e}")
            else:
                logging.info(f"Thread {thread_id} has no sanitized text, skipping.")

        logging.info("Narration process completed.")
