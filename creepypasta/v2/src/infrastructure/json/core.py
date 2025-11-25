"""
JSON storage utilities.
"""

import json
from pathlib import Path
from typing import Iterator


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


def append_jsonl(data: dict, filepath: str | Path) -> None:
    """Append dict to JSONL file (one JSON object per line)."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def load_jsonl(filepath: str | Path) -> Iterator[dict]:
    """Load dicts from JSONL file."""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)
