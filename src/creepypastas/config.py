import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


class Settings(BaseSettings):
    """Application settings with defaults and validation."""

    # Where to save data
    DATA_DIR: Path = DATA_DIR
    THREADS_PATH: Path = DATA_DIR / "threads"

    # Reddit Wrapper (PRAW)
    REDDIT_CLIENT_ID: str = Field(..., env="REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = Field(..., env="REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT: str = Field(default="creepypasta-yap/0.1")
    REDDIT_SUBREDDITS: List[str] = Field(
        default=["CreepyPasta", "nosleep", "shortscarystories"]
    )
    REDDIT_POST_LIMIT: int = Field(default=10)

    # Triage settings
    MIN_WORDS: int = 300
    MAX_WORDS: int = 2000

    TRIAGE_LLM_MODEL: str = "llama3.1:8b"
    TRIAGE_LLM_PROMPT: str = """
    You are an expert evaluator of creepypasta stories and experiences. Your task is to determine if the following raw text strictly adheres to the creepypasta theme, meaning it presents a genuinely scary story or a frightening personal experience.

    Consider the following criteria:
    - **Scary Theme:** The core of the text should revolve around creating fear, suspense, unease, or horror.
    - **Narrative or Experiential:** It should be presented as either a fictional story or a recounting of a personal (though potentially fictionalized) scary experience.
    - **Exclusion of Other Themes:** The text should *not* primarily focus on other genres or topics such as:
        - General fiction without a significant horror element.
        - Non-fiction accounts that are not inherently scary.
        - Discussions, analyses, or explanations of creepypasta or horror in general (meta-commentary).
        - Requests for information or help.
        - Advertisements or promotional material.
        - Content that is primarily humorous, satirical, or romantic.
        - Content that is excessively graphic or disturbing without a clear scary narrative purpose.

    Evaluate the following title and raw text:
    ---
    {title}
    {text}
    ---

    Based solely on the criteria above, determine if this text qualifies as a creepypasta (scary story or experience) and explain why the story eithers qualifies or does not.

    Respond with a JSON object in the following format:
    {{
      "approved": true/false,
      "reasoning": "explanation of why it was approved or rejected",
    }}
    """
    TRIAGE_LLM_TEMPERATURE: float = 0.0  # Make responses deterministic

    class Config:
        """Pydantic config for environment variables."""

        env_file = ".env"
        env_file_encoding = "utf-8"
