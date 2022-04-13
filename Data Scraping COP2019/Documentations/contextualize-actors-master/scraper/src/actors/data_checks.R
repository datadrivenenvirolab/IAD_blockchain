# Zhi Yi Yeo
# Yale-NUS/Data-Driven Lab
# March 2019

# Data Checks for Scrapers

library(dplyr)

#### EU Covenant ####
# Read in both new and old data
eu_newpath <- "../../../output/actors/EU Covenant/03.26.19"
new_ap <- read.csv(paste0(eu_newpath, "action_plan.csv"), encoding = "UTF-8",
                   stringsAsFactors = FALSE)
new_base <- read.csv(paste0(eu_newpath, "baseline.csv"), encoding = "UTF-8",
                     stringsAsFactors = FALSE)
new_ka <- read.csv(paste0(eu_newpath, "key_actions.csv"), encoding = "UTF-8",
                   stringsAsFactors = FALSE)
new_ov <- read.csv(paste0(eu_newpath, "overview.csv"), encoding = "UTF-8",
                   stringsAsFactors = FALSE)
eu_oldpath <- "../../../../../../Google Drive/NAZCA Developers/EU Covenant of Mayors Feb 2018/"
old_ap <- read.csv(paste0(eu_oldpath, "action_plan.csv"), encoding = "UTF-8",
                   stringsAsFactors = FALSE)
old_base <- read.csv(paste0(eu_oldpath, "baseline.csv"), encoding = "UTF-8",
                     stringsAsFactors = FALSE)
old_ka <- read.csv(paste0(eu_oldpath, "key_actions.csv"), encoding = "UTF-8",
                   stringsAsFactors = FALSE)
old_ov <- read.csv(paste0(eu_oldpath, "overview.csv"), encoding = "UTF-8",
                   stringsAsFactors = FALSE)

# First start with overview and check for differences in actors
which(paste0(new_ov$name, new_ov$country) %in% paste0(old_ov$name, old_ov$country) == F)
# All the newly scraped data was also in the old database
# Check for differences in baseline info
names(new_base) == names(old_base)
all_equal(old_base[,-1], new_base[,-1])
ind <- -which(paste0(old_base$name, old_base$country) %in% 
                paste0(new_base$name, new_base$country) == FALSE)
all_equal(old_base[ind, -1],
          new_base[,-1])
# Other than the missing observation in the new database, everything else is the same
all_equal(new_ka[,-1], old_ka[,-1])
# Key action all the same
all_equal(new_ap[, -1], old_ap[ind, -1])
# Action plans also same except for the missing row 
# Random spotchecks to make sure everything is ok
s <- sample(nrow(new_ov), 1)
new_ov[s, ]
new_ap[s, ]
new_base[s, ]
# Nope, things are not in the correct order. Probably due to multi-threading. Order the data
# based on name and country
new_ov <- new_ov[order(paste0(new_ov$name, new_ov$country)), ]
new_base <- new_base[order(paste0(new_base$name, new_base$country)), ]
new_ka <- new_ka[order(paste0(new_ka$name, new_ka$country)), ]
new_ap <- new_ap[order(paste0(new_ap$name, new_ap$country)), ]
# Try doing random spotchecks again
s <- sample(nrow(new_ov), 1)
new_ov[s, ]
new_ap[s, ]
new_base[s, ]
new_ka[new_ka$name == new_ov[s, "name"], ]
# Checked a few different actors, data seems to be in order 
# Remove redundant rows
new_ov <- select(new_ov, -(ACTION:MONITOR))
if (any(grepl("X", names(new_ov)))) {
  new_ov <- select(new_ov, -X)
  new_ap <- select(new_ap, -X)
  new_base <- select(new_base, -X)
  new_ka <- select(new_ka, -X)
}
# Rewrite out the data
# write.csv(new_ap, paste0(eu_newpath, "action_plan.csv"), fileEncoding = "UTF-8",
#           row.names = FALSE)
# write.csv(new_base, paste0(eu_newpath, "baseline.csv"), fileEncoding = "UTF-8",
#           row.names = FALSE)
# write.csv(new_ov, paste0(eu_newpath, "overview.csv"), fileEncoding = "UTF-8",
#           row.names = FALSE)
# write.csv(new_ka, paste0(eu_newpath, "key_actions.csv"), fileEncoding = "UTF-8",
#           row.names = FALSE)

