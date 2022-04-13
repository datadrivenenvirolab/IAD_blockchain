# Zhi Yi Yeo
# Data-Driven Lab
# ICLEI Scraper

# Load libraries needed
library(rvest)

# 9 pages in total to iterate through

pages <- 1:9

# Iterate through the different pages to get all the HTML to scrape 
iterate_url <- "https://iclei.org/en/members-search.html?order_by=1&page="
html <- lapply(paste0(iterate_url, pages), read_html)

# Start by combining all the nodes together into one big nodeset
members_list <- lapply(html, html_nodes, ".members-list")


# Write function to scrape data 

# Finding name
html_text(xml_find_all(xml_child(members_list[[1]][[1]], 1), "//a[@id][@class = 'open']"))
# Finding country 
html_text(xml_find_all(members_list[[1]], "//a[@id][@class = 'open']//span"))

# Leaders' names 
html_text(xml_find_all(members_list[[1]], 
                       "//div[@class = 'text-holder']//strong[@class = 'info']"))



nodes <- members_list[[1]] %>% html_nodes(".open")
info_node <- members_list[[1]] %>% html_nodes(".info")
html_nodes(html9, ".members-list")