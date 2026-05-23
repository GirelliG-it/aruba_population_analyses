import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config.project_paths import DATA_PROCESSED, DATA_RAW


def _read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)

    if suffix in {".xls", ".xlsx"}:
        return pd.read_excel(path)

    raise ValueError(f"Unsupported table format: {path}")


def load_and_verify_tables(
    filenames: list[str],
    base_dir=DATA_RAW,
) -> dict[str, pd.DataFrame]:
    """Load tables from raw or processed data."""
    base_path = Path(base_dir)
    loaded_dfs = {}

    for filename in filenames:
        path = base_path / filename
        if not path.exists():
            logging.critical("Required data file is missing: %s", path)
            raise FileNotFoundError(path)

        loaded_dfs[filename] = _read_table(path)
        logging.info(
            "Loaded %s with shape %s",
            filename,
            loaded_dfs[filename].shape,
        )

    return loaded_dfs