#### Global Covenant ####
gcom_new <- read.csv("../../../output/actors/Global Covenant/04.01.19global_covenant_cities.csv",
                     stringsAsFactors = FALSE, encoding = "UTF-8")
gcom_oldpath <- "../../../../../../Google Drive/NAZCA Developers/Global Covenant of Mayors/"
gcom_old <- read.csv(paste0(gcom_oldpath, "global_covenant_cities.csv"), 
                     stringsAsFactors = FALSE, encoding = "UTF-8")
head(gcom_old)
head(gcom_new)
nrow(gcom_new)
length(unique(gcom_new$name))
# A few duplicate in names?
nrow(gcom_old)
setdiff(gcom_old$name, gcom_new$name)
setdiff(gcom_new$name, gcom_old$name)
all_equal(gcom_new, gcom_old)
# Risk columns not in the new dataset
# check for duplicated entries
gcom_new[duplicated(gcom_new$name), "name"]
dup_name <- gcom_new[duplicated(gcom_new$name), "name"]
gcom_new[gcom_new$name == dup_name[1], ] # same city name different country
gcom_new[gcom_new$name == dup_name[2], ] # Looks like some bug -> Fossa
gcom_new[gcom_new$name == dup_name[3], ] # Same thing, same name different country
gcom_new[gcom_new$name == dup_name[4], ] # Same thing, same name different country
# Spot check
s <- sample(nrow(gcom_new), 1)
gcom_new[s, ]
# Closer check on Antwerp
gcom_new[grep("Antwerp", gcom_new$name), ] # ok it's fine, just wasn't doing things correctly
# Closer check on Casalnuovo
gcom_new[grep("Casalnuovo", gcom_new$name), ]
# Spot check on those that actually have data
s <- sample(nrow(gcom_new[!is.na(gcom_new$total_ghg_emissions), ]), 1)
gcom_new[s, ]

#### Carbonn ####
car_newpath <- "../../../output/actors/carbonn/03.23.19"
car_oldpath <- "../../../../../../Google Drive/NAZCA Developers/Carbonn April 2018/04.27.18"
new_carap <- read.csv(paste0(car_newpath, "carbonn_action_plans.csv"),
                      stringsAsFactors = FALSE, encoding = "UTF-8")
new_caraa <- read.csv(paste0(car_newpath, "carbonn_adaptation_actions.csv"),
                      stringsAsFactors = FALSE, encoding = "UTF-8")
new_carcom <- read.csv(paste0(car_newpath, "carbonn_commitments.csv"),
                       stringsAsFactors = FALSE, encoding = "UTF-8")
new_carinv <- read.csv(paste0(car_newpath, "carbonn_inventories.csv"),
                       stringsAsFactors = FALSE, encoding = "UTF-8")
new_carmit <- read.csv(paste0(car_newpath, "carbonn_mitigation_actions.csv"),
                       stringsAsFactors = FALSE, encoding = "UTF-8")
new_carsum <- read.csv(paste0(car_newpath, "carbonn_summary_stats.csv"),
                       stringsAsFactors = FALSE, encoding = "UTF-8")
old_carap <- read.csv(paste0(car_oldpath, "carbonn_action_plans.csv"),
                      stringsAsFactors = FALSE, encoding = "UTF-8")
old_caraa <- read.csv(paste0(car_oldpath, "carbonn_adaptation_actions.csv"),
                      stringsAsFactors = FALSE, encoding = "UTF-8")
old_carcom <- read.csv(paste0(car_oldpath, "carbonn_commitments.csv"),
                       stringsAsFactors = FALSE, encoding = "UTF-8")
old_carinv <- read.csv(paste0(car_oldpath, "carbonn_inventories.csv"),
                       stringsAsFactors = FALSE, encoding = "UTF-8")
