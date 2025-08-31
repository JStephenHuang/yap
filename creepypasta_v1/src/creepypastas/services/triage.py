import logging
from pathlib import Path
from typing import Optional
from ollama import Client
import pandas as pd
from pydantic import BaseModel
from creepypastas.utils import save

from creepypastas.keys import Keys


class OllamaOpinion(BaseModel):
    """Result of the triage process."""

    approved: bool
    reasoning: str


logger = logging.getLogger(__name__)


class Triage:
    """
    Handles triage of raw Creepypasta Reddit threads in a CSV.

    - Skips already-triaged rows
    - Checks word count bounds
    - Uses Ollama LLM for a final YES/NO
    - Marks each row with `triaged` and `status`
    - Returns the first approved thread's ID & text
    """

    def __init__(
        self,
        csv_path: Path,
        settings: Keys,
    ):
        self.csv_path = csv_path
        self.ollama = Client()
        self.settings = settings
        # Load CSV, ensure required columns exist
        self.df = pd.read_csv(self.csv_path)

        logger.info(f"Loaded {len(self.df)} threads from {self.csv_path}")

    def _evaluate_thread(self, row) -> OllamaOpinion:
        """Evaluate a single thread using the Ollama LLM."""
        word_count = row.get("word_count")

        if (word_count < self.settings.MIN_WORDS) or (
            word_count > self.settings.MAX_WORDS
        ):
            return OllamaOpinion(
                approved=False,
                reasoning=f"Word count {word_count} outside bounds",
            )

        raw_text = row.get("raw_text", None)
        title = row.get("title", None)

        response = self.ollama.chat(
            model=self.settings.TRIAGE_LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": self.settings.TRIAGE_LLM_PROMPT.format(
                        text=raw_text,
                        title=title,
                    ),
                }
            ],
            format="json",
            options={"temperature": self.settings.TRIAGE_LLM_TEMPERATURE},
        )

        return OllamaOpinion.model_validate_json(response.message.content)

    def get_approved_thread(self) -> str | None:
        """
        Get one triaged thread's ID.

        """
        triaged_threads = self.df[self.df["status"] == "triaged"]

        if triaged_threads.empty:
            return None

        first_thread = triaged_threads.iloc[0]

        print(first_thread.get("word_count"), first_thread.get("raw_text"))

        return first_thread["thread_id"]

    def triage(self):
        """
        Iterate through non-triaged rows, evaluate each, update CSV.
        Returns None if no thread passes.
        """

        logger.info("Starting triage process")

        for idx, row in self.df.iterrows():
            # If already triaged, skip
            thread_id = row.get("thread_id")

            logger.info(f"Checking thread {thread_id}")

            if bool(row.get("triaged")):
                logger.info(f"Thread {thread_id} already triaged, skipping...")
                continue

            opinion = self._evaluate_thread(row)

            # Set status
            if opinion.approved:
                logger.info(f"Thread {thread_id} approved.")
                self.df.at[idx, "status"] = "triaged"
            else:
                logger.info(f"Thread {thread_id} rejected.")
                self.df.at[idx, "status"] = "rejected"
                self.df.at[idx, "rejected_reasoning"] = opinion.reasoning

            self.df.at[idx, "triaged"] = True

            # Save updated CSV after each decision
            save(self.csv_path, self.df)

        # No more candidates
        logger.info("Triage complete")
        return None
