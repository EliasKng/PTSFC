# This script checks if the automatic download of financial data matches the manually downloaded data.
# GDAXI.csv was downloaded automatically using tidyquant and ^GDAXI.csv manually from yahoo finance
# It can be seen, that the data matches.

# Here the most recent Data was downloaded:

# library(tidyquant)
# setwd("/Users/elias/Desktop/PTSFC/DAX/Check Automatic Download Validity")
# options("getSymbols.warning4.0"=FALSE)
# options("getSymbols.yahoo.warning"=FALSE)
# # Downloading Apple price using quantmod
# 
# getSymbols("^GDAXI", from = '1987-12-30',warnings = FALSE,
#            auto.assign = TRUE)
# 
# write.csv(GDAXI, "GDAXI.csv")
# 

setwd("/Users/elias/Desktop/PTSFC/DAX/Check Automatic Download Validity")
GDAXI <- read.csv("GDAXI.csv")
gGDAXI <- read.csv("^GDAXI.csv", header = TRUE)



# Here, the comparison takes place

gGDAXI$'Adj.Close' = as.numeric(gGDAXI$'Adj.Close')

# Calculate the absolute percentage difference
percent_difference <- abs(GDAXI$'GDAXI.Adjusted' - gGDAXI$'Adj.Close') / ((GDAXI$'GDAXI.Adjusted' + gGDAXI$'Adj.Close')/2) * 100
percent_difference_no_na <- na.omit(percent_difference)

# Print maximum percentage difference
print("Maximum percentage difference: ")
print(max(percent_difference_no_na))



# Create an index for rows where both are NA or both are not NA
valid_index <- (is.na(GDAXI$`GDAXI.Adjusted`) & is.na(gGDAXI$`Adj.Close`)) | 
  (!is.na(GDAXI$`GDAXI.Adjusted`) & !is.na(gGDAXI$`Adj.Close`))

# Check if all NA's match
print("Are all NAs identical: ")
print(all(valid_index))
