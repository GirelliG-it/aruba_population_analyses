"""
Load domiciliation by country of birth and sex (Table 1.11) into DuckDB.
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

SOURCE_FILE = "Table-1.11-Domiciliation-by-country-of-birth-and-sex.xlsx"
PARQUET_NAME = "domiciliation.parquet"
VIEW_NAME = "domiciliation"
TOTALS_PARQUET_NAME = "domiciliation_total.parquet"
TOTALS_VIEW_NAME = "domiciliation_total"

TOTALS_LABEL = "Total Domiciliation:"  # note the trailing colon — matches the source sheet
EXCLUDE_LABELS = ["MEAN", "ST.DEV.P", "MIN", "MAX"]


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
    df = raw_df.dropna(how="all").copy()

    # The sheet has two header rows: a year row (set only over the "Male"
    # half of each year's pair, e.g. `nan, 2015, nan, 2016, ...`) and a
    # label row (`Country, Male, Female, Male, Female, ...`). Merge them
    # into single column names like "2015_Male" — the "Country" column
    # has no year above it, so it's kept as-is.
    years = pd.to_numeric(df.iloc[0], errors="coerce").ffill()
    labels = df.iloc[1]
    df.columns = [
        label if pd.isna(year) else f"{int(year)}_{label}"
        for year, label in zip(years, labels)
    ]
    df = df.iloc[2:].reset_index(drop=True)

    df = df[~df["Country"].astype(str).str.startswith("Source:", na=False)].reset_index(drop=True)

    tidy = df.melt(id_vars="Country", var_name="year_sex", value_name="value")
    tidy[["year", "sex"]] = tidy["year_sex"].str.split("_", expand=True)
    tidy = tidy.drop(columns="year_sex")

    # Cast once, here — before splitting totals off, so both totals and
    # country rows end up with the same, correct dtype.
    tidy["year"] = pd.to_numeric(tidy["year"], errors="coerce").astype("Int64")
    tidy["value"] = pd.to_numeric(tidy["value"], errors="coerce")

    totals = tidy[tidy["Country"] == TOTALS_LABEL].copy()
    tidy = tidy[tidy["Country"] != TOTALS_LABEL]

    # Drop ad-hoc stats rows left in the source sheet
    tidy = tidy[~tidy["Country"].isin(EXCLUDE_LABELS)]
    tidy = tidy.dropna(subset=["Country"])

    # Safe to cast to Int64 now — no non-integer floats remain
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
    """Confirm country-level sums reconcile against reported totals.

    Uses a LEFT merge (not inner) so a missing totals row shows up as a
    visible gap instead of silently vanishing from the comparison.
    """
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
    """Re-query both tables FROM DuckDB and re-validate — proves the
    persisted data is correct, not just the in-memory computation."""
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
        raise AssertionError(f"Smoke test FAILED — no totals row for:\n{missing}")

    mismatches = validation[validation["computed_total"] != validation["value"]]
    if not mismatches.empty:
        raise AssertionError(f"Smoke test FAILED — reconciliation mismatch:\n{mismatches}")

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
