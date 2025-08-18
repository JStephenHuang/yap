import asyncio
import logging
from pathlib import Path

import pandas as pd
from TTS.api import TTS

from creepypastas.config import Settings
from creepypastas.utils import save


class Narrator:
    """
    Handles narration of sanitized creepypasta stories.
    """

    def __init__(self, csv_path: Path, settings: Settings):
        self.settings = settings
        self.csv_path = csv_path
        # Load CSV, ensure required columns exist
        self.df = pd.read_csv(csv_path)

        logging.info(f"Loaded {len(self.df)} rows from {self.csv_path}")

        # Load TTS model once
        self.tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        ).to("cuda")

    async def _narrate_story(self, sanitized_text: str, thread_id: str) -> str:
        """Generate narration for one story and return audio path."""
        out_path = self.settings.TTS_OUTPUT_PATH / f"{thread_id}.wav"

        self.tts.tts_to_file(
            text=sanitized_text,
            file_path=str(out_path),
            speaker_wav=str(self.settings.TTS_SPEAKER_PATH),
            language="en",
        )
        return str(out_path)

    async def run(self):
        logging.info("Starting narration process")

        for idx, row in self.df.iterrows():
            sanitized_text = row.get("sanitized_text")
            thread_id = row.get("thread_id", f"row{idx}")

            if pd.isna(sanitized_text) or not sanitized_text.strip():
                logging.info(f"Thread {thread_id} has no sanitized text, skipping.")
                continue  # skip empty or NaN

            logging.info(f"Narrating thread {thread_id}...")

            try:
                out_path = await self._narrate_story(sanitized_text, thread_id)
                logging.info(f"Audio saved to {out_path}")

                return
                # self.df.at[idx, "audio_path"] = out_path

                # # Save progress incrementally
                # save(self.csv_path, self.df)
                logging.info(f"✅ Narration saved for thread {thread_id}: {out_path}")

            except Exception as e:
                logging.error(f"Error narrating thread {thread_id}: {e}")
            return

        logging.info("Narration process completed.")
