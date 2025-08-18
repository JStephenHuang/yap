import logging
from pathlib import Path
from typing import Optional
from ollama import AsyncClient
import pandas as pd
from pydantic import BaseModel
from creepypastas.utils import save

from creepypastas.config import Settings


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
        settings: Settings,
    ):
        self.csv_path = Path(csv_path)
        self.ollama = AsyncClient()
        self.settings = settings
        # Load CSV, ensure required columns exist
        self.df = pd.read_csv(self.csv_path)

        logger.info(f"Loaded {len(self.df)} threads from {self.csv_path}")

    async def triage(self) -> Optional[str]:
        """
        Iterate through non-triaged rows, evaluate each, update CSV.
        Returns None if no thread passes.
        """

        logger.info("Starting triage process")

        for idx, row in self.df.iterrows():
            # If already triaged, skip
            thread_id = row.get("thread_id", None)

            logger.info(f"Checking thread {thread_id}")

            if not bool(row.get("triaged", False)):
                raw_text = row.get("raw_text", None)
                title = row.get("title", None)

                opinion: OllamaOpinion = OllamaOpinion(approved=False, reasoning="")

                word_count = row.get("word_count", 0)
                # basic word-count check
                if self.settings.MIN_WORDS <= word_count <= self.settings.MAX_WORDS:
                    # ask Ollama to make final pass/fail decision
                    logger.info(
                        f"Thread {thread_id} passed word count and llm is evaluating thread..."
                    )
                    response = await self.ollama.chat(
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
                    opinion = OllamaOpinion.model_validate_json(
                        response.message.content
                    )
                    logger.info(
                        f"Thread {thread_id}: approved={opinion.approved}, reasoning={opinion.reasoning}"
                    )

                else:
                    logger.info(f"Thread {thread_id} skipped due to word count")
                    opinion.approved = False

                # Mark triaged
                self.df.at[idx, "triaged"] = True

                # Set status
                if opinion.approved:
                    logger.info(f"Thread {row["thread_id"]} approved.")
                    self.df.at[idx, "status"] = "triaged"
                else:
                    logger.info(f"Thread {row["thread_id"]} rejected.")
                    self.df.at[idx, "status"] = "rejected"
                    self.df.at[idx, "rejected_reasoning"] = opinion.reasoning

                # Save updated CSV after each decision
                save(self.csv_path, self.df)
            else:
                logger.info(f"Thread {thread_id} already triaged, skipping...")

        # No more candidates
        logger.info("Triage complete: no more threads to triage")
        return None
