# Zhi Yi Yeo
# Data-Driven Lab
# NAZCA scraper 

# This file contains a quick and dirty NAZCA scraper that scrapes half of the current 
# (March 2020) NAZCA database (entities 8000 to 17290). This is done in collaboration with 
# Mia who scraped the other half of the database. 
# Updated June 2020 - Change scraper to scrape all the data 

library(rjson)
library(xml2)
library(rvest)

# Functions to scrape and break-up into dataframe for exporting
# Write helper functions! 
# check_action <- function(json){
#   tmp <- do.call(paste0, list(lapply(json$CA, function(x) if (x$commitmentType == "Cooperative actions"){
#     x$cooperativeInitiativeName} else {x$climateActionContextualStatement}),
#     collapse = ";;"))
#   return(tmp)
# }
# Get data provider information 
get_dp <- function(dp){
  if (length(dp) != 0){
    dp_link <- paste(sapply(dp, function(x) x$DataProviderLink), 
                     collapse = ";;\n")
    dp_name <- paste(sapply(dp, function(x) x$DataProviderName),
                     collapse = ";; ")
  } else {
    dp_link <- NA
    dp_name <- NA
  }
  return(data.frame(dataprovider_link = dp_link,
                    dataprovider_name = dp_name, stringsAsFactors = F))
}
# Get commitments info 
get_commitment <- function(ca){
  # Some special checks first 
  if (length(ca$themes) != 0){
    themes <- paste(ca$themes, collapse = ";;")
  } else {
    themes <- NA
  }
  if (length(ca$crosscuttingThemes) != 0){
    cross_cutting_themes <- paste(ca$crosscuttingThemes, collapse = ";;")
  } else {
    cross_cutting_themes <- NA
  }
  if (ca$commitmentType == "Cooperative actions"){
    commit_text <- paste(ca$cooperativeInitiativeName, collapse = ";;")
  } else {
    commit_text <- ca$climateActionContextualStatement
  }
  commitment <- data.frame(climate_action_timeframe = ca$climateactiontimeframe,
                           themes = themes,
                           commitment_type = ca$commitmentType,
                           commit_text = commit_text,
                           cooperative_description = ca$cooperativeInitiativeDescription,
                           climate_action_type = ca$climateActionTypeDisplay,
                           cross_cutting_themes = cross_cutting_themes,
                           sdgs = paste(ca$sdgs, collapse = ";;"),
                           stringsAsFactors = F)
  commitment <- cbind(commitment, get_dp(ca$dps))
  return(commitment)
}


