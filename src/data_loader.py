from pathlib import Path

import pandas as pd

from config.project_paths import DATA_RAW


def load_excel_file(
    filename: str,
    sheet_name: int | str = 0,
    base_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Load an Excel sheet from the raw data directory."""
    raw_dir = Path(base_dir) if base_dir is not None else DATA_RAW
    file_path = raw_dir / Path(filename)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Expected Excel file '{filename}' was not found. "
            f"Looked in: {raw_dir}. "
            "Raw data files are not tracked by Git; place local source files "
            "in data/raw or pass a fixture directory in CI."
        )

    dataframe = pd.read_excel(file_path, sheet_name=sheet_name)
    dataframe = dataframe.dropna(how="all").dropna(axis=1, how="all")
    dataframe.columns = [
        column.strip() if isinstance(column, str) else column
        for column in dataframe.columns
    ]

    return dataframe
