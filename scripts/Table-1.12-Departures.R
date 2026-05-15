# Import necessary libraries

library(readxl)

# Provide the full path or relative path from your working directory
raw_df <- read_excel("/home/ggirelli/Documents/DataAnalysis/projects/cbs_aruba/data/raw/Table-1.12-Departures-by-country-of-birth-and-sex.xlsx",
                     skip = 1,
                     col_names = FALSE)
View(raw_df)