get_nazca <- function(entityid, html){
  # Save as little things as possible so we are lumping all the functions together
  # Use try catch to wrap around 
  json <- tryCatch({
    message(cat(paste("Scraping html for", entityid)))
    fromJSON(html_text(read_html(paste0(html, entityid),
                                 encoding = "UTF-8")))},
    error = function(cond){
      message(cat(paste("Scrape failed for", entityid)))
      return(entityid)
    })
  if (length(json) > 1 & !is.null(json$entityID)){
    df <- data.frame(entity_id = json$entityID,
                     name = json$entityName,
                     entity_type = json$entityTypeName,
                     country = json$country$countryName,
                     lat = json$entityGeoLatitude,
                     lng = json$entityGeoLongitude,
                     area = json$entityTerritorialAreaSize,
                     area_unit = json$entityTerritorialAreaSizeUnit,
                     area_year = json$entityTerritorialAreaSizeYear,
                     density = json$entityPopulationDensity,
                     density_unit = json$entityPopulationDensityUnit,
                     density_year = json$entityPopulationDensityYear,
                     gdp = json$entityGDPValue,
                     gdp_unit = json$entityGDPUnit,
                     gdp_year = json$entityGDPYear,
                     budget = json$entityOperationalBudget,
                     budget_year = json$entityOperationalBudgetYear,
                     budget_currency = json$entityOperationalBudgetCurrency,
                     population = json$entityNumberOfPopulation,
                     population_year = json$entityPopulationYear,
                     number_of_employees = json$entityNumberOfEmployees,
                     employee_range = json$entityNumberOfEmployeesRange,
                     employees_year = json$entityNumberOfEmployeesYear,
                     revenue = json$entityRevenueValue,
                     revenue_year = json$entityRevenueValueYear,
                     revenue_currency = json$entityRevenueValueCurrency,
                     business_activity = json$BusinessActivityNameGRI,
                     total_emissions = json$GHGEmissionsRange,
                     total_emissions_unit = json$GHGEmissionsUnit,
                     baseyear_emissions = json$GHGBaseYearEmission,
                     base_year = json$GHGBaseYear,
                     base_year_units = json$GHGBaseYearEmissionUnit,
                     stringsAsFactors = F)
    if (length(json$CA) != 0){
      commitments <- do.call(rbind,lapply(json$CA, get_commitment))
      df <- df[rep(1, nrow(commitments)), ]
      df <- cbind(df, commitments)
    } else {
      df <- cbind(df, data.frame(climate_action_timeframe = NA,
                                 themes = NA,
                                 commitment_type = NA,
                                 commit_text = NA,
                                 cooperative_description = NA,
                                 climate_action_type = NA,
                                 cross_cutting_themes = NA,
                                 sdgs = NA,
                                 dataprovider_link = NA,
                                 dataprovider_name = NA,
                                 stringsAsFactors = F))
    }
    
  } else {
    df <- data.frame(entity_id = entityid,
                     name = NA,
                     entity_type = NA,
                     country = NA,
                     lat = NA,
                     lng = NA,
                     area = NA,
                     area_unit = NA,
                     area_year = NA,
                     density = NA,
                     density_unit = NA,
                     density_year = NA,
                     gdp = NA,
                     gdp_unit = NA,
                     gdp_year = NA,
                     budget = NA,
                     budget_year = NA,
                     budget_currency = NA,
                     population = NA,
                     population_year = NA,
                     number_of_employees = NA,
                     employee_range = NA,
                     employees_year = NA,
                     revenue = NA,
                     revenue_year = NA,
                     revenue_currency = NA,
                     business_activity = NA,
                     total_emissions = NA,
                     total_emissions_unit = NA,
                     baseyear_emissions = NA,
                     base_year = NA,
                     base_year_units = NA,
                     climate_action_timeframe = NA,
                     themes = NA,
                     commitment_type = NA,
                     commit_text = NA,
                     cooperative_description = NA,
                     climate_action_type = NA,
                     cross_cutting_themes = NA,
                     sdgs = NA,
                     dataprovider_link = NA,
                     dataprovider_name = NA,
                     stringsAsFactors = F)
  }
  return(df)
}
# Main scraping loop 
# Initialize main html 
html <- "https://nazcaapiprod.howoco.com/handlers/stakeholder.ashx?entityid="


# Long loop - might want to break into chunks to run 
# Prevents any errors that might slip past the various error checks in the functions
# and prevents function from breaking after scraping a few thousand entries 
# (Speaking from painful experience)    
# Clocks in at about 3min per 100 actors 
naz1 <- lapply(1:3000, get_nazca, html)
naz1df <- do.call(rbind, naz1)
write.csv(naz1df, "nazca_scrape1.csv", fileEncoding = "UTF-8",
          row.names = F)
rm(naz1)
gc()
# Chunk 2 
naz2 <- lapply(3001:6000, get_nazca, html)
naz2df <- do.call(rbind, naz2)
write.csv(naz2df, "nazca_scrape2.csv", fileEncoding = "UTF-8",
          row.names = F)
rm(naz2)
gc()
# Chunk 3
naz3 <- lapply(6001:9000, get_nazca, html)
naz3df <- do.call(rbind, naz3)
write.csv(naz3df, "nazca_scrape3.csv", fileEncoding = "UTF-8",
          row.names = F)
rm(naz3)
gc()
# Chunk 4
naz4 <- lapply(9001:12000, get_nazca, html)
naz4df <- do.call(rbind, naz4)
write.csv(naz4df, "nazca_scrape4.csv", fileEncoding = "UTF-8",
          row.names = F)
rm(naz4)
gc()
# Chunk 5
naz5 <- lapply(12001:15000, get_nazca, html)
naz5df <- do.call(rbind, naz5)
write.csv(naz5df, "nazca_scrape5.csv", fileEncoding = "UTF-8",
          row.names = F)
