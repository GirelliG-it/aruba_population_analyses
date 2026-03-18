#############################################
# Data analysis project Capstone 1
# Configuration file for project paths
# Data: Wed, Mar 18, 2026
#############################################

from pathlib import Path


# Resolve project root
cwd = Path.cwd()
ROOT = cwd.parent if cwd.name == "notebooks" else cwd


# Core directories
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"


# Project=-wide constants
YEAR_MIN = 2010
YEAR_MAX = 2024


# Ensure output directories exist
OUTPUTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)


# Definitions

def get_raw_data_path(filename: str) -> Path:
    path = DATA_RAW / filename
    if not path.exists():
        raise FileNotFoundError(f"{filename} not found in raw data folder")
    return path


def get_processed_data_path(filename: str) -> Path:
    path =  DATA_PROCESSED / filename
    if not path.exists():
        raise FileNotFoundError(f"{filename} not found in raw data folder")
    return path


def get_figure_path(filename: str) -> Path:
    path =  FIGURES / filename
    if not path.exists():
        raise FileNotFoundError(f"{filename} not found in raw data folder")
    return path


def validate_paths(paths: dict[str, Path]) -> None:
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing required file(s): {', '.join(missing)}"
        )