old_carmit <- read.csv(paste0(car_oldpath, "carbonn_mitigation_actions.csv"),
                       stringsAsFactors = FALSE, encoding = "UTF-8")
old_carsum <- read.csv(paste0(car_oldpath, "carbonn_summary_stats.csv"),
                       stringsAsFactors = FALSE, encoding = "UTF-8")
# Check summary stats first
all_equal(old_carsum, new_carsum)
new_carsum <- select(new_carsum, -"Unnamed..0")
nrow(old_carsum)
nrow(new_carsum)
setdiff(old_carsum$city, new_carsum$city)
setdiff(new_carsum$city, old_carsum$city)
old_carsum$area..km2. <- as.numeric(old_carsum$area..km2.)
new_carsum$target[which(new_carsum$target == "" | new_carsum$target == " ")] <- "N/A" 
nrow(intersect(old_carsum[,-1], new_carsum[,-1])) # 253 cities' summary stats did not change

# Check commitments
new_carcom <- select(new_carcom, -"Unnamed..0")
all_equal(new_carcom, old_carcom, convert = TRUE)
nrow(new_carcom) # Much less commitments in the new data
nrow(old_carcom)
# Do random spotchecks for the commitments
s <- sample(nrow(new_carcom), 1)
new_carcom[new_carcom$city == new_carcom$city[s], ]
old_carcom[old_carcom$city == new_carcom$city[s], ]

# Check inventories
new_carinv <- select(new_carinv, -"Unnamed..0")
all_equal(new_carinv, old_carinv, convert = TRUE)
nrow(new_carinv)
nrow(old_carinv)
# Random spotchecks
s <- sample(nrow(new_carinv), 1)
new_carinv[new_carinv$city == new_carinv$city[s], ]
old_carinv[old_carinv$city == new_carinv$city[s], ]
# Just do a check for those in the new dataset but not in the old
s <- sample(which(!(new_carinv$city %in% old_carinv$city)), 1)
new_carinv[new_carinv$city == new_carinv$city[s], ]
old_carinv[old_carinv$city == new_carinv$city[s], ]

# Check Actions
# Adaptations
new_caraa <- select(new_caraa, -"Unnamed..0")
all_equal(new_caraa, old_caraa, convert = TRUE)
nrow(new_caraa)
nrow(old_caraa)
length(unique(new_caraa$city))
length(unique(old_caraa$city))
# Random spotchecks (adaptation actions)
s <- sample(nrow(new_caraa), 1)
new_caraa[new_caraa$city == new_caraa$city[s], ]
nrow(new_caraa[new_caraa$city == new_caraa$city[s], ])
old_caraa[old_caraa$city == new_caraa$city[s], ]
nrow(old_caraa[old_caraa$city == new_caraa$city[s], ])
# Mitigation actions
new_carmit <- select(new_carmit, -"Unnamed..0")
all_equal(new_carmit, old_carmit, convert = TRUE)
nrow(new_carmit)
nrow(old_carmit)
length(unique(new_carmit$city))
length(unique(old_carmit$city))
# Random Spotcheck
s <- sample(nrow(new_carmit), 1)
new_carmit[new_carmit$city == new_carmit$city[s], ]
nrow(new_carmit[new_carmit$city == new_carmit$city[s], ])
old_carmit[old_carmit$city == new_carmit$city[s], ]
nrow(old_carmit[old_carmit$city == new_carmit$city[s], ])

# Action Plans
new_carap <- select(new_carap, -"Unnamed..0")
all_equal(new_carap, old_carap, convert = TRUE)
nrow(new_carap)
nrow(old_carap)
length(unique(new_carap$city))
length(unique(old_carap$city))
# Random Spotcheck
s <- sample(nrow(new_carap), 1)
new_carap[new_carap$city == new_carap$city[s], ]
nrow(new_carap[new_carap$city == new_carap$city[s], ])
old_carap[old_carap$city == new_carap$city[s], ]
nrow(old_carap[old_carap$city == new_carap$city[s], ])