rm(naz5)
gc()

naz6 <- lapply(15001:18500, get_nazca, html)
naz6df <- do.call(rbind, naz6)
write.csv(naz6df, "nazca_scrape6.csv", fileEncoding = "UTF-8",
          row.names = F)
rm(naz6)
gc()

# Combine all together 
nazcafull <- rbind(naz1df, naz2df, naz3df, naz4df, naz5df, naz6df)
head(nazcafull)
tail(nazcafull)
# Remove those that have no data 
which(is.na(nazcafull$name))
sum(is.na(nazcafull$name))
nazcafull <- nazcafull[!is.na(nazcafull$name), ]
# Write out NAZCA data
saveRDS(nazcafull, "nazcadatafull_raw_June20_rdata.rds")
write.csv(nazcafull, "nazcadatafull_raw_June20.csv",
          fileEncoding = "UTF-8", row.names = F)


nazcafull <- read.csv("../../../../../output/actors/NAZCA/nazcadatafull_raw_June20.csv",
                  stringsAsFactors = F, encoding = "UTF-8")
# some data checks
any(is.na(nazcafull$entity_id))
any(is.na(nazcafull$name))
any(is.na(nazcafull$country))
# Looks ok 
# Check for empty columns 
which(apply(nazcafull, 2, function(x) all(is.na(x) | x == "")))
# Remove columns that are just empty columns 
nazcafull <- nazcafull[, -which(apply(nazcafull, 2, function(x) all(is.na(x) | x == "")))]
# Re-export 
write.csv(nazcafull, "../../../../../output/actors/NAZCA/nazcadatafull_raw_June20.csv",
          fileEncoding = "UTF-8", row.names = F)

# Getting investors actors 
nazca <- read.csv("../../../../../output/actors/NAZCA/nazcadatafull_raw_June20.csv",
                  stringsAsFactors = F, encoding = "UTF-8")
table(nazca$entity_type)
nazca_investor <- nazca[nazca$entity_type == "Investor", ]
head(nazca_investor)
# Write out csv
write.csv(nazca_investor, "../../../../../output/actors/NAZCA/nazca_investorJune2020.csv", 
          row.names = F, fileEncoding = "UTF-8")

## Some exploration for the scraper to check through all the data and scrape all data 
# html <- "https://nazcaapiprod.howoco.com/handlers/stakeholder.ashx?entityid="
# ent_ind <- 10616
# 
# scrape <- fromJSON(html_text(read_html(paste0(html, ent_ind),
#                                        encoding = "UTF-8")))


# read in data from Mia and combine them into one 
# Much easier to fix the weird rows in excel itself... but for posterity's sake..
# Mia's data has missing gaps -> so I rescraped the database 
# library(readxl)
# library(dplyr)
# # city merged file downloaded from Mia's gdrive link: 
# # https://docs.google.com/spreadsheets/d/1kJq-3PM1zr7IZcTAQlaHlxJogVpLCEF-eeeR3OfY-XU/edit#gid=1750640681
# 
# mia_scrape <- read_xlsx("City_Merged.xlsx", sheet = "City_Merged.csv")
# # Fix weird lines and gaps 
# names(mia_scrape) <- mia_scrape[3, ]
# mia_scrape <- mia_scrape[-(1:3), ]
# head(mia_scrape)
# head(nazcafull)
# dim(nazcafull)
# dim(mia_scrape)
# # Remove empty rows from Mia's data set
# # Mia's scrape seems to be missing some entities..... 
# which(is.na(mia_scrape$Name))
# mia_scrape <- mia_scrape[!is.na(mia_scrape$Name), ]
# head(mia_scrape)
# tail(mia_scrape)
# # Standardize the different columns between the 2 datasets 
# names(nazcafull)
# mia_scrape$entity_id <- NA
# mia_scrape <- mia_scrape %>%
#   select(entity_id, Name:Y)
# nazcafull$employees <- NA
# names(mia_scrape) <- names(nazcafull)
# tmp <- mia_scrape$population
# mia_scrape$population <- mia_scrape$employees
# mia_scrape$employees <- tmp
# 
# fulldf <- rbind(mia_scrape, nazcafull)
