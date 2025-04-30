from typing import Dict, Optional, List
from pydantic import BaseModel, Field


class RedditThread(BaseModel):
    """Raw Reddit Thread"""

    author: str = Field(..., description="Original author username")
    url: str = Field(..., description="Original post URL")
    subreddit: str = Field(..., description="Subreddit the story was posted in")
    created_utc: float = Field(
        ..., description="UTC timestamp of when the post was created"
    )
    upvote_ratio: Optional[float] = Field(
        None, description="Ratio of upvotes to downvotes"
    )
    score: Optional[int] = Field(None, description="Score (upvotes - downvotes)")


import csv
import logging
import pandas
from pathlib import Path
from datetime import datetime

import praw
from praw.models import Submission

from creepypastas.config import Settings
from creepypastas.utils import ensure_dir

logger = logging.getLogger(__name__)


class RedditScrapper:
    """Scraps Reddit for Creepypasta stories."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT,
        )

        logger.info("Initialized Reddit scraper")

    def scrape_stories(self) -> Path:
        """Scrape stories from configured subreddits and save to CSV.

        Returns:
            Path to the saved CSV file
        """
        all_threads = []

        logger.info("Scraping Reddit threads...")

        # Scrape all configured subreddits
        for subreddit in self.settings.REDDIT_SUBREDDITS:
            threads = self._get_threads(
                subreddit, limit=self.settings.REDDIT_POST_LIMIT
            )

            all_threads.extend(threads)

        # Convert to dictionaries
        threads_data = [self._submission_to_dict(post) for post in all_threads]

        # Create dataframe
        data_frame = pandas.DataFrame(threads_data)

        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reddit_threads_{timestamp}.csv"

        # Ensure directory exists
        ensure_dir(self.settings.DATA_DIR)

        # Save to CSV
        csv_path = self.settings.THREADS_PATH / filename
        data_frame.to_csv(csv_path, index=False, quoting=csv.QUOTE_ALL)

        logger.info(f"Saved {len(threads_data)} posts to {csv_path}")
        return csv_path

    def _get_threads(self, subreddit_name: str, limit: int = 50) -> List[Submission]:
        """
        Get threads from a specific subreddit.

        Args:
            subreddit_name: Name of the subreddit to scrape
            limit: Maximum number of threads to retrieve

        Returns:
            List of Reddit Submission objects
        """
        return list(self.reddit.subreddit(subreddit_name).hot(limit=limit))

    def _submission_to_dict(self, submission: Submission) -> Dict:
        """Convert a Reddit submission to a dictionary.

        Args:
            submission: Reddit submission object

        Returns:
            Dictionary with submission data
        """
        return {
            "thread_id": submission.id,
            "title": submission.title,
            "raw_text": submission.selftext,
            "url": f"https://www.reddit.com{submission.permalink}",
            "author": str(submission.author),
            "subreddit": submission.subreddit.display_name,
            "created_utc": submission.created_utc,
            "upvote_ratio": submission.upvote_ratio,
            "score": submission.score,
            "num_comments": submission.num_comments,
            "is_original": submission.is_original_content,
            "is_self": submission.is_self,
            "word_count": len(submission.selftext.split()),
            "used": False,
        }
