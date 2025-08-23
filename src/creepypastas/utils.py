from pathlib import Path
from typing import Union
import csv

import pandas as pd


def ensure_dir(path: Union[str, Path]) -> None:
    """
    Make sure that `path` exists as a directory.
    If it already exists, do nothing.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)


def save(csv_path: Path, df: pd.DataFrame) -> None:
    """
    Save the DataFrame to a CSV file.
    """
    df.to_csv(csv_path, index=False, quoting=csv.QUOTE_ALL)


def find_thread(thread_id: str, df: pd.DataFrame) -> tuple[pd.Series, int]:
    """
    Find a thread by its ID in the DataFrame.

    Returns:
        idx: The index of the thread (row).
        data: The data of the thread (row).
    """
    result = df[df["thread_id"] == thread_id]
    if result.empty:
        raise Exception(f"Thread {thread_id} not found in DataFrame")

    row = result.iloc[0]
    idx = result.index[0]

    return row, idx
