class RedditConfig():
    """Reddit scraper configuration"""

    REDDIT_CLIENT_ID: str
    REDDIT_CLIENT_SECRET: str
    REDDIT_USER_AGENT: str = "creepypasta-bot/2.0"

    # Target subreddits ranked by content quality
    SUBREDDITS: list[str] = ["nosleep", "creepypasta", "shortscarystories"]

    # Minimum thresholds to filter low-quality posts
    MIN_SCORE: int = 10
    MIN_TEXT_LENGTH: int = 500


# Import this directly: from config.reddit import reddit_config
reddit_config = RedditConfig()
