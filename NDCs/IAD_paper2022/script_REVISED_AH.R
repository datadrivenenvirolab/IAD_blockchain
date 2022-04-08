require(stm)
require(tm)
require(igraph)
require(Rmisc)
require(ggplot2)
require(dplyr)
require(tidyr)
require(formatR)
require(corrr)
require(rstudioapi)
library(tidytext)


# Read metadata
metadata <- read.csv("new_metadata.csv")

emission <- read.csv("emission.csv")
emission <- emission[emission$Year == 2014,]

countrypop <- read.csv("countrypop.csv", sep="\t") %>%
  select("Country.Name", "X2016")



set.seed(1234)

folder= rstudioapi::getActiveDocumentContext()$path 
setwd(dirname(dirname(folder)))
print( getwd() )
folder = getwd()
pttrn <- 'revised'


p <- 'EN'
files_2 <- list.files(path = folder, pattern = p)

files <- list.files(path=folder, pattern = pttrn)
f_files <- intersect(files, files_2) # these are just the NDCs



#filestocopy <- f_files
#origindir <- c(getwd())
#targetdir <- c("./IAD_paper2022/TARGET")
#flist <- list.files(filestocopy, full.names = TRUE)
#file.copy(filestocopy, targetdir)




words_rm <- read.csv("./IAD_paper2022/initial_stopwords-MCS.csv", stringsAsFactors = FALSE) # had to add stringAsFactors=FALSE
words_rm <- words_rm[words_rm$keep_stopword=="yes",]
stopwords <- c(words_rm$stopwords)


# stp <- data.frame(stopwords)
# write.csv(stp, "initial_stopwords.csv", row.names = F)



get_text <- function(entity){
  con <- file(description=entity)
  html <- readLines(con)
  close(con)
  return (html)
  }

htmls <- lapply(X=f_files,
                FUN=get_text)

htmls <- gsub("<(.|\n)*?>","",htmls)
htmls <- gsub("\\\\","",htmls)
htmls <- tolower(htmls)
htmls <- gsub("`na` = ", "", htmls)
htmls <- gsub('\\', "", htmls, fixed = T)
htmls <- gsub('\\\"', "", htmls)
htmls <- gsub(" , ", "", htmls)



tmdf<-read.csv("./IAD_paper2022/toMatch_NSA_words_updated.csv", stringsAsFactors = FALSE)
toMatch <- c(tmdf$NSA_word)

# append the toMatch vector the list of stopwords

stopwords <- append(stopwords, toMatch) 



toreplace <- c("\\\"", "\\\\n", "capacity building", "climate change adaptation",
               "industrial sector", "environmental sector", "transporation sector",
               "transport sector", "gas sector", "oil sector", "natural resource sector",
               "waste sector", "housing sector", "energy sector", "electricity sector",
               "forest sector", "forests sector", "forestry sector", "mining sector", 
               "agriculture sector", "tourism sector", "water sector", "food sector",
               "water use", "private sector", "water source", "water resource", 
               "water resources", "waste water", "water quality", "water shortage", 
               "water conservation", "water efficiency", "water supply", "water scarcity", 
               "water security", "water management", "electricity",
               "accompany", "accompanies", "[^[:alnum:][:blank:]+?&/\\-]")

replacewith <- c("", "", "capacitbuilding", "climchangeadapt", "industrialsect", 
                 "envsect", "transpesect", "transpsect", "fuelsect", "fuelsect", 
                 "natressect", "wastesect", "housesect", "energysect", "electsect", 
                 "forestsect", "forestsect", "forestsect", "miningsect", "agsect", 
                 "tourismsect", "watersect", "foodsect", "wateruse", "privatesect",
                 "waterresource", "waterresource", "waterresource", "wastewater", 
                 "waterquality", "watershortage", "waterconserv", "watereffic",
                 "watersupply", "watershortage", "watersecurity", "watermanage", 
                 "electric", "coexist", "coexist", "")



