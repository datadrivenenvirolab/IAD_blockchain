folder <- rstudioapi::getActiveDocumentContext()$path 
file <- paste0(dirname(folder), "/foreign_LTS_texts/foreign_LTS_texts_translated.csv")
truncated <- read.csv(file)

M <- max(nchar(truncated$text))

S <-sort(nchar(truncated$text), decreasing = TRUE)
S[1:10]

pos <- which(nchar(truncated$text)==M)
truncated$text[pos]

truncated <- truncated[-pos,]

my_function <-function(x){
  return (paste(x, collapse=" "))
}
df <- aggregate(truncated$Text_translated, by=list(truncated$file_name), my_function)
names(df)[names(df) == 'Group.1'] <- 'file_name'
names(df)[names(df) == 'x'] <- 'translated_text'

df$file_name <- substring(df$file_name,3)

setwd(folder)

for (i in 1:length(df$file_name)){
  cat(df$translated_text[i], file = df$file_name[i])
}

