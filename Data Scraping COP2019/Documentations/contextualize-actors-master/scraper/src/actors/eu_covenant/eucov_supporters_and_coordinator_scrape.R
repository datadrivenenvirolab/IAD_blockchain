# Zhi Yi Yeo
# Data-Driven Lab 
# May 2020
# EU Cov scrape for coordinators and supporters

# Initialize
library(rvest)

# First start by scraping master lists for all actors for coordinator and supporters

coordinators <- html_nodes(read_html("https://www.covenantofmayors.eu/about/covenant-community/coordinators.html?tmpl=response&filter-search=&filter_country=&filter_commits=&filter_support=&filter_status=&filter_type=&filter_signin=&limit=0&filter_order=a.coordinator_name&filter_order_Dir=ASC"), "tr")
supporters <- html_nodes(read_html("https://www.covenantofmayors.eu/about/covenant-community/supporters.html?tmpl=response&filter-search=&filter_country=&filter_type=&filter_commits=&filter_signumber=&filter_signin=&limit=0&filter_order=a.date_of_adhesion&filter_order_Dir=ASC"), "tr")

# Coordinators 
# Extract all info on master list 
extract_coordinator <- function(node){
  text <- sapply(html_nodes(node, "td"), html_text)
  link <- html_attr(html_node(node, "a"), "href")
  data.frame("actor_name" = text[1],
             "country" = text[2], 
             "num_supported" = text[3],
             "sign_year" = text[4],
             "actor_link" = link,
             stringsAsFactors = F)
}

coordinators_scraped <- lapply(coordinators, extract_coordinator)
coordinators_scraped <- do.call(rbind, coordinators_scraped)

# Scrape link by link for more information 
extract_signatories_supported <- function(link){
  html <- read_html(gsub("overview", "signatories", link))
  if (length(xml_nodes(html, "td")) == 0){
    return(data.frame(sig_supported = NA, population = NA, adhesion_year = NA,
                      stringsAsFactors = F))
  } else {
    sig_supported <- paste(html_text(html_nodes(html, "td:nth-child(1)")), 
                           collapse = ";\n")
    population <- paste(html_text(html_nodes(html, "td:nth-child(2)")), 
                        collapse = ";\n")
    adhesion_year <- paste(html_text(html_nodes(html, "td:nth-child(3)")), 
                           collapse = ";\n")
    return(data.frame(sig_supported, population, adhesion_year,
                      stringsAsFactors = F))
  }
}

coordinators_sig_supported <- lapply(coordinators_scraped$actor_link, 
                                     extract_signatories_supported)
coordinators_sig_supported <- do.call(rbind, coordinators_sig_supported)
coordinators_scraped <- cbind(coordinators_scraped, coordinators_sig_supported)
save.path <- "../../../../output/actors/EU Covenant"

write.csv(coordinators_scraped, paste0(save.path, "/eucov_coordinators.csv"), 
          fileEncoding = "UTF-8", row.names = F)

# Supporters 
# Extract data from master list 
supporters_scraped <- lapply(supporters, extract_coordinator)
supporters_scraped <- do.call(rbind, supporters_scraped)
# Change name of col
names(supporters_scraped)[grep("country", names(supporters_scraped))] <- "type"
# Remove new line and tabs from the type col
supporters_scraped$type <- gsub("[\n\t]", "", supporters_scraped$type)
# Remove all white space from the num col
supporters_scraped$num_supported <- gsub("\\W", "", supporters_scraped$num_supported)
supporters_sig_supported <- lapply(supporters_scraped$actor_link,
                                   extract_signatories_supported)
supporters_sig_supported <- do.call(rbind, supporters_sig_supported)
supporters_scraped <- cbind(supporters_scraped, supporters_sig_supported)

write.csv(supporters_scraped, paste0(save.path, "/eucov_supporters.csv"),
          fileEncoding = "UTF-8", row.names = F)
