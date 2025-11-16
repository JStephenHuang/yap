from .reddit import RedditConfig
from .youtube import YouTubeConfig


class Settings(RedditConfig, YouTubeConfig):
    """Complete application settings - combines all service configs"""
    pass


# Singleton instance - import this everywhere
settings = Settings()