parse_sentences <- function(html, index) {
  sentences <- unlist(strsplit(html[index],split="\\."))
  gsub.mult <- function(n) {
    sentences <<- gsub(toreplace[n], replacewith[n], sentences)
  }
  sentences <- lapply(c(1:length(toreplace)), gsub.mult)[[length(toreplace)]]
  sentences <- paste(sentences, ".")
  
  for (sentence in sentences) {
    sentence <- sentence[nchar(sentence) > 10]
  }
  subset_sentences<-function(Match){
    sentences[grep(Match,sentences)]}
  subsetted <- lapply(toMatch, subset_sentences)
  subsetted <- unlist(subsetted[lapply(subsetted, length)>0])
  subsetted <- paste(subsetted, collapse ="")
  return(subsetted)
}



results = data.frame(matrix(NA, nrow = length(f_files), ncol = 1))
results_meta = data.frame(matrix(NA, nrow = length(f_files), ncol = 1))
colnames(results) <-c("result")
colnames(results_meta) <- c("meta")

for (i in c(1:length(f_files))) {
  results$result[i] <- parse_sentences(htmls, i)
  results_meta$meta[i] <- i
}


results <- results$result[results$result != ""]

results.df = data.frame(matrix(NA, nrow=length(f_files), ncol=2))
colnames(results.df) <-c("result", "meta")

for (i in c(1:length(f_files))) {
  results.df$result[i] <- parse_sentences(htmls, i)
  results.df$meta[i] <- i
}

write.csv(results.df, "./IAD_paper2022/REVISED_ndc_data.csv", row.names = FALSE)

results2 <- read.csv("./IAD_paper2022/REVISED_ndc_data.csv", stringsAsFactors = FALSE)
results2 <- results2[!results2$result == "",]


results <- gsub("\\s+na\\s+|na\\s+", " ", results2$result)


n_words <- function(i) {
  l <- data.frame(words = unlist(strsplit(as.character(results2$result[i]), " ")))
  return(nrow(l)) }

lengths <- unlist(lapply(seq(1, 124), n_words))

results2$result <- as.character(results2$result)
results2$result <- gsub(" na ", " ", results2$result)
results2$result <- gsub("\\s+", " ", results2$result)
results2$result <- gsub("[.]", "", results2$result)

vocab_size <- unlist(lapply(seq(1, 124), n_words))

lengths_begin <- unlist(lapply(seq(1, 124), n_words))

vocab_end <- unlist(lapply(seq(1, 124), n_words))


write.csv(results2, "./IAD_paper2022/revised_cleaned_ndc_data.csv", row.names = FALSE)

mtd_subset <- as.vector(unlist(results2['meta']))

htmls_processed_2 <- textProcessor(documents=results, metadata=metadata[mtd_subset,], 
                                   lowercase = TRUE, removestopwords=TRUE, 
                                   removenumbers = TRUE, removepunctuation = TRUE, 
                                   stem=F, wordLengths=c(4,20),
                                   striphtml = TRUE, language = "en", verbose=F, 
                                   customstopwords=stopwords)

plotRemoved(htmls_processed_2$documents, lower.thresh = seq(1, 5, by = 1))


prepped <- prepDocuments(htmls_processed_2$documents, 
                         htmls_processed_2$vocab, 
                         htmls_processed_2$meta, 
                         lower.thresh = 1)


# SAVE CORPUS
save(prepped, file = "./IAD_paper2022/Corpora/NDC_corpus_STM.Rdata")

topic_search <- stm::searchK(prepped$documents, 
                             prepped$vocab,
                             K = c(4,5,6,7,8,9,10,11,12,13,14,15), 
                             init.type="LDA",
                             N=floor(0.5*length(prepped$documents)), 
                             proportion=0.5, 
                             cores=4)


plot(topic_search)


stm_covariate_1 <- stm(documents=prepped$documents, 
                     vocab=prepped$vocab,
                     K = 6, 
                     data=prepped$meta, 
                     init.type="Spectral", 
                     verbose=FALSE, 
                     seed=1234)

labelTopics(stm_covariate_1, c(1:6))

par(mfrow=c(1,1))
plot(stm_covariate_1, type = "summary")

# ap_documents <- tidy(stm_covariate_1, matrix = "gamma") %>%
#   as.data.frame()
  
# write.csv(ap_documents,"document_topic_prob_k=8.csv")


metadata_subset <- metadata[metadata$X %in% results2$meta,]

results_stm <- make.dt(stm_covariate_1, meta=metadata_subset)
head(results_stm)
write.csv(results_stm, "./IAD_paper2022/results_stm_iter4_k=6.csv")

