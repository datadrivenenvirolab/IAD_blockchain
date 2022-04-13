# Zhi Yi Yeo
# Aug 2020
# Data-Driven Lab
# Hoovers cleaning script 
library(ClimActor)

# Read in data 
hoovers <- read.csv("Contextuals/hoovers_revenue_full_28Aug.csv",
                    stringsAsFactors = F, encoding = "UTF-8")

head(hoovers)
hoovers$country <- trimws(gsub("([[:upper:]])", " \\1", 
                               gsub(".*,(.*)", "\\1", hoovers$location)))
hoovers <- hoovers[, -grep("^X", names(hoovers))]
names(hoovers)

hoovers <- add_entity_type(hoovers, "Company")

hoovers <- fill_type(hoovers)
table(hoovers$entity_type)
# Filled some of them as cities and regions - change them all back to companies 
hoovers$entity_type <- "Company"

# Clean country and iso 
# Manual fix for Korea first 
hoovers$country[grep("Republicof", hoovers$location)] <- "South Korea"
hoovers <- clean_country_iso(hoovers, country_dict)
hoovers$country[country_ind]
hoovers <- fuzzify_country(hoovers, country_dict)

hoovers <- resolve_entity_types(hoovers, key_dict)
hoovers_resolved <- resolve_entity_types(hoovers, key_dict)

orignames <- hoovers_resolved$name
hoovers_resolved <- remove_extra(hoovers_resolved)
setdiff(orignames, hoovers_resolved$name)
precleaned_names <- hoovers_resolved$name

# Clean names 
hoovers_resolved <- clean_name(hoovers_resolved, key_dict)
hoovers_resolved <- phonetify_names(hoovers_resolved, key_dict)

# Resume cleaning 
hoovers_resolved <- read.csv("Contextuals/hoovers_cleaning_intermediate.csv",
                             stringsAsFactors = F, fileEncoding = "UTF-8")
unmatched_indices <- readRDS("Contextuals/hoovers_unmatched_indices.rds")
custom_indices <- readRDS("Contextuals/hoovers_custom_indices.rds")

# Export interim cleaning 
write.csv(hoovers_resolved, "Contextuals/hoovers_clean_names.csv",
          row.names = F, fileEncoding = "UTF-8")
saveRDS(unmatched_indices, "Contextuals/hoovers_unmatched_indices.rds")
saveRDS(custom_indices, "Contextuals/hoovers_custom_indices.rds")

hoovers_resolved <- read.csv("Contextuals/hoovers_clean_names.csv", stringsAsFactors = F,
                             encoding = "UTF-8")
# Read in data to be merged 
cdp_rev <- read.csv("CDP_companies_nz_revenue_to_scrape_27Aug.csv",
                   stringsAsFactors = F, encoding = "UTF-8")
sum(unique(paste(tolower(cdp_rev$name), cdp_rev$iso)) %in% paste(tolower(hoovers_resolved$name),
                                                         hoovers_resolved$iso))
length(unique(paste(cdp_rev$name, cdp_rev$iso)))
