"""
JSON storage utilities.
"""

import json
from pathlib import Path


def save_json(data: dict, filepath: str | Path) -> None:
    """Save dict to JSON file."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: str | Path) -> dict:
    """Load dict from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_metadata(run_dir: str | Path, state: dict) -> None:
    """
    Save current pipeline state to metadata.json in the run directory.

    Filters out control fields and saves only the meaningful output data.
    """
    serializable_fields = [
        "checkpoint_thread_id",
        "reddit_thread",
        "triage",
        "script",
        "scene_prompts",
        "thumbnail_prompt",
        "yt_title",
        "yt_description",
        "audio",
        "scene_images",
        "thumbnail",
        "video",
        "youtube_link",
        "status",
    ]

    metadata = {}
    for field in serializable_fields:
        if field in state and state[field] is not None:
            value = state[field]
            # Handle Pydantic models
            if hasattr(value, "model_dump"):
                metadata[field] = value.model_dump()
            else:
                metadata[field] = value

    save_json(metadata, Path(run_dir) / "metadata.json")
