class YouTubeConfig():
    """YouTube upload configuration"""

    # secrets
    YOUTUBE_CLIENT_SECRET_FILE: str
    YOUTUBE_CHANNEL_ID: str
    
    
    YOUTUBE_DEFAULT_TAGS: list[str] = [
        "creepypasta",
        "horror stories",
        "scary stories",
        "creepy narration",
        "true horror",
    ]
