"""
SQLite database connection management.
"""

import sqlite3
from pathlib import Path

from config.base import BaseConfig

# Compute path relative to this file: infrastructure/database/ -> src/data/

_connection: sqlite3.Connection | None = None


class DatabaseConnectionSingleton():
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

def init_connection() -> None:
    """Initialize database schema."""
    db_path = BaseConfig().DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row

    print("Connected to database at", db_path)
    
    return connection


