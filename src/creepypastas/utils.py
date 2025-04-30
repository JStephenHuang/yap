from pathlib import Path
from typing import Union


def ensure_dir(path: Union[str, Path]) -> None:
    """
    Make sure that `path` exists as a directory.
    If it already exists, do nothing.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
