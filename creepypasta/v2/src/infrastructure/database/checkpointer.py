"""
LangGraph checkpointer for state persistence.

Uses SQLite for durable storage of graph state, enabling:
- Interrupt/resume workflows
- Human-in-the-loop review cycles
- Crash recovery
- Time travel (re-run from specific steps)
"""

import sqlite3
from typing import Any

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.state import CompiledStateGraph

from config.base import BaseConfig


def create_checkpointer() -> SqliteSaver:
    """Create SQLite checkpointer for graph state persistence."""
    config = BaseConfig()
    config.DB_PATH.mkdir(parents=True, exist_ok=True)
    checkpoint_path = config.DB_PATH / "checkpoints.sqlite"

    conn = sqlite3.connect(str(checkpoint_path), check_same_thread=False)
    return SqliteSaver(conn)


def find_checkpoint_before_node(
    app: CompiledStateGraph,
    thread_id: str,
    target_node: str,
) -> dict | None:
    """
    Find the checkpoint recorded just before a target node executed.
    
    Returns the full config dict for that checkpoint, or None if not found.
    """
    config = {"configurable": {"thread_id": thread_id}}
    history = list(app.get_state_history(config))
    
    for snapshot in history:
        if target_node in snapshot.next:
            return snapshot.config
    
    return None


def update_state_at_checkpoint(
    app: CompiledStateGraph,
    checkpoint_config: dict,
    updates: dict[str, Any],
) -> None:
    """Update state at a specific checkpoint."""
    app.update_state(checkpoint_config, updates)


def get_checkpoint_history_summary(
    app: CompiledStateGraph,
    thread_id: str,
    limit: int = 10,
) -> list[dict]:
    """Get a summary of checkpoint history for debugging."""
    config = {"configurable": {"thread_id": thread_id}}
    history = list(app.get_state_history(config))
    
    return [
        {
            "next": snap.next,
            "checkpoint_id": snap.config["configurable"].get("checkpoint_id", "N/A")[:8],
        }
        for snap in history[:limit]
    ]
