# SOLUTION 1: EXTRACTING THE NGO ORGANIZATION NAMES USING TABULIZER AND STRSPLIT

# Uploading the necessary libraries:
library(dplyr)
library(pdftools)
library(rJava)
library(tabulizer)
# Optional: setting the working directory (the pdf(s) to scrape should be in this directory)
setwd("/Users/stefan/Desktop/Data Scraping")

# Initializing the file path (or just the name if the working directory is properly set):
path = "COP2019.pdf"

# Extracting the text from the pdf in raw format:
tabul_text <- tabulizer::extract_text(path, pages = 215:357)

# "content" will store the (final) modified text (now it is just an empty vector)
content <- vector()

# "current" will store the current modification
# The first modification will be to split the text by the substring containing space and the newline character
current <- unlist(strsplit(tabul_text, "  \n"))

# Second and subsequent modifications: split the text by the title of participants: Mr./Ms./Sr./Sra.
current <- unlist(strsplit(current, "(?=\nMr[.])", perl = T))
current <- unlist(strsplit(current, "(?=\nMs[.])", perl = T))
current <- unlist(strsplit(current, "(?=\nSr[.])", perl = T))
current <- unlist(strsplit(current, "(?=\nSra[.])", perl = T))

# Remove newline characters from participants' and organizations' names
current <- gsub("[\r\n]", "", current)

# Eliminate empty strings generated after the cleaning process:
current <- current[current!=""]

# Finally, append the modifications to the "content" variable
content <- append(content, current)
#print(content)

# EXTRACING THE ORGANIZATION NAMES

# Initializing "organizations" as an empty vector:
ngo_organizations <- vector()

# Iterating through the "content":
for(i in 1:length(content)){
  if (stringr::str_sub(content[i],-1,-1) == " "){ # observing that, in general, the organization names in "content" end with a space
    ngo_organizations <- append(ngo_organizations, content[i])
  }
}

# Cleaning empty strings generated in the appending process:
ngo_organizations <- ngo_organizations[ngo_organizations != " "]
print(ngo_organizations)

# Further cleaning of organization names that contain the page header:
ngo_organizations<- gsub("FCCC/CP/2019/INF.4  *[[:digit:]][[:digit:]][[:digit:]] ", "", ngo_organizations)
print(ngo_organizations)

# Deleting organizations that contain the "(continued)" substring:

ngo_organizations <- ngo_organizations[-grep("[(]continued[)]", ngo_organizations)]
print(ngo_organizations)

# Dropping the first 6 elements, as these pertain to another category
ngo_organizations <- ngo_organizations[6:length(ngo_organizations)]
ngo_organizations



#text <- pdf_text("COP2019_sample.pdf") %>% readr::read_lines()
#print(text)


# GENERALIZING THE ORGANIZATION EXTRACTOR FUNCTION:

organization_extractor <- function(file_path, pages){
  tabul_text <- tabulizer::extract_text(file_path, pages)
  content <- vector()
  current <- unlist(strsplit(tabul_text, "  \n"))
  current <- unlist(strsplit(current, "(?=\nMr[.])", perl = T))
  current <- unlist(strsplit(current, "(?=\nMs[.])", perl = T))
  current <- unlist(strsplit(current, "(?=\nSr[.])", perl = T))
  current <- unlist(strsplit(current, "(?=\nSra[.])", perl = T))
  current <- gsub("[\r\n]", "", current)
  current <- current[current!=""]
  content <- append(content, current)
  
  organizations <- vector()
  for(i in 1:length(content)){
    if (stringr::str_sub(content[i],-1,-1) == " "){
      organizations <- append(organizations, content[i])
    }
  }
  organizations <- organizations[organizations != " "]
  organizations<- gsub("FCCC/CP/2019/INF.4  *[[:digit:]][[:digit:]][[:digit:]] ", "", organizations)
  organizations <- organizations[-grep("[(]continued[)]", organizations)]
  return (organizations)
}



