import logging
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.project_paths import DATA_PROCESSED
from src.data_loader import load_excel_file


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

RAW_FILENAME = "Demographic-aspects-2023.xlsx"
PROCESSED_FILENAME = "demographic_aspects_2023.csv"
EXPECTED_SHAPE = (13, 11)


def main():
    logging.info("Loading raw Excel file: data/raw/%s", RAW_FILENAME)
    dataframe = load_excel_file(RAW_FILENAME)

    logging.info("Validating loaded dataframe")
    if dataframe.empty:
        raise ValueError(f"{RAW_FILENAME} loaded as an empty dataframe")
    if dataframe.shape != EXPECTED_SHAPE:
        raise ValueError(
            f"{RAW_FILENAME} shape is {dataframe.shape}, expected {EXPECTED_SHAPE}"
        )
    logging.info("Dataframe validation passed with shape %s", dataframe.shape)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    output_path = DATA_PROCESSED / PROCESSED_FILENAME

    logging.info("Saving processed CSV: data/processed/%s", PROCESSED_FILENAME)
    dataframe.to_csv(output_path, index=False)
    if not output_path.exists():
        raise FileNotFoundError(f"Processed CSV was not created: {output_path}")
    logging.info("Verified processed CSV exists: data/processed/%s", PROCESSED_FILENAME)

    logging.info(
        "Pipeline completed successfully with dataframe shape %s",
        dataframe.shape,
    )


if __name__ == "__main__":
    main()
