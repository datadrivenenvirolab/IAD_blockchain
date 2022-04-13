# Zhi Yi Yeo
# Data-Driven Lab
# September 2019
# Scrape of EU Cov data

# Initialization
library(dplyr)
library(rvest)
# Attach URL
url <- "https://www.covenantofmayors.eu/plans-and-actions/action-plans.html?tmpl=response&filter-search=&filter_country=&filter_commits=&filter_region=&filter_targetyear=&filter_status=&filter_sdate=&filter_population=&filter_sector=&filter_emission=&filter_language=&filter_doctype=&limit=0&filter_order=a.signatory_name&filter_order_Dir=ASC"

# First read the html 
html <- url %>%
  read_html()


# Write a function that goes into each XML tree and grabs the info we want
parser <- function(xml_tree, nodeset){
  # Write a parser that takes an individual xml tree (with each tree belonging to an 
  # actor) and extract the information from that tree 
  nodes <- html_nodes(xml_tree, nodeset)
  return(html_text(nodes))
}
text <- lapply(html_nodes(xml_child(html, 1), "tr"), parser, "td")
text.df <- do.call(rbind, text)
text.df <- data.frame(text.df, stringsAsFactors = FALSE)
names(text.df) <- c("name", "population", "commitment", "date_signedup", "action_plan")
text.df$commitment <- gsub("\\W", "", text.df$commitment)
date <- Sys.Date()
data.table::fwrite(text.df, paste0("eucov_actionplan", date,".csv"))


# Scrape "Progress Page" 
progress_url <- "https://www.covenantofmayors.eu/plans-and-actions/progress.html?tmpl=response&filter-search=&filter_country=&filter_submittedby=&filter_commits=&filter_ftgyear=&filter_submission=&filter_region=&filter_status=&filter_actionplan=&filter_population=&filter_sector=&filter_emission=&limit=0&filter_order=a.signatory_name&filter_order_Dir=ASC"

progress_html <- progress_url %>%
  read_html()
# Write funtion that parses the progress page
progress_parser <- function(xml_tree, nodeset){
  nodes <- html_nodes(xml_tree, nodeset)
  # Check for icon bar
  if (length(html_nodes(nodes, ".icon-bar")) != 0){
    img.nodes <- html_nodes(html_nodes(xml_tree, ".icon-bar"), "img")
    sectors <- html_text(xml_find_all(img.nodes, "@title"))
    text <- html_text(nodes)
    text[8] <- paste0(sectors, collapse = "; ")
    return(text)
  } else {
    return(html_text(nodes))
  }
}

progress.text <-lapply(html_nodes(xml_child(progress_html, 1), "tr"), progress_parser, "td")
ptext.df <- do.call(rbind, progress.text)
ptext.df <- data.frame(ptext.df)
names(ptext.df) <- c("name", "country", "commitments", "submission", "year", "region",
                     "population", "sectors", "target")
ptext.df$commitments <- gsub("\\W+?(\\w*)\\W+", "\\1;", ptext.df$commitments)
ptext.df$commitments <- gsub("^;(.*?);$", "\\1",ptext.df$commitments)
data.table::fwrite(ptext.df, paste0("eucov_progress", date,".csv"))

# Read in data to merge 
eucov <- read.csv("~/Google Drive/NAZCA Developers/EU Covenant of Mayors Apr 2019/EUCovenantofMayors2019_clean.csv",
                  header = T, as.is = T, encoding = "UTF-8", stringsAsFactors = F)
action.plans <- read.csv("~/Google Drive/NAZCA Developers/EU Covenant of Mayors Apr 2019/action_plan_clean.csv", 
                         header=T, as.is=T, encoding="UTF-8", stringsAsFactors = FALSE)
progress <- read.csv("eucov_progress2019-09-25.csv", header = T, 
                     as.is = T, encoding = "UTF-8")

eucov$action_plan_submission_date <- NA
eucov$action_plan_approval_date <- NA
eucov$progress_report_submission_date <- NA

eucov$action_plan_approval_date <- action.plans$approval_date[match(paste0(eucov$name, 
                                                                           eucov$iso, eucov$entity_type), 
                                                                    paste0(action.plans$name, 
                                                                           action.plans$iso, action.plans$entity_type))]
eucov$action_plan_submission_date <- action.plans$submission_date[match(paste0(eucov$name, 
                                                                               eucov$iso, eucov$entity_type), 
                                                                        paste0(action.plans$name, 
                                                                               action.plans$iso, action.plans$entity_type))]

# Need to clean progress actors' names and iso first
dict <- read.csv("~/Google Drive/NAZCA Developers/Dictionaries/country_dict.csv", header = TRUE, as.is = TRUE, encoding="UTF8") 
key.dict <- read.csv("~/Google Drive/NAZCA Developers/Dictionaries/key_dict_new.csv", header=T, as.is=T, encoding="UTF8")

# Clean country names and include iso first
any(toupper(progress$country) %in% toupper(dict$wrong))
progress$country <- dict$right[match(toupper(progress$country), toupper(dict$wrong))]
# Quick check
all(toupper(progress$country) %in% toupper(dict$right))

progress$iso <- dict$iso[match(toupper(progress$country), toupper(dict$wrong))]

progress$name_cleaned <- key.dict$right[match(paste0(toupper(progress$name), progress$iso),
                                              paste0(toupper(key.dict$wrong), key.dict$iso))]

# Check for which data is not currently in the key dict
which(!(toupper(progress$name) %in% toupper(key.dict$wrong)))

eucov$progress_report_submission_date <- progress$submission[match(paste0(toupper(eucov$name), eucov$iso),
                                                                   paste0(toupper(progress$name), progress$iso))]
data.table::fwrite(eucov, "EUCov_data_with_dates_nihit.csv", )
