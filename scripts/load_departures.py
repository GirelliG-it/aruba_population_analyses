"""
Load departures by country of birth and sex (Table 1.12) into DuckDB.
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

SOURCE_FILE = "Table-1.12-Departures-by-country-of-birth-and-sex.xlsx"
PARQUET_NAME = "departures.parquet"
VIEW_NAME = "departures"
TOTALS_PARQUET_NAME = "departures_total.parquet"
TOTALS_VIEW_NAME = "departures_total"

TOTALS_LABEL = "Total Departures:"  # confirmed via DuckDB distinct-country check
EXCLUDE_LABELS: list[str] = []  # no stray stats rows found in this source file


def load_raw(source_file: str = SOURCE_FILE, raw_dir: Path = DATA_RAW) -> pd.DataFrame:
    """Load the raw CBS Excel file, skipping the title row above the header."""
    path = raw_dir / source_file
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")
    return pd.read_excel(path, skiprows=1, header=None)


def clean_and_reshape(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reshape from wide (year_sex columns) to tidy long format.

    Returns (country_df, totals_df) — the totals row is split out and
    persisted separately rather than mixed in with country-level data.
    """
    year_row = pd.to_numeric(raw_df.iloc[0], errors="coerce").ffill()
    sex_row = raw_df.iloc[1]

    new_columns = [
        "Country" if sex == "Country" else f"{int(year)}_{sex}"
        for year, sex in zip(year_row, sex_row)
    ]

    df = raw_df.iloc[2:].copy()
    df.columns = new_columns
    df = df.dropna(how="all").reset_index(drop=True)

    df = df[~df["Country"].astype(str).str.startswith("Source:", na=False)].reset_index(drop=True)

    tidy = df.melt(id_vars="Country", var_name="year_sex", value_name="value")
    tidy[["year", "sex"]] = tidy["year_sex"].str.split("_", expand=True)
    tidy = tidy.drop(columns="year_sex")

    tidy["year"] = pd.to_numeric(tidy["year"], errors="coerce").astype("Int64")
    tidy["value"] = pd.to_numeric(tidy["value"], errors="coerce")

    totals = tidy[tidy["Country"] == TOTALS_LABEL].copy()
    tidy = tidy[tidy["Country"] != TOTALS_LABEL]

    if EXCLUDE_LABELS:
        tidy = tidy[~tidy["Country"].isin(EXCLUDE_LABELS)]
    tidy = tidy.dropna(subset=["Country"])

    tidy["value"] = tidy["value"].astype("Int64")
    totals["value"] = totals["value"].astype("Int64")

    tidy = tidy.rename(columns={"Country": "country"})
    tidy = tidy[["country", "year", "sex", "value"]].sort_values(
        ["country", "year", "sex"]
    ).reset_index(drop=True)

    totals = totals.rename(columns={"Country": "country"})[["year", "sex", "value"]]

    if totals.empty:
        raise ValueError(
            f"No rows matched TOTALS_LABEL={TOTALS_LABEL!r} — check the exact "
            "label text in the source sheet (e.g. trailing colon, spacing)."
        )

    return tidy, totals


def validate(tidy_df: pd.DataFrame, totals_df: pd.DataFrame) -> None:
    """Confirm country-level sums reconcile against reported totals."""
    check = (
        tidy_df.groupby(["year", "sex"])["value"]
        .sum()
        .reset_index()
        .rename(columns={"value": "computed_total"})
    )
    validation = check.merge(totals_df, on=["year", "sex"], how="left", indicator=True)

    missing = validation[validation["_merge"] != "both"]
    if not missing.empty:
        raise ValueError(f"No matching totals row for:\n{missing}")

    mismatches = validation[validation["computed_total"] != validation["value"]]
    if not mismatches.empty:
        raise ValueError(f"Country sums do not reconcile with totals:\n{mismatches}")

    logger.info(
        "Validation passed: %d year/sex combinations reconcile.", len(validation)
    )


def persist(tidy_df: pd.DataFrame, totals_df: pd.DataFrame) -> None:
    """Save both tables to parquet and register them in DuckDB."""
    db_path = DB_FILES / "aruba.duckdb"

    country_parquet = save_to_parquet(tidy_df, PARQUET_NAME, base_dir=DATA_PROCESSED)
    register_in_duckdb(country_parquet, VIEW_NAME, db_path=db_path)
    logger.info("Parquet saved: %s", country_parquet)
    logger.info("DuckDB table registered: %s", VIEW_NAME)

    totals_parquet = save_to_parquet(totals_df, TOTALS_PARQUET_NAME, base_dir=DATA_PROCESSED)
    register_in_duckdb(totals_parquet, TOTALS_VIEW_NAME, db_path=db_path)
    logger.info("Parquet saved: %s", totals_parquet)
    logger.info("DuckDB table registered: %s", TOTALS_VIEW_NAME)


def smoke_test() -> pd.DataFrame:
    """Re-query both tables FROM DuckDB and re-validate."""
    con = duckdb.connect(str(DB_FILES / "aruba.duckdb"))
    country_df = con.execute(f"SELECT * FROM {VIEW_NAME}").df()
    totals_df = con.execute(f"SELECT * FROM {TOTALS_VIEW_NAME}").df()
    con.close()

    logger.info(
        "%s: %d rows, %d countries, years %d\u2013%d",
        VIEW_NAME,
        len(country_df),
        country_df["country"].nunique(),
        country_df["year"].min(),
        country_df["year"].max(),
    )

    check = (
        country_df.groupby(["year", "sex"])["value"]
        .sum()
        .reset_index()
        .rename(columns={"value": "computed_total"})
    )
    validation = check.merge(totals_df, on=["year", "sex"], how="left", indicator=True)

    missing = validation[validation["_merge"] != "both"]
    if not missing.empty:
        raise AssertionError(f"Smoke test FAILED \u2014 no totals row for:\n{missing}")

    mismatches = validation[validation["computed_total"] != validation["value"]]
    if not mismatches.empty:
        raise AssertionError(f"Smoke test FAILED \u2014 reconciliation mismatch:\n{mismatches}")

    logger.info("Smoke test PASSED: all %d year/sex combinations reconcile.", len(validation))
    return country_df


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    raw_df = load_raw()
    tidy_df, totals_df = clean_and_reshape(raw_df)
    validate(tidy_df, totals_df)
    persist(tidy_df, totals_df)
    smoke_test()


if __name__ == "__main__":
    main()
