import argparse
import logging
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.project_paths import DATA_PROCESSED, DATA_RAW
from src.data_loader import load_excel_file


DEFAULT_INPUT_FILE = "Demographic-aspects-2023.xlsx"
DEFAULT_OUTPUT_FILE = "demographic_aspects_2023.csv"


def parse_sheet_name(value: str) -> int | str:
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return value


def validate_dataframe(dataframe: pd.DataFrame, input_file: str) -> None:
    logging.info("Validating loaded dataframe")

    if dataframe.empty:
        raise ValueError(f"{input_file} loaded as an empty dataframe")

    if dataframe.shape[1] == 0:
        raise ValueError(f"{input_file} loaded with zero columns")

    logging.info("Dataframe validation passed with shape %s", dataframe.shape)


def run_pipeline(
    input_file: str = DEFAULT_INPUT_FILE,
    output_file: str = DEFAULT_OUTPUT_FILE,
    raw_dir: str | Path = DATA_RAW,
    output_dir: str | Path = DATA_PROCESSED,
    sheet_name: int | str = 0,
) -> Path:
    raw_path = Path(raw_dir)
    output_path = Path(output_dir)

    logging.info("Loading raw Excel file: %s", raw_path / input_file)
    dataframe = load_excel_file(input_file, sheet_name=sheet_name, base_dir=raw_path)

    validate_dataframe(dataframe, input_file)

    output_path.mkdir(parents=True, exist_ok=True)
    csv_path = output_path / output_file

    logging.info("Saving processed CSV: %s", csv_path)
    dataframe.to_csv(csv_path, index=False)

    if not csv_path.exists():
        raise FileNotFoundError(f"Processed CSV was not created: {csv_path}")

    logging.info("Verified processed CSV exists: %s", csv_path)
    logging.info(
        "Pipeline completed successfully with dataframe shape %s",
        dataframe.shape,
    )

    return csv_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Aruba data pipeline.")
    parser.add_argument("--input-file", default=DEFAULT_INPUT_FILE)
    parser.add_argument("--output-file", default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--raw-dir", default=DATA_RAW, type=Path)
    parser.add_argument("--output-dir", default=DATA_PROCESSED, type=Path)
    parser.add_argument("--sheet-name", default=0, type=parse_sheet_name)
    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    args = build_parser().parse_args()
    run_pipeline(
        input_file=args.input_file,
        output_file=args.output_file,
        raw_dir=args.raw_dir,
        output_dir=args.output_dir,
        sheet_name=args.sheet_name,
    )


if __name__ == "__main__":
    main()
