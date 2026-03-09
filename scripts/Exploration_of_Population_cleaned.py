# Exploration of Population Data between 2015-2023
# Source: Central Bureau of Statistics Aruba
# Project started: Wed, Feb 25, 2026
# -------------------------------------------------
# Goal: reshape two wide-format Excel sheets into a single
#       tidy long-form DataFrame ready for visualisation.

import pandas as pd
import matplotlib.pyplot as plt

# =============================================================
# 1. LOAD RAW DATA
# =============================================================
# Both sheets use row 1 (0-indexed) as the real header → header=1
df1 = pd.read_excel("Demographic-aspects-2023.xlsx", header=1)
df2_raw = pd.read_excel(
    "Table-1_9-Relative-population-by-age-groups-in-percentage.xlsx",
    header=1
)

# =============================================================
# 2. CLEAN df1 → extract total population per year
# =============================================================
# Normalise the text column to avoid invisible-whitespace mismatches
df1["Key Demographic aspects"] = (
    df1["Key Demographic aspects"].astype(str).str.strip()
)

# NOTE: the actual label in the file is "Total population" (with a space),
# not "Total_population" as in the original script – that was the bug!
df_total_row = df1[df1["Key Demographic aspects"] == "Total population"]

# Melt from wide → long; years become rows
df_total_tidy = df_total_row.melt(
    id_vars=["Key Demographic aspects", "Unit"],
    var_name="Year",
    value_name="Total_Count"
)

# Keep only the two columns we need downstream
df_total_tidy = df_total_tidy[["Year", "Total_Count"]]
df_total_tidy["Year"] = df_total_tidy["Year"].astype(int)

print("── df_total_tidy ──")
print(df_total_tidy.to_string(index=False))


# =============================================================
# 3. CLEAN df2 → age-group percentages per sex per year
# =============================================================
# The raw sheet has a two-row header:
#   Row 0 (after header=1 read): year numbers (2015 … 2023), every 3rd column
#   Row 1 (actual data row 0):   sub-labels "Male", "Female", "Total"
#
# Strategy: rename ALL columns explicitly, then drop the sub-label row.

years = range(2015, 2024)

new_cols = ["Age"]
for y in years:
    new_cols += [f"Male_{y}", f"Female_{y}", f"Total_{y}"]  # 9 × 3 = 27 cols + Age = 28

df2_raw.columns = new_cols          # overwrite the messy auto-generated names
df2 = df2_raw.iloc[1:].copy()       # drop row 0 (the "Male / Female / Total" sub-header)

# Keep only the meaningful age-band rows; discard ratio/footnote rows
keep_ages = ["0 - 14", "15 - 59", "60 +", "Total"]
df2["Age"] = df2["Age"].astype(str).str.strip()
df_age = df2[df2["Age"].isin(keep_ages)].reset_index(drop=True)

print("\n── df_age (wide, cleaned) ──")
print(df_age.to_string(index=False))


# =============================================================
# 4. MELT df_age → tidy long form
# =============================================================
df_age_long = df_age.melt(
    id_vars=["Age"],
    var_name="Sex_Year",        # e.g. "Male_2015"
    value_name="Percentage"
)

# Split "Male_2015" into two columns → Sex="Male", Year=2015
df_age_long[["Sex", "Year"]] = (
    df_age_long["Sex_Year"].str.rsplit("_", n=1, expand=True)
)
df_age_long["Year"] = df_age_long["Year"].astype(int)
df_age_long["Percentage"] = pd.to_numeric(df_age_long["Percentage"], errors="coerce")
df_age_long = df_age_long.drop(columns=["Sex_Year"]).reset_index(drop=True)

print("\n── df_age_long (first 12 rows) ──")
print(df_age_long.head(12).to_string(index=False))


# =============================================================
# 5. MERGE both DataFrames on Year
# =============================================================
df_final = df_age_long.merge(df_total_tidy, on="Year", how="left")

# Bonus column: back-calculate absolute counts from % × total
df_final["Abs_Count"] = (
    df_final["Percentage"] / 100 * df_final["Total_Count"]
).round(0).astype("Int64")   # Int64 supports NaN natively

# Tidy column order and sort
df_final = (
    df_final[["Year", "Age", "Sex", "Percentage", "Total_Count", "Abs_Count"]]
    .sort_values(["Year", "Age", "Sex"])
    .reset_index(drop=True)
)

print("\n── df_final (ready for visualisation) ──")
print(df_final.to_string(index=False))


# =============================================================
# 6. QUICK SANITY CHECK
# =============================================================
# For Sex=="Total", the three age groups should sum to ~100 %
check = (
    df_final[df_final["Sex"] == "Total"]
    .groupby("Year")["Percentage"]
    .sum()
    .round(1)
)
print("\n── Column sum per year (Sex='Total', should be 100) ──")
print(check)


# =============================================================
# 7. QUICK STARTER PLOT  (example – uncomment to run)
# =============================================================
# Filter to totals only, exclude the grand-total "Total" age row
# plot_df = df_final[
#     (df_final["Sex"] == "Total") & (df_final["Age"] != "Total")
# ]
#
# fig, ax = plt.subplots(figsize=(10, 5))
# for age, grp in plot_df.groupby("Age"):
#     ax.plot(grp["Year"], grp["Percentage"], marker="o", label=age)
#
# ax.set_title("Aruba: Population share by age group (2015–2023)")
# ax.set_ylabel("% of total population")
# ax.set_xlabel("Year")
# ax.legend(title="Age group")
# ax.grid(True, linestyle="--", alpha=0.5)
# plt.tight_layout()
# plt.show()
