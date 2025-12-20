"""
YouTube upload configuration.
"""

from config.base import EnvConfig


class YouTubeConfig(EnvConfig):
    """YouTube node configuration."""

    # OAuth credentials (load from env/secrets)
    YOUTUBE_CLIENT_SECRET_FILE: str
    TOKEN_DIR: str = "token_files"

    # API scopes
    SCOPES: list[str] = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube",
    ]

    # Video defaults
    CATEGORY_ID: str = "24"  # Entertainment
    PRIVACY_STATUS: str = "public"
    MADE_FOR_KIDS: bool = False
    NOTIFY_SUBSCRIBERS: bool = False

    # Default tags
    DEFAULT_TAGS: list[str] = [
        "creepypasta",
        "horror stories",
        "scary stories",
        "creepy narration",
        "true horror",
    ]


youtube_config = YouTubeConfig()
