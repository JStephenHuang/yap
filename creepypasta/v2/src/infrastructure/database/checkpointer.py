"""
LangGraph checkpointer for state persistence.

Uses SQLite for durable storage of graph state, enabling:
- Interrupt/resume workflows
- Human-in-the-loop review cycles
- Crash recovery
"""

import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

from config.base import BaseConfig


def create_checkpointer() -> SqliteSaver:
    """
    Create SQLite checkpointer for graph state persistence.

    Returns:
        SqliteSaver configured with project database path.
    """
    config = BaseConfig()
    config.DB_PATH.mkdir(parents=True, exist_ok=True)
    checkpoint_path = config.DB_PATH / "checkpoints.sqlite"

    conn = sqlite3.connect(str(checkpoint_path), check_same_thread=False)
    return SqliteSaver(conn)
