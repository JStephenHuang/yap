"""
Reddit scraper for creepypasta content.
Saves to both JSONL (raw backup) and SQLite (pipeline state).
"""

import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import praw
from praw.models import Submission

from config.reddit import reddit_config
from config.base import BaseConfig

from infrastructure.json import append_jsonl
from infrastructure.database import RedditThreadRepositorySingleton, RedditThreadInsert

logger = logging.getLogger(__name__)


def get_reddit_client() -> praw.Reddit:
    """Factory for Reddit client."""
    return praw.Reddit(
        client_id=reddit_config.REDDIT_CLIENT_ID,
        client_secret=reddit_config.REDDIT_CLIENT_SECRET,
        user_agent=reddit_config.REDDIT_USER_AGENT,
    )


def _submission_to_dict(submission: Submission) -> dict | None:
    """
    Extract relevant fields from submission.
    Returns None if post should be filtered out.
    """
    text = submission.selftext

    if len(text) < reddit_config.MIN_TEXT_LENGTH:
        return None

    if submission.score < reddit_config.MIN_SCORE:
        return None

    return {
        "id": submission.id,
        "title": submission.title,
        "text": text,
        "author": str(submission.author) if submission.author else "[deleted]",
        "subreddit": submission.subreddit.display_name,
        "score": submission.score,
        "upvote_ratio": submission.upvote_ratio,
        "num_comments": submission.num_comments,
        "created_utc": submission.created_utc,
        "url": f"https://reddit.com{submission.permalink}",
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def scrape_subreddit(
    reddit: praw.Reddit,
    subreddit_name: str,
    limit: int = 100,
    time_filter: str = "week",
):
    """
    Scrape top posts from a subreddit.
    Uses 'top' instead of 'hot' for better story quality.
    """
    subreddit = reddit.subreddit(subreddit_name)

    for submission in subreddit.top(time_filter=time_filter, limit=limit):
        post = _submission_to_dict(submission)
        if post:
            yield post
        time.sleep(0.1)  # Rate limit


def run(
    limit_per_sub: int = 50,
    time_filter: str = "week",
) -> Path:
    """
    Scrape all configured subreddits.
    Saves to JSONL (raw backup) and SQLite (deduped pipeline state).
    Returns path to output file.
    """
    # Initialize database
    repo = RedditThreadRepositorySingleton()

    # Setup output file
    output_path = BaseConfig().RAW_DATA_PATH / "reddit_threads"
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"creepypasta_{timestamp}.jsonl"

    reddit = get_reddit_client()
    total_scraped = 0
    total_new = 0

    for subreddit in reddit_config.SUBREDDITS:
        logger.info(f"Scraping r/{subreddit}")
        try:
            for post in scrape_subreddit(reddit, subreddit, limit_per_sub, time_filter):
                # Always append to JSONL (raw backup)
                append_jsonl(post, output_file)
                total_scraped += 1

                # Only insert to DB if not already exists
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

    logger.info(f"Scraped {total_scraped} posts, {total_new} new -> {output_file}")
    return output_file