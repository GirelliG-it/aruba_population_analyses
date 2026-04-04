# Create CSV file, load and write to SQLite
# Perform validation check

import sqlite3
from pathlib import Path

import pandas as pd


CSV_PATH = Path("data/processed/population_change_by_sex.csv")
DB_PATH = Path("outputs/db_files/aruba.db")
TABLE_NAME = "population_change_by_sex"

EXPECTED_COLUMNS = ["sex", "year", "population", "annual_change"]
EXPECTED_SEX_VALUES = {"Males", "Females"}


def drop_unnamed_columns(df: pd.DataFrame) -> pd.DataFrame:
    unnamed_columns = [col for col in df.columns if col.startswith("Unnamed:")]
    if unnamed_columns:
        print(f"Dropping unwanted columns: {unnamed_columns}")
        df = df.drop(columns=unnamed_columns)
    return df


def validate_columns(df: pd.DataFrame) -> None:
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    extra_columns = [col for col in df.columns if col not in EXPECTED_COLUMNS]

    if missing_columns:
        raise ValueError(f"Missing expected columns: {missing_columns}")

    if extra_columns:
        raise ValueError(f"Unexpected extra columns: {extra_columns}")

    print("Column validation passed.")


def validate_dtypes_and_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["year"] = pd.to_numeric(df["year"], errors="raise")
    df["population"] = pd.to_numeric(df["population"], errors="raise")
    df["annual_change"] = pd.to_numeric(df["annual_change"], errors="coerce")

    found_sex_values = set(df["sex"].dropna().unique())
    if found_sex_values != EXPECTED_SEX_VALUES:
        raise ValueError(
            f"Unexpected sex values: {found_sex_values}. "
            f"Expected: {EXPECTED_SEX_VALUES}"
        )

    df = df.sort_values(["sex", "year"]).reset_index(drop=True)

    nan_counts = df.groupby("sex")["annual_change"].apply(lambda s: s.isna().sum())

    for sex, count in nan_counts.items():
        if count != 1:
            raise ValueError(
                f"{sex} should have exactly 1 NaN in annual_change, found {count}"
            )

    for sex in EXPECTED_SEX_VALUES:
        subset = df[df["sex"] == sex].sort_values("year")
        first_year = subset.iloc[0]["year"]
        first_annual_change = subset.iloc[0]["annual_change"]

        if not pd.isna(first_annual_change):
            raise ValueError(
                f"First annual_change for {sex} in year {first_year} should be NaN"
            )

    print("Data type and value validation passed.")
    return df


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV_PATH)

    df = drop_unnamed_columns(df)
    validate_columns(df)
    df = df[EXPECTED_COLUMNS]
    df = validate_dtypes_and_values(df)

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

        row_count = pd.read_sql(
            f"SELECT COUNT(*) AS n FROM {TABLE_NAME}",
            conn
        )
        print("Load to SQLite passed.")
        print(row_count)


if __name__ == "__main__":
    main()