# Data

Raw and processed data files are not tracked in Git.

## Required raw files

Place the following file in `data/raw/` before running the pipeline:

- `Demographic-aspects-2023.xlsx`

Source: Central Bureau of Statistics Aruba  
Used by: `scripts/run_pipeline.py`

## Generated files

The pipeline generates:

- `data/processed/demographic_aspects_2023.csv`

To regenerate processed data, run:

```bash
python scripts/run_pipeline.py
```
