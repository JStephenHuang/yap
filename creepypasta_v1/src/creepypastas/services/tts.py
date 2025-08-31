import logging
import re
from pathlib import Path

import pandas as pd
from pydub import AudioSegment

# from creepypastas.services.tts_v2.common import TTS

from creepypastas.keys import Keys
from creepypastas.utils import find_thread, save

from creepypastas.services.tts_v2.main import run as run_tts_v2
from creepypastas.services.tts_v2.BosonAi import HiggsAudioTTS

logger = logging.getLogger(__name__)


class Narrator:
    """
    Handles narration of sanitized creepypasta stories.
    """

    def __init__(self, csv_path: Path, settings: Keys, thread_id: str | None = None):
        self.settings = settings
        self.csv_path = csv_path
        self.thread_id = thread_id
        # Load CSV, ensure required columns exist
        self.df = pd.read_csv(csv_path)

        logger.info(f"Loaded {len(self.df)} rows from {self.csv_path}")

        # self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(
        #     "cuda"
        # )

    def _chunk_by_sentence(self, text: str) -> list[str]:
        """Split text into chunks by sentence and clean up artifacts."""
        sentences = re.split(r"(?<=[.!?])\s+", text)

        cleaned = []
        for sentence in sentences:
            s = sentence.replace("\n", " ").replace("\t", " ").strip()

            s = re.sub(r"^[\W_]+", "", s)

            if s and len(s) > 3:
                cleaned.append(s)

        return cleaned

    # def _narrate_story(self, sanitized_text: str, output_dir: Path) -> None:
    #     """Generate narration for one story and return audio path."""
    #     output_dir.parent.mkdir(parents=True, exist_ok=True)

    #     logger.info(f"Sanitized text: {sanitized_text}")

    #     print(f"input: {self._chunk_by_sentence(sanitized_text)}")

    #     clean_text = " ".join(self._chunk_by_sentence(sanitized_text))

    #     self.tts.tts_to_file(
    #         text=clean_text,
    #         file_path=str(output_dir),
    #         speaker_wav=self.settings.TTS_SPEAKER_PATH,
    #         language="en",
    #         split_sentences=True,
    #     )

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

        # self._narrate_story(sanitized_text, output_dir)
        run_tts_v2(HiggsAudioTTS(), sanitized_text, output_dir)
        logger.info(f"Audio saved to {output_dir}")

        self.df.at[idx, "audio_path"] = output_dir
        self.df.at[idx, "narrated"] = True
        self.df.at[idx, "status"] = "narrated"

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
            logger.error(f"Error narrating thread {e}")

        logger.info("Narration process completed.")
