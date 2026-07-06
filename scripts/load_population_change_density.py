"""
Load population change & density (Table 1.1) into DuckDB.
"""
import logging
import sys
from pathlib import Path

import duckdb
import pandas as pd

logging.getLogger("config.project_paths").setLevel(logging.WARNING)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.project_paths import DATA_RAW, DATA_PROCESSED, DB_FILES
from src.data_loader import save_to_parquet, register_in_duckdb

logger = logging.getLogger(__name__)

SOURCE_FILE = "Table-1.1-Population-population-change-and-population-density.xlsx"
PARQUET_FILE = "population_change_density.parquet"
TABLE_NAME = "population_change_density"

WANTED_ROWS = [
    "Total population1",
    " - males",
    " - females",
    "Annual rate of population change (%)²",
    "Density of population (inhabitants/km²)³",
    "Males per 1000  females",
]

RENAME_MAP = {
    " - females": "population_female",
    " - males": "population_male",
    "Annual rate of population change (%)²": "annual_change_pct",
    "Density of population (inhabitants/km²)³": "density_per_km2",
    "Males per 1000  females": "males_per_1000_females",
    "Total population1": "population_total",
}


def load_raw(source_file: str = SOURCE_FILE, raw_dir: Path = DATA_RAW) -> pd.DataFrame:
    """Load the raw CBS Excel file, skipping the title row above the header."""
    df = pd.read_excel(raw_dir / source_file, header=1)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df.columns = [c.strip() if isinstance(c, str) else str(c) for c in df.columns]
    df = df.rename(columns={"Unnamed: 0": "indicator"})
    return df


def clean_and_reshape(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Filter to the wanted indicator rows, melt to long, pivot to wide (one row per year)."""
    selected = raw_df.loc[raw_df["indicator"].isin(WANTED_ROWS)].copy()

    if selected.shape[0] != len(WANTED_ROWS):
        missing = set(WANTED_ROWS) - set(selected["indicator"])
        raise ValueError(
            f"Expected {len(WANTED_ROWS)} indicator rows, got {selected.shape[0]}. "
            f"Missing: {missing}"
        )

    tidy = selected.melt(id_vars="indicator", var_name="year", value_name="value")
    tidy["year"] = tidy["year"].astype(int)

    wide = tidy.pivot(index="year", columns="indicator", values="value").reset_index()
    wide.columns.name = None
    wide = wide.rename(columns=RENAME_MAP)
    return wide


def validate(wide_df: pd.DataFrame) -> pd.DataFrame:
    """Check male + female sums reconcile against reported total population."""
    check_total = wide_df["population_female"] + wide_df["population_male"]
    discrepancies = wide_df[abs(check_total - wide_df["population_total"]) > 1.0]

    if discrepancies.empty:
        logger.info("Validation passed: male + female sums match population_total.")
    else:
        logger.warning("Discrepancies found:\n%s", discrepancies[["year", "population_total"]])

    return wide_df


def persist(wide_df: pd.DataFrame) -> Path:
    """Save to parquet and register as a DuckDB table."""
    parquet_path = save_to_parquet(wide_df, PARQUET_FILE, base_dir=DATA_PROCESSED)
    register_in_duckdb(parquet_path, TABLE_NAME, db_path=DB_FILES / "aruba.duckdb")
    logger.info("Parquet saved: %s", parquet_path)
    logger.info("DuckDB table registered: %s", TABLE_NAME)
    return parquet_path


def smoke_test() -> pd.DataFrame:
    """Query the table back from DuckDB to confirm it loaded correctly."""
    con = duckdb.connect(str(DB_FILES / "aruba.duckdb"))
    result = con.execute(f"SELECT * FROM {TABLE_NAME} ORDER BY year").df()
    con.close()
    logger.info("Smoke test: %s rows retrieved from '%s'", result.shape[0], TABLE_NAME)
    return result


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    raw_df = load_raw()
    wide_df = clean_and_reshape(raw_df)
    wide_df = validate(wide_df)
    persist(wide_df)
    smoke_test()


if __name__ == "__main__":
    main()
