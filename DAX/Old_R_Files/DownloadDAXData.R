library(tidyquant)

setwd("/Users/elias/Desktop/PTSFC/DAX/")

get_dax_data <- function() {
  options("getSymbols.warning4.0"=FALSE)
  options("getSymbols.yahoo.warning"=FALSE)
  # Downloading Apple price using quantmod
  getSymbols("^GDAXI", from = '1987-12-30',warnings = FALSE,
              auto.assign = TRUE)
  
  # Rename "Adjusted" Column
  colnames(GDAXI)[colnames(GDAXI) == "GDAXI.Adjusted"] <- "Adj"
  
  return (GDAXI$Adj)
}

# This function will drop all NA-Values
get_log_returns <- function(GDAXI) {
  GDAXI <- na.omit(GDAXI)
  log_returns <- 100 * diff(log(GDAXI$Adj))
  GDAXI <- merge(GDAXI, log_returns)
  colnames(GDAXI)[colnames(GDAXI) == "Adj.1"] <- "log_returns"
  GDAXI <- na.omit(GDAXI)
  return (GDAXI)
}