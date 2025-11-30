"""
SQLite database connection management.
"""

import sqlite3

from config.base import BaseConfig


class DatabaseConnectionSingleton:
    """
    Get SQLite connection (singleton).

    Returns:
        SQLite connection with row factory set to dict-like access.
    """
    _connection: sqlite3.Connection | None = None

    def __new__(cls) -> sqlite3.Connection:
        if cls._connection is None:
            cls._connection = init_connection()

        return cls._connection


def init_connection() -> sqlite3.Connection:
    """Initialize database connection."""
    config = BaseConfig()
    config.DB_PATH.mkdir(parents=True, exist_ok=True)
    db_path = config.DB_PATH / "threads.sqlite"

    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row

    print(f"Connected to database at {db_path}")

    return connection
