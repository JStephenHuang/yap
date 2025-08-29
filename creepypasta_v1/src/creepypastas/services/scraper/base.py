import praw
from creepypastas.keys import Keys

REDDIT_USER_AGENT: str = "creepypasta-yap/0.1"
REDDIT_SUBREDDITS: list[str] = ["CreepyPasta", "nosleep", "shortscarystories"]
REDDIT_POST_LIMIT: int = 10


def scrape_story():

    key = Keys()

    reddit = praw.Reddit(
        client_id=key.REDDIT_CLIENT_ID,
        client_secret=key.REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    
