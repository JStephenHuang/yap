from .base import BaseConfig


class RedditConfig(BaseConfig):
    """Reddit scraper configuration"""

    REDDIT_CLIENT_ID: str
    REDDIT_CLIENT_SECRET: str
    REDDIT_USER_AGENT: str = "creepypasta-bot/2.0"
