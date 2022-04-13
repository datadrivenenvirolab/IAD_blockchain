setwd("~/Google Drive/NAZCA/NAZCA Developers/Climate Mayors 2020")

if (!require('pacman')) {
  install.packages('pacman')
}

p_load(dplyr, climactor, pdftools)

text <- pdf_text("Cities_Climate_Action_Compendium_180105.pdf") %>% readr::read_lines()
text2 <- gsub("^\\s+\\d{,2}$", "pg no", text) #ignoring the page numbers
text3 <- gsub("^Significa(.*)?|^Climate(.*)?", "0stop0", text2) #adding the stop points for targets
nodes <- gsub("^Targets(:)?", "0start0", text3) #adding the start points for targets


# Consolidating the City names
actors <- c()
for (i in 1:length(nodes)){
  if (nodes[i] == "0start0"){
    actors <- c(actors, trimws(nodes[i-1]))
  }
}

actors <- c(actors, "Cooperstown, NY") #Data for Cooperstown does not start with "Targets"
View(actors)
#Check for actors that are not already in the collated list
x <- read.csv("Climate Mayors Additions May 2019 (Final) - Climate Mayors.csv", stringsAsFactors = F)
actors[!actors %in% x$name]
# "Ashville, NC" -- "Durham and Durham County, NC2" -- "Washington, DC"

# ------------------------------------------------------------------
actors<- as.data.frame(actors) #converting to a dataframe
names(actors) <- "name"

#adding info from climactor package
actors <- add_country(actors)
actors$country <- "United States of America"
actors <- add_entity_type(actors, "City")

origcountry <- actors$Country
actors <- clean_country_iso(actors, country_dict, iso = 3, clean_enc = F)

actors$Country[country_ind] # empty
sum(actors$country %in% country_dict$right) #all

# Check ISO first 
any(is.na(actors$iso)) # none

#adding additional columns
actors$region <- "North America"
actors$state <- gsub(".*,","", actors$name)
actors$raw_commitment <- ''
actors$ghg_reduction_target_type <- ''


#iterating through to add raw commitments and target type
r <- 0
start <- F
indicators <- c()
ghg <- ''

for(i in 1:length(nodes)){
  if (nodes[i] == '0start0'){
    start <- T
    r <- r + 1
  } else if (nodes[i] == "0stop0"){
    start <- F
    ghg <- ''
  }
  if (nodes[i] != '0start0' & nodes[i] != 'pg no' & nodes[i] != '' & start){
    if (actors$raw_commitment[r] == ''){
      nodes[i] <- gsub('^o |•|○', '', trimws(nodes[i]))
      nodes[i] <- gsub('—', '-', nodes[i])
      actors$raw_commitment[r] <- trimws(nodes[i])
      if (grepl('Municipal([[:punct:]]*)?$|Municipal GHG Reduction Targets:', actors$raw_commitment[r])){
        ghg <- 'GHG emission reduction target:Local Government'
        indicators <- c(indicators, r)
      } else if (grepl('Community(.{,5})?$|Community GHG Reduction Targets:', actors$raw_commitment[r])){
        ghg <- 'GHG emission reduction target:Community'
        indicators <- c(indicators, r)
      } 
      actors$ghg_reduction_target_type[r] <- ghg
      if (grepl('municipal', actors$raw_commitment[r]) & actors$ghg_reduction_target_type[r] == ''){
        actors$ghg_reduction_target_type[r] <- 'GHG emission reduction target:Local Government'
      } else if (grepl('community', actors$raw_commitment[r]) & actors$ghg_reduction_target_type[r] == ''){
        actors$ghg_reduction_target_type[r] <- 'GHG emission reduction target:Community'
      }
    }
    else if (!startsWith(trimws(nodes[i]), "o ") & !startsWith(trimws(nodes[i]), "•") & !startsWith(trimws(nodes[i]), "○")){
      nodes[i] <- gsub('^o |•|○', '', trimws(nodes[i]))
      nodes[i] <- gsub('—', '-', nodes[i])
      actors$raw_commitment[r] <- paste(actors$raw_commitment[r], trimws(nodes[i]), "")
    }
    else {
      actors[r:nrow(actors) + 1,] <- actors[r:nrow(actors), ]
      r <- r + 1
      nodes[i] <- gsub('^o |•|○', '', trimws(nodes[i]))
      nodes[i] <- gsub('—', '-', nodes[i])
      actors$raw_commitment[r] <- trimws(nodes[i])
      if (grepl('Municipal([[:punct:]]*)?$|Municipal GHG Reduction Targets:', actors$raw_commitment[r])){
        ghg <- 'GHG emission reduction target:Local Government'
        indicators <- c(indicators, r)
      } else if (grepl('Community(.{,5})?$|Community GHG Reduction Targets:', actors$raw_commitment[r])){
        ghg <- 'GHG emission reduction target:Community'
        indicators <- c(indicators, r)
      } 
      actors$ghg_reduction_target_type[r] <- ghg
      if (grepl('municipal', actors$raw_commitment[r]) & actors$ghg_reduction_target_type[r] == ''){
        actors$ghg_reduction_target_type[r] <- 'GHG emission reduction target:Local Government'
      } else if (grepl('community', actors$raw_commitment[r]) & actors$ghg_reduction_target_type[r] == ''){
        actors$ghg_reduction_target_type[r] <- 'GHG emission reduction target:Community'
      }
    }
  }
}

#removing rows with target markers
actors <- actors[-indicators, ]


#adding additional columns
actors$percent_reduction <- ''
actors$target_year <- ''
actors$baseline_year <- ''
actors$data_source <- 'ClimateMayors'

write.csv(actors, "ClimateMayors2020.csv", row.names = FALSE, fileEncoding = "utf-8")

# Some quick data checks 
actors <- read.csv("../../../../output/actors/Climate Mayors/ClimateMayors2020_clean.csv",
                   encoding = "UTF-8", stringsAsFactors = F)
head(actors)
tail(actors)
unique(actors$ghg_reduction_target_type)
head(actors$raw_commitment)
tail(actors$raw_commitment)
unique(actors$name)
actors$baseline_year
actors$target_year
