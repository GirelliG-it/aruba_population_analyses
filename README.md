# Demographic Shifts & Workforce Aging in Aruba (2015–2023)  
   
This project explores structural demographic changes in Aruba between 2015 and 2023, with a specific focus on workforce aging and its broader societal implications.  
   
## Results / Key Findings

- Aruba’s total population increased through 2019, declined sharply from 2020 onward, and showed a modest recovery in 2023.
- The most severe contraction appears in 2020, making it a clear turning point in the series.
- Year-over-year population change suggests that female population change was more volatile than male change over the period shown.

<p align="center">
  <img src="outputs/figures/aruba_total_population_2015_2023.png"
       alt="Aruba total population over time, 2015 to 2023"
       width="48%">
  <img src="outputs/figures/annual_population_change_rate_2015_2023.png"
       alt="Annual population change rate in Aruba, 2015 to 2023"
       width="48%">
</p>

<p align="center">
  <em>Figures 1 and 2: Total population trend and annual population change rate.</em>
</p>

<p align="center">
  <img src="outputs/figures/yoy_population_change_by_sex_2016_2023.png"
       alt="Year-over-year population change by sex in Aruba"
       width="75%">
</p>

<p align="center">
  <em>Figure 3. Year-over-year population change by sex.</em>
</p>

---

## Project Overview

**Motivation**  
My interest in this project is rooted in a desire to contribute to the long-term wellbeing of Aruba as a nation.  
Rather than focusing on commercial analytics or short-term business metrics, this work centers on population structure, workforce sustainability, and potential systemic pressures that may shape daily life in Aruba over the coming decades.  
By analyzing official datasets from the Central Bureau of Statistics (CBS), this project seeks to:  
- Identify trends in working-age population structure  
- Measure changes in age distribution over time  
- Explore aging-related dependency ratios  
- Examine connections between demographic shifts and potential healthcare or labor pressures  
This project is driven by curiosity, civic responsibility, and a commitment to evidence-based thinking.  


**Approach**  
The analysis will proceed in structured phases:  
1. Exploratory Data Analysis (EDA) in Google Sheets for pattern recognition  
2. Data transformation (wide → long format) for analytical flexibility  
3. Construction of a unified panel dataset (Year × Age Group)  
4. Calculation of structural indicators such as:  
- Workforce composition  
- Old-age dependency ratio  
- Age cohort shifts  
- Hospitalization rates per 1,000 population (planned) 

The goal is not to generate flashy dashboards, but to build a clear, reproducible, and policy-relevant analysis.  


## Data Sources

Primary datasets include:  
- Age distribution of the end-of-year population  
- Live births by age of mother  
- Teenage motherhood statistics  
- Life expectancy by age and sex  
- Country of birth (domiciliation data)  
- (Planned) Hospitalization data by age group  
All data originates from the [Central Bureau of Statistics Aruba](https://cbs.aw)


## Guiding Question

What demographic patterns in Aruba between 2015 and 2023 may signal long-term structural pressure on the workforce and healthcare system?  


## Project Status

Currently in the exploratory and pipeline-hardening phase. Data cleaning, reshaping, and structural indicator calculations are in progress.


## Stack

- Python (pandas, Polars) in VS Code
- DuckDB / parquet
- Jupyter Notebook / JupyterLab
- Google Sheets (informal, quick-look exploration only — not part of the pipeline)
- Git / GitHub


## Project Structure

```text
cbs_aruba/
├── .github/
│   └── workflows/
├── config
├── data
│   ├── processed
│   ├── raw
│   └── README.md
├── environment.yml
├── Makefile
├── notebooks
├── outputs
│   ├── db_files
│   ├── figures
│   └── tables
└── src
```


---

## Reproducibility

Raw source files and processed data files are not tracked in Git. Required CBS
Aruba source files should be placed in `data/raw/`. See `data/README.md` for
the current list of expected input files.

Create the Conda environment from `environment.yml`:

```bash
conda env create -f environment.yml
conda activate aruba-population-analysis
```

Update an existing environment after dependency changes:

```bash
conda env update -f environment.yml --prune
```

### Running the pipeline

Each dataset currently has its own load step under `notebooks/load/`. Place
the required CBS Aruba source files in `data/raw/`, then run the relevant
load notebook/script for the table you need. A single unified entry point
(`scripts/run_all.py`) is planned once all load steps are converted and
stable.

## Local Development Workflow

Common local checks are available through the Makefile:

```bash
make compile
```

- `make compile` compiles Python files in `config`, `src`, and `scripts`.

A fixture-based smoke test (previously built around a since-deprecated
pipeline) will be rebuilt to match the current DuckDB/parquet architecture.

## Continuous Integration

The CI workflow creates the Conda environment from `environment.yml`,
verifies that core dependencies import correctly, and compiles the Python
modules in `config`, `src`, and `scripts` to catch syntax errors early.
