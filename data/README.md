# Data

Raw data files are tracked in Git for reproducibility (CBS Aruba source links can be removed or replaced without notice). Processed data files are not tracked — they're regenerated from raw sources via the load step for each table.

## Raw files

All raw CBS Aruba source files live in `data/raw/`. For per-file retrieval dates, exact source URLs, and attribution requirements, see [`SOURCES.md`](raw/SOURCES.md).

Files are grouped by topic:

| Category | Tables | Example |
|---|---|---|
| Population & vital statistics | 1.1–1.13, Demographic aspects | Population change, births, deaths, marriages, domiciliation, departures |
| Health | 2.1–2.20 | Hospitals, causes of death, communicable diseases, family planning |
| Elections | 4.1–4.3 | Parliament results, party composition |
| Labor & employment | 6.1, 6.4–6.16 | Unemployment/participation rates, government employment by ministry |
| Wages & economy | 7.2–7.7, Macro-economic aspects | Registered jobs, monthly wages, regional company distribution |
| Geography & administrative boundaries | GAC (Geografische Adressen Classificatie) | Neighborhoods, street names, geographic address classification |

CBS Aruba data is free to use with source attribution; non-commercial use only. See `SOURCES.md` for the full attribution line.

## Generated files

Each table has its own dedicated load step that cleans and reshapes the raw source into a parquet file and registers it as a DuckDB table. Tables are being migrated from notebooks to standalone scripts one at a time:

**Converted to scripts** (`scripts/`):
- `load_population_change_density.py` (Table 1.1)
- `load_domiciliation.py` (Table 1.11)

**Still notebook-based** (`notebooks/load/`):
- All other tables not yet converted

To regenerate a table's processed data, run its script (`python scripts/load_domiciliation.py`) if converted, or its notebook otherwise.

A unified `scripts/run_all.py` entry point is planned once all load steps are converted and stabilized (see main [README.md](../README.md)).
