"""
Repository for reddit_threads database operations.
"""

from datetime import datetime, timezone
from typing import Iterator
from typing_extensions import TypedDict

from .connection import DatabaseConnectionSingleton


# Input type for creating threads
class RedditThreadInsert(TypedDict, total=False):
    thread_id: str
    title: str
    author: str
    content: str
    subreddit: str
    score: int
    upvote_ratio: float
    num_comments: int
    url: str
    created_utc: float


# DB entity type (what comes out)
class RedditThreadRow(TypedDict):
    thread_id: str
    title: str
    author: str
    content: str
    subreddit: str
    score: int
    upvote_ratio: float
    num_comments: int
    url: str
    created_utc: float
    status: str
    scraped_at: str

class RedditThreadRepository:
    """Repository for reddit thread data access."""

    def __init__(self):
        self._conn = DatabaseConnectionSingleton()
          # Enable foreign keys
        self._conn.execute("PRAGMA foreign_keys = ON")

        # Reddit threads - raw scraped data with status
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS reddit_threads (
                thread_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                content TEXT NOT NULL,
                subreddit TEXT,
                score INTEGER,
                upvote_ratio REAL,
                num_comments INTEGER,
                url TEXT,
                created_utc REAL,
                status TEXT DEFAULT 'raw',
                scraped_at TEXT NOT NULL
            )
        """)

        # Index for status queries
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_reddit_threads_status
            ON reddit_threads(status)
        """)

        self._conn.commit()

    def exists(self, thread_id: str) -> bool:
        """Check if thread exists."""
        cursor = self._conn.execute(
            "SELECT 1 FROM reddit_threads WHERE thread_id = ?",
            (thread_id,)
        )
        return cursor.fetchone() is not None

    def get_by_id(self, thread_id: str) -> RedditThreadRow | None:
        """Get thread by ID."""
        cursor = self._conn.execute(
            "SELECT * FROM reddit_threads WHERE thread_id = ?",
            (thread_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def create(self, data: RedditThreadInsert) -> None:
        """Insert a new reddit thread."""
        now = datetime.now(timezone.utc).isoformat()

        self._conn.execute("""
            INSERT INTO reddit_threads (
                thread_id, title, author, content,
                subreddit, score, upvote_ratio, num_comments, url, created_utc,
                status, scraped_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'scraped', ?)
        """, (
            data["id"],
            data["title"],
            data.get("author", ""),
            data["content"],
            data.get("subreddit", ""),
            data.get("score", 0),
            data.get("upvote_ratio", 0.0),
            data.get("num_comments", 0),
            data.get("url", ""),
            data.get("created_utc", 0.0),
            now
        ))
        self._conn.commit()

    def get_raw(self, limit: int = 100) -> list[RedditThreadRow]:
        """Get unprocessed threads (status = 'raw')."""
        cursor = self._conn.execute("""
            SELECT * FROM reddit_threads
            WHERE status = 'raw'
            ORDER BY score DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor]

    def get_single_raw(self) -> RedditThreadRow | None:
        """Get single highest-scored unprocessed thread, or None if queue empty."""
        cursor = self._conn.execute("""
            SELECT * FROM reddit_threads
            WHERE status = 'raw'
            ORDER BY score DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_status(self, thread_id: str, status: str) -> None:
        """Update thread status (scraped, approved, rejected)."""
        self._conn.execute("""
            UPDATE reddit_threads
            SET status = ?
            WHERE thread_id = ?
        """, (status, thread_id))
        self._conn.commit()

class RedditThreadRepositorySingleton:
    """Singleton repository for reddit thread data access."""
    _repo: RedditThreadRepository | None = None

    def __new__(cls) -> RedditThreadRepository:
        if cls._repo is None:
            cls._repo = RedditThreadRepository()
        return cls._repo