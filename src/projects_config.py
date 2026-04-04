from pathlib import Path

# Resolve project root from this file location
ROOT = Path(__file__).resolve().parents[1]

# Core directories
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
OUTPUTS = ROOT / "outputs"

# Project-wide constants
YEAR_MIN = 2015
YEAR_MAX = 2023

# Ensure output-style directories exist
for folder in [DATA_PROCESSED, FIGURES, OUTPUTS]:
    folder.mkdir(parents=True, exist_ok=True)


def get_raw_data_path(filename: str) -> Path:
    """Return full path to a raw data file."""
    return DATA_RAW / filename


def get_processed_data_path(filename: str) -> Path:
    """Return full path to a processed data file."""
    return DATA_PROCESSED / filename


def get_figure_path(filename: str) -> Path:
    """Return full path to a figure file."""
    return FIGURES / filename


def get_output_path(filename: str) -> Path:
    """Return full path to an output file."""
    return OUTPUTS / filename
