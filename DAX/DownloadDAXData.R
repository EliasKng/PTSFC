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
