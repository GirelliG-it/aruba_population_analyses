"""
src/data_loader.py

Loading and cleaning Excel files.
Also handles persisting cleaned DataFrames to parquet
and registering them as DuckDB tables.
"""
from pathlib import Path
import logging
import re
import pandas as pd
import duckdb
from typing import Union

from config.project_paths import DATA_RAW, DATA_PROCESSED, DB_FILES

logger = logging.getLogger(__name__)

def load_excel_file(
    filename: str,
    sheet_name: Union[int, str] = 0,
    base_dir: Union[Path, None] = None
) -> pd.DataFrame:
    """Load an Excel file from the specified directory."""
    base_dir = base_dir if base_dir is not None else DATA_RAW
    file_path = base_dir / Path(filename)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Expected Excel file '{filename}' was not found. "
            f"Looked in: {base_dir}. "
            "Raw data files are not tracked by Git; place local source files "
            "in data/raw or pass a fixture directory in CI."
        )

    try:
        dataframe = pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        raise ValueError(f"Failed to load sheet '{sheet_name}' from {file_path}: {e}") from e

    dataframe = dataframe.dropna(how="all").dropna(axis=1, how="all")
    dataframe.columns = [
        col.strip() if isinstance(col, str) else str(col)
        for col in dataframe.columns
    ]

    logger.info(f"Loaded {filename} from {file_path} with shape {dataframe.shape}")
    return dataframe


def save_to_parquet(
    df: pd.DataFrame,
    filename: str,
    base_dir: Union[Path, None] = None,
) -> Path:
    """Persist a DataFrame to parquet in data/processed."""
    out_dir =  base_dir if base_dir is not None else DATA_PROCESSED
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    df.to_parquet(out_path, index=False)
    logger.info(f"Saved parquet to {out_path}")
    return out_path


def register_in_duckdb(
    parquet_path: Path,
    table_name: str,
    db_path: Union[Path, None] = None,
) -> None:
    """Register a parquet file as a view in the persistent DuckDB database."""
    if not table_name.isidentifier():
        raise ValueError(
            f"'{table_name}' is not a safe table name. "
            "Use only letters, digits and underscores, and do not start with a digit. "
        )
    
    db_file = db_path if db_path is not None else DB_FILES / "aruba.duckdb"

    con = duckdb.connect(str(db_file))
    con.execute(
        f"CREATE OR REPLACE VIEW {table_name} AS "
        f"SELECT * FROM read_parquet('{parquet_path}')"
    )
    con.close()
    logger.info(f"Registered '{table_name}' in DuckDB at {db_file}")
