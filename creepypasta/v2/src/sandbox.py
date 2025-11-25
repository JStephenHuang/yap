"""
Sandbox for testing triage without Reddit credentials.
Run from v2/: uv run sandbox
"""

import logging

from infrastructure.database import RedditThreadRepository, RedditThreadInsert, init_db
from graph.nodes.triage import triage_node
from graph.state import CreepypastaState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_test_data():
    """Insert fake posts for testing."""
    init_db()
    repo = RedditThreadRepository()

    fake_posts = [
        RedditThreadInsert(
            id="test_001",
            title="The Basement Door Won't Stay Closed",
            author="creepy_writer",
            content="Every night at 3am, I hear scratching from the basement. I've tried locks, nails, even a bookshelf against the door. Nothing works. Last night, I finally decided to go down there. What I found changed everything I thought I knew about my house...",
            subreddit="nosleep",
            score=1500,
            upvote_ratio=0.95,
            num_comments=234,
            url="https://reddit.com/r/nosleep/test_001",
            created_utc=1700000000.0,
        ),
        RedditThreadInsert(
            id="test_002",
            title="My Daughter's Imaginary Friend Isn't Imaginary",
            author="scared_parent",
            content="She calls him Mr. Whispers and says he lives in the walls. I thought it was cute until I heard a second voice responding to her last night. The voice was coming from inside her closet...",
            subreddit="creepypasta",
            score=2300,
            upvote_ratio=0.92,
            num_comments=456,
            url="https://reddit.com/r/creepypasta/test_002",
            created_utc=1700100000.0,
        ),
        RedditThreadInsert(
            id="test_003",
            title="The Last Elevator Ride",
            author="night_shift",
            content="Working security at an old hospital, I took the service elevator to floor 13. We don't have a floor 13. Someone was standing inside, waiting...",
            subreddit="shortscarystories",
            score=890,
            upvote_ratio=0.88,
            num_comments=123,
            url="https://reddit.com/r/shortscarystories/test_003",
            created_utc=1700200000.0,
        ),
    ]

    inserted = 0
    for post in fake_posts:
        if not repo.exists(post["id"]):
            repo.create(post)
            inserted += 1
            logger.info(f"Inserted: {post['title'][:40]}...")

    logger.info(f"Seeded {inserted} new posts")
    logger.info(f"Database status: {repo.count_by_status()}")


def triage():
    """Run the triage node."""
    logger.info("Running triage node...")
    initial_state: CreepypastaState = {}
    final_state = triage_node(initial_state)
    logger.info(f"Final state: {final_state}")
    return final_state


def main():
    """Seed data and run triage."""
    seed_test_data()
    print("\n" + "="*50 + "\n")
    triage()


if __name__ == "__main__":
    main()
