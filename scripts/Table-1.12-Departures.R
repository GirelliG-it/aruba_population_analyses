# Import necessary libraries

library(readxl)
library(tidyr)
library(dplyr)
library(janitor)

# Provide the full path or relative path from your working directory
raw_df <- read_excel("/home/ggirelli/Documents/DataAnalysis/projects/cbs_aruba/data/raw/Table-1.12-Departures-by-country-of-birth-and-sex.xlsx",
                     skip = 1,
                     col_names = FALSE)
View(raw_df)

# Remove empty row
df <- remove_empty(raw_df, which="rows")

# Extract the first two rows as a separate header data frame
headers <- df[1:2,]

# Rotate, fill missing years down, and combine 'year' + 'gender'
headers_clean <- headers |> 
  t() |> 
  as.data.frame() |> 
  fill(V1, .direction = "down") |> 
  mutate(clean_name = ifelse(is.na(V1), V2, paste(V1, V2, sep = "_")))

headers_clean                             
