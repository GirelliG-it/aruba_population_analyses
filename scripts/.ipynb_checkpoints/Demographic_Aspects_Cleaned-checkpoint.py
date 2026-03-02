#==============================================================
# File Key Demographic aspects from wide form to long form
# Tidy Format
# Fri, Feb 27, 2026
#==============================================================
# Import libraries

import pandas as pd
import matplotlib.pyplot as plt

# =============================================================
# 1. LOAD RAW DATA
# =============================================================
df1 = pd.read_excel(
    "/home/ggirelli/Documents/DataAnalysis/Datasets/Official_Open-Datasets_Aruba_CBS/Demographic-aspects-2023.xlsx",
    header=1
)

# =============================================================
# 2. CLEAN: strip whitespace, drop problematic row
# =============================================================
df1["Key Demographic aspects"] = df1["Key Demographic aspects"].astype(str).str.strip()
df1 = df1[df1["Key Demographic aspects"] != "Average age"].copy()

# =============================================================
# 3. MELT wide → long and rename columns
# =============================================================
df_long = (
    df1.melt(
        id_vars=["Key Demographic aspects", "Unit"],
        var_name="Year",
        value_name="Value"
    )
    .rename(columns={
        "Key Demographic aspects": "Indicator",
        "Unit": "Measurement"
    })
)

# =============================================================
# 4. FIX DTYPES
# =============================================================
df_long["Year"] = df_long["Year"].astype(int)
df_long["Value"] = pd.to_numeric(df_long["Value"], errors="coerce")

# =============================================================
# 5. CLEAN VALUES
# =============================================================
def clean_value(row):
    if pd.isna(row["Value"]):
        return 0
    if row["Measurement"] == "Absolute":
        return int(row["Value"])
    else:
        return float(row["Value"])

df_long["Value"] = df_long.apply(clean_value, axis=1)

# =============================================================
# 6. SPLIT INTO SUBSETS
# =============================================================
headcount_indicators = ["Males", "Females", "Total population"]

df_counts = df_long[df_long["Indicator"].isin(headcount_indicators)].copy()
df_counts["Value"] = df_counts["Value"].round(0).astype("Int64")

df_relative = df_long[~df_long["Indicator"].isin(headcount_indicators)].copy()

# =============================================================
# 7. INSPECT
# =============================================================
print("── df_long ──")
print(df_long)

print("\n── df_counts (headcounts only) ──")
print(df_counts)

print("\n── df_relative (ratios, density, etc.) ──")
print(df_relative)
