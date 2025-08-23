import logging
from pathlib import Path

import pandas as pd
from TTS.api import TTS

from creepypastas.config import Settings
from creepypastas.utils import find_thread, save

logger = logging.getLogger(__name__)


class Narrator:
    """
    Handles narration of sanitized creepypasta stories.
    """

    def __init__(
        self, csv_path: Path, settings: Settings, thread_id: str | None = None
    ):
        self.settings = settings
        self.csv_path = csv_path
        self.thread_id = thread_id
        # Load CSV, ensure required columns exist
        self.df = pd.read_csv(csv_path)

        logger.info(f"Loaded {len(self.df)} rows from {self.csv_path}")

        # Load TTS model once
        self.tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        ).to("cuda")

    def _narrate_story(self, sanitized_text: str, output_dir: Path) -> str:
        """Generate narration for one story and return audio path."""
        output_dir.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Sanitized text: {sanitized_text}")

        self.tts.tts_to_file(
            text=sanitized_text,
            file_path=str(output_dir),
            speaker_wav=self.settings.TTS_SPEAKER_PATH,
            language="en",
        )

    def _process_thread(self, row: pd.Series, idx: int, thread_id: str) -> None:
        status = row.get("status")
        sanitized = bool(row.get("sanitized"))

        if status == "rejected" or not sanitized:
            logger.info(
                f"Thread {thread_id}'s status: {status}, sanitized: {sanitized}, skipping."
            )
            return

        sanitized_text = row.get("sanitized_text")

        output_dir = self.settings.DATA_DIR / thread_id / "narration.wav"

        self._narrate_story(sanitized_text, output_dir)
        logger.info(f"Audio saved to {output_dir}")

        self.df.at[idx, "audio_path"] = output_dir
        self.df.at[idx, "narrated"] = True

        save(self.csv_path, self.df)

        logger.info(f"Narration saved for thread {thread_id}: {output_dir}")

    def run(self):
        logger.info("Starting narration process")
        try:

            if self.thread_id:
                row, idx = find_thread(self.thread_id, self.df)
                self._process_thread(row, idx, self.thread_id)

                return

            for idx, row in self.df.iterrows():
                thread_id = row.get("thread_id", f"row{idx}")

                self._process_thread(row, idx, thread_id)

                return  # break after first narration...

        except Exception as e:
            logger.error(f"Error narrating thread {thread_id}: {e}")

        logger.info("Narration process completed.")
