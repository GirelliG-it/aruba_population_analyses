import logging
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data_loader import load_excel_file


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    dataframe = load_excel_file("Demographic-aspects-2023.xlsx")
    logging.info(
        "Successfully loaded Demographic-aspects-2023.xlsx with shape %s",
        dataframe.shape,
    )


if __name__ == "__main__":
    main()
