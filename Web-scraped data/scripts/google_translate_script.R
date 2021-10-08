# Angel Hsu
# Data-Driven Lab
# October 2021
# Translation for IAD Analysis - Stefan

# Libraries
library(tidyverse)
library(googleLanguageR)
library(ClimActor)
library(readxl)

# google translate auth
gl_auth("~/Google Drive/NAZCA/NAZCA Developers/EU Covenant of Mayors Apr 2019/eu-covenant-project-9277c5244b54.json")

# setwd
setwd("~/Documents/GitHub/IAD_blockchain/Web-scraped data")

# read in data
x <- read.csv("FOREIGN_LANGUAGE_TEXTS.csv", stringsAsFactors = FALSE)
dict <- read_xlsx("../Dictionaries/language_codes_wiki.xlsx")

# add a column for the language
x <- x %>% mutate(original_language = str_replace(original_language, "ChineseT", "Chinese"), 
                  original_language = tolower(original_language), original_language = str_replace(original_language, "spanish", "spanish, castilian"),
                  original_language = str_replace(original_language, "catalan", "catalan, valencian"),
                  original_language = str_replace(original_language, "dutch", "dutch, flemish"),
                  original_language = str_replace(original_language, "pashto", "pashto, pushto")) %>%
     left_join(dict %>% mutate(`ISO language name` = tolower(`ISO language name`)) %>% rename("iso"=`ISO language name`) %>% dplyr::select(iso, `639-1`), 
               by = c("original_language"="iso"))

# dutch not matched
x <- x %>% mutate(`639-1` = case_when(is.na(`639-1`) ~ "nl", TRUE ~ as.character(`639-1`)))

# add new columns
x <- y <- x %>% add_column(Text_translated = "NA", organization_translated = "NA")

# translate text - detect language method (requires OAuth)
for(i in 1:nrow(x)){
  if(x$original_language[i] != "en"){
    x$Text_translated[i] <- gl_translate(x$Text[i], target="en")
    x$organization_translated[i] <- gl_translate(x$organization[i], target="en")
  }
}
