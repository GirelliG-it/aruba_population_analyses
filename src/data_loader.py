from pathlib import Path

import pandas as pd

from config.project_paths import DATA_RAW


def load_excel_file(filename, sheet_name=0):
    """Load an Excel sheet from the raw data directory."""
    file_path = DATA_RAW / Path(filename)

    if not file_path.exists():
        print(f"Error: required Excel file is missing: {filename}")
        print(f"Place it in the raw data directory: {DATA_RAW}")
        return pd.DataFrame()

    dataframe = pd.read_excel(file_path, sheet_name=sheet_name)
    dataframe = dataframe.dropna(how="all").dropna(axis=1, how="all")
    dataframe.columns = [
        column.strip() if isinstance(column, str) else column
        for column in dataframe.columns
    ]

    return dataframe
