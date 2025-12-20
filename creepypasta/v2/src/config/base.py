from pydantic_settings import BaseSettings, SettingsConfigDict

from pathlib import Path

_ROOT_PATH = Path(__file__).resolve().parents[2]
_ENV_FILE = _ROOT_PATH / ".env"


class EnvConfig(BaseSettings):
    """Minimal base that only loads .env - inherit this for any config needing env vars"""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )


class BaseConfig(EnvConfig):
    """App-wide configuration with shared settings"""

    # API keys for LLM providers
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # Global paths
    DB_PATH: Path = _ROOT_PATH / "db"
    RUNS_PATH: Path = _ROOT_PATH / "runs"