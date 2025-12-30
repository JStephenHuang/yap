"""
Reddit scraper for creepypasta content.
"""

import logging
import time
from datetime import datetime, timezone

import praw
from praw.models import Submission

from config.reddit import reddit_config

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