setwd("~/Google Drive/NAZCA/NAZCA Developers/We Are Still In 2020")

if (!require('pacman')) {
  install.packages('pacman')
}

library(pacman)
p_load(dplyr,rvest,magrittr,googlesheets,janitor, ggplot2, wesanderson)

url <- "http://wearestillin.com/signatories"
nodes <- url %>%
  read_html %>%
  html_nodes(".signatory") %>%
  html_text()

# Seems like we need to hardcode the categories and sources
# Remove duplicates first
signatories <- nodes[!duplicated(nodes)]
# Clean data
# Write function for easier replicability
split_actors <- function(start, end, sour, sig){
  # Function that takes in characters for start, end, and name that 
  # consists of the starting actors and ending actors for each split,
  # the name to assign to, and the vector to split from
  # Use in conjunction with mapply for iterability
  if (!require(Hmisc)){
    install.packages("Hmisc")
  }
  return(data.frame(name = sig[grep(start, sig):grep(end, sig)], 
                    source = Hmisc::capitalize(sour), country = "United States of America",
                    stringsAsFactors = FALSE))
}
signatories <- gsub("[\n]", "", signatories)
signatories <- trimws(signatories)
start.actors <- c("Andy Cook", "1000watt", "Acton, MA", "Alameda County, CA",
                  "AAM's Environment and Climate Network", "Presbyterian Church \\(USA\\)", 
                  "Academy of Integrative Health and Medicine", "Adelphi University",
                  "Action Together New Jersey", "^California$", "Blue Lake Rancheria")
end.actors <- c("VIXEVERSA INC", "Innovative Power Systems, Inc.", "Yonkers, NY",
                "Yolo County", "World Museum", 
                "Young Evangelicals for Climate Action", "Virginia Mason Memorial Hospital",
                "Worcester State University", "Zevin Asset Management", "^Washington$",
                "Suquamish Tribe")
assigned.names <- c("artists", "business", "cities", "counties", "cultural", "faith",
                    "health", "highered", "investor", "state", "tribe")
# Future scrapes can just change the different vectors and don't have to hard code so much
# Of course assuming that the layout stays the same... 

actors <- mapply(split_actors, start.actors, end.actors, assigned.names, MoreArgs = list(signatories),
                 SIMPLIFY = FALSE)
actors <- do.call(rbind, actors)
row.names(actors) <- NULL
actors$source <- gsub("Highered", "Higher Ed", actors$source)
actors$entity_type <- ifelse(actors$source == "Cities", "City",
                             ifelse(actors$source == "State" | actors$source == "Counties",
                                    "Region", ifelse(actors$source == "Business" | actors$source == "Investor",
                                                     "Company", "CSO")))

write.csv(actors, "stillin_2020scrape.csv", row.names = FALSE, fileEncoding = "utf-8")

# Some Data checks 
## Some data checks 
actors <- read.csv("../../../../output/actors/We Are Still In/stillin_2020scrape.csv",
                   encoding = "UTF-8", stringsAsFactors = F)
head(actors)
tail(actors)
# Seems like some actors missing 
url <- "http://wearestillin.com/signatories"
nodes <- url %>%
  read_html %>%
  html_nodes(".signatory") %>%
  html_text()

signatories <- nodes[!duplicated(nodes)]
signatories <- gsub("[\n]", "", signatories)
signatories <- trimws(signatories)
setdiff(signatories, actors$name)

# 
# #### Outdated ------------------------------------------------------
# # Define the URL
# url <- 'http://wearestillin.com/'
# # create an x
# nodes <- url %>% 
#   read_html %>%
#   html_nodes("div.gutter-top-2") %>%
#   "["(1:4)
# 
# t.1 <- nodes[1] %>% html_nodes(css = "li") %>% html_text() %>%
#   data.frame() %>% mutate(source.et="Cities and Regions")
# colnames(t.1) <- c("name","source")
# t.1 <- t.1  %>% mutate(entity_type=if_else("county" %in% name,"Region","City" ),
#                        country="United States of America",
#                        person=unlist(lapply(strsplit(as.character(t.1$name), "[,]"), `[[`, 1)) )
# 
# t.2 <- nodes[2] %>% html_nodes(css = "li") %>% html_text() %>%
#   data.frame() %>% mutate(source.et="States")
# colnames(t.2) <- c("name","source")
# t.2 <- t.2  %>% mutate(entity_type="Region" ,
#                        country="United States of America",
#                        person=NA)
# 
# t.3 <- nodes[3] %>% html_nodes(css = "li") %>% html_text() %>%
#   data.frame() %>% mutate(source.et="Higher education" )
# colnames(t.3) <- c("name","source")
# t.3 <- t.3  %>% mutate(entity_type="CSO",
#                        country="United States of America",
#                        person=NA)
# 
# t.4 <- nodes[4] %>% html_nodes(css = "li") %>% html_text() %>%
#   data.frame() %>% mutate(source.et="Businesses and Investors")
# colnames(t.4) <- c("name","source")
# t.4 <- t.4  %>% mutate(entity_type="Company",
#                        country="United States of America",
#                        person=NA)
# 
# stillin <- rbind(t.1, t.2, t.3, t.4)
# 
# # out of date
# link <- gs_url("https://docs.google.com/spreadsheets/d/1591k9_NLuxA3SUM7Ks3Dh5pQ1wETmbkkHMrbF1P12bI/pub?output=csv")
# states <- gs_read(link, range = "A1:G1220")
# 
# dat <- stillin %>% right_join(states, by = c('name', 'entity_type', 'country', 'person'))
# ####
# 
# write.csv(stillin, "stillin_merge.csv", row.names=F)                  
# 