corrs <- topicCorr(stm_covariate_1, 
          method = c("simple", "huge"), 
          cutoff = 0.01, 
          verbose = TRUE)


plot(corrs, main = "Topic Correlations")


shortdoc <- sapply(results, substring, 1, 350)
shortdoc <- gsub(" na ", " ", shortdoc)
shortdoc <- unname(shortdoc)
shortdoc <- gsub("^ ", "", shortdoc)


make_shortdoc <- function(id, number) {
  temp <- unique(unlist(strsplit(results[id], "[.]")))
  return(temp)
}

first.sentence <- unlist(lapply(c(1:length(results)), make_shortdoc))
first.sentence <- first.sentence[nchar(first.sentence) < 500]

align.meta <- data.frame(meta=first.sentence)
first.sentence <- textProcessor(documents=first.sentence, metadata=align.meta, 
                                lowercase = TRUE, removestopwords=TRUE, 
                                removenumbers = TRUE, removepunctuation = TRUE, 
                                stem=F, wordLengths=c(4,20),
                                striphtml = TRUE, language = "en", verbose=F, 
                                customstopwords=stopwords)

first.sentence <- alignCorpus(first.sentence, prepped$vocab)

l <- fitNewDocuments(model = stm_covariate_1, 
                     documents = first.sentence$documents, 
                     origData = htmls_processed_2$meta)

first.sentence$meta <- gsub("\\s+{1,}", " ", first.sentence$meta)

# TOPIC 1
# pdf(file = "./figures/word-cloud/topic_1_cloud.pdf", width=6,height=6)
# dev.off()
stm::cloud(stm_covariate_1, topic = 1, max.words = 18)

# theta = matrix, shows you the probability of a document belonging to a topic

top_n <- first.sentence$meta[which(l$theta[,1] > 0.5)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #1 Quotes")


# TOPIC 2
stm::cloud(stm_covariate_1, 
           topic = 2, 
           max.words = 25)

top_n <- first.sentence$meta[which(l$theta[,2] > 0.9)]
plotQuote(top_n, 
          width=100, 
          text.cex = 1,
          main = "Topic #2 Quotes")


# TOPIC 3
stm::cloud(stm_covariate_1, 
           topic = 3, 
           max.words = 25)

top_n <- first.sentence$meta[which(l$theta[,3] > 0.95)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #3 Quotes")


# TOPIC 4
stm::cloud(stm_covariate_1, 
           topic = 4, 
           max.words = 20)

top_n <- first.sentence$meta[which(l$theta[,4] > 0.95)]
plotQuote(top_n[c(1,2,7,8,9,15)], 
          width=100, 
          text.cex = 1,
          main = "Topic #4 Quotes")

# TOPIC 5
stm::cloud(stm_covariate_1, 
           topic = 5, 
           max.words = 20)

top_n <- first.sentence$meta[which(l$theta[,5] > 0.8)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #5 Quotes")


# TOPIC 6
stm::cloud(stm_covariate_1, 
           topic = 6, 
           max.words = 25)

top_n <- first.sentence$meta[which(l$theta[,6] > 0.9)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #6 Quotes")

# TOPIC 7
stm::cloud(stm_covariate_1, 
           topic = 7, 
           max.words = 25)

top_n <- first.sentence$meta[which(l$theta[,7] > 0.9)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #7 Quotes")

# TOPIC 8
stm::cloud(stm_covariate_1, 
           topic = 8, 
           max.words = 25)

top_n <- first.sentence$meta[which(l$theta[,8] > 0.9)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #8 Quotes")


# TOPIC 9
stm::cloud(stm_covariate_1, 
           topic = 9, 
           max.words = 25)


# TOPIC 10
stm::cloud(stm_covariate_1, 
           topic = 10, 
           max.words = 25)

# TOPIC 11
stm::cloud(stm_covariate_1, 
           topic = 11, 
           max.words = 25)

# TOPIC 12
stm::cloud(stm_covariate_1, 
           topic = 12, 
           max.words = 25)


library(stringr)
mean(str_length(results2$result))
median(str_length(results2$result))

results2$result %>%
  str_count(.,'\\w+') %>%
  mean()



