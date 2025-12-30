"""
Entry point for Reddit scraping.

Usage:
    uv run scrape-reddit
"""

import logging

from rich.logging import RichHandler

from config.reddit import reddit_config
from infrastructure.reddit_scraper import scrape_subreddit, get_reddit_client
from infrastructure.database import RedditThreadRepositorySingleton, RedditThreadInsert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%H:%M:%S]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)]
)
logger = logging.getLogger(__name__)


def run(
    limit_per_sub: int = 50,
    time_filter: str = "week",
) -> int:
    """
    Scrape all configured subreddits into SQLite.

    Returns:
        Number of new threads added.
    """
    repo = RedditThreadRepositorySingleton()
    reddit = get_reddit_client()

    total_scraped = 0
    total_new = 0

    for subreddit in reddit_config.SUBREDDITS:
        logger.info(f"Scraping r/{subreddit}")
        try:
            for post in scrape_subreddit(reddit, subreddit, limit_per_sub, time_filter):
                total_scraped += 1

                if not repo.exists(post["id"]):
                    thread = RedditThreadInsert(
                        id=post["id"],
                        title=post["title"],
                        author=post["author"],
                        content=post["text"],
                        subreddit=post["subreddit"],
                        score=post["score"],
                        upvote_ratio=post["upvote_ratio"],
                        num_comments=post["num_comments"],
                        url=post["url"],
                        created_utc=post["created_utc"],
                    )
                    repo.create(thread)
                    total_new += 1

        except Exception as e:
            logger.error(f"Failed scraping r/{subreddit}: {e}")
            continue

    logger.info(f"Scraped {total_scraped} posts, {total_new} new")

    return total_new


if __name__ == "__main__":
    run()
