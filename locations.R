# locations.R
# M. Silk

# Read in a copy of the Airtable export,
# collect locations, append to locations
# lookup table, try automatically querying
# locations


library(data.table)
library(magrittr)
library(tidygeocoder)


# Read in Airtable exported data
new = fread("Harmony Day - Interactive Map-MASTER LIST.csv", header = TRUE)


# Gather all location strings (any with Location
# in colname)
new_location_cols <- grep("Location", names(new))
new_location_strings <- new[, ..new_location_cols] %>%
  unlist %>%
  as.character %>%
  .[. != ""] %>%
  .[!is.na(.)] %>%
  unique


# Convert to data table and key
new_locations <- data.table(loc_string = new_location_strings)
setkey(new_locations, loc_string)

# Read in full edited locations list
if (file.exists("locations.tsv")) {
  curr_locations <- fread("locations.tsv")
} else {
  curr_locations <- data.table(loc_string = character(),
                              lat_query = numeric(),
                              lon_query = numeric(),
                              lat_final = numeric(),
                              lon_final = numeric()
                              )
}
setkey(curr_locations, loc_string)

# Merge
merged_locations <- curr_locations[new_locations]

# Query missing locations
merged_locations[is.na(lat_query), c("lat_query", "lon_query") := geo(address = loc_string,
                                                                      method = "osm")[, 2:3]]

# Remove duplicate rows (shouldn't be any)
merged_locations <- unique(merged_locations, by = "loc_string")

# Write to file
fwrite(merged_locations, "locations.tsv", sep = "\t")
