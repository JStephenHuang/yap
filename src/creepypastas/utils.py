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
