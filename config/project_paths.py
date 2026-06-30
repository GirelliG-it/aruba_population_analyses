"""
Configuration file for project paths.
Uses environment variables for flexibility and includes error handling and logging.
"""
from pathlib import Path
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allow overriding the project root via environment variable
ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).parent.parent))

# Define project directories
DATA_RAW: Path = ROOT / "data" / "raw"
DATA_PROCESSED: Path = ROOT / "data" / "processed"
DATA_EXTERNAL: Path = ROOT / "data" / "external"
LOGS_DIR: Path = ROOT / "logs"
FIGURES: Path = ROOT / "outputs" / "figures"
DB_FILES: Path = ROOT / "outputs" / "db_files"

# Ensure directories exist with error handling
for path in [DATA_RAW, DATA_PROCESSED, DATA_EXTERNAL, LOGS_DIR, FIGURES, DB_FILES]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {path}")
    except PermissionError as e:
        logger.error(f"Permission denied creating directory {path}: {e}")
        raise RuntimeError(f"Failed to create directory {path}: Permission denied") from e
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise RuntimeError(f"Failed to create directory {path}: {e}") from e
