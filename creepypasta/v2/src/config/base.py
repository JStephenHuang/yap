from pydantic_settings import BaseSettings, SettingsConfigDict

from pathlib import Path

_ROOT_PATH = Path(__file__).resolve().parents[2]
class BaseConfig(BaseSettings):
    """Base configuration that all services inherit from"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # API keys for LLM providers
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # Global paths
    DB_PATH: Path = _ROOT_PATH / "db"
    RUNS_PATH: Path = _ROOT_PATH / "runs"