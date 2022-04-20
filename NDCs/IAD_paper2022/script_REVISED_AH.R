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
library(wesanderson)
library(hrbrthemes)
library(tidyverse)
library(ClimActor)
library(stargazer)
library(patchwork)

### This is a script adapted from Stefan's script_REVISED.R only focused on the combined NDC/LTS texts.
# setwd
setwd("/Users/angelhsu/Documents/GitHub/IAD_blockchain")

# source
source("src/reorder_within.R")

# Read metadata
# metadata <- read.csv("new_metadata.csv")

# emission <- read.csv("emission.csv")
# emission <- emission[emission$Year == 2014,]

# countrypop <- read.csv("countrypop.csv", sep="\t") %>%
#  select("Country.Name", "X2016")
set.seed(1234)

# stop words 
words_rm <- read.csv("NDCs/IAD_paper2022/initial_stopwords-MCS.csv", stringsAsFactors = FALSE) # had to add stringAsFactors=FALSE
words_rm <- words_rm[words_rm$keep_stopword=="yes",]
stopwords <- c(words_rm$stopwords)


# stp <- data.frame(stopwords)
# write.csv(stp, "initial_stopwords.csv", row.names = F)

# tmdf<-read.csv("NDCs/IAD_paper2022/toMatch_NSA_words_updated.csv", stringsAsFactors = FALSE)

# use NSA word list from Hsu, Brandt 2019 paper
tmdf <- c("company", "non-governmental", "nongovernmental", "subnational", "NGO","non-government", "investor", "organization",
          "investor", "city", "university", "corporation", "NGOs", "institution", "town", "municipality", "metropolis", "metropolitan",
          "district", "province", "territory", "county", "college", "private sector", "local government", "civil society", "non-profit", "business",
          "businesses")

toMatch <- tmdf

# append the toMatch vector the list of stopwords

stopwords <- append(stopwords, toMatch) 

# Next, we convert multi-word keywords into one word for the "bag of words" approach to STM (as shown in `toreplace` and `replacewith`), remove special characters, and remove sentences that are less than 10 characters. For example, the phrase "capacity building" was transformed to "capacitbuilding" to be recognized as a unique phrase. Sentences were identified by punctuation and all sentences referencing NSAs formed the corpus. 

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
               "accompany", "accompanies", "[^[:alnum:][:blank:]+?&/\\-]", "public participation", "climate change")

replacewith <- c("", "", "capacitbuilding", "climchangeadapt", "industrialsect", 
                 "envsect", "transpesect", "transpsect", "fuelsect", "fuelsect", 
                 "natressect", "wastesect", "housesect", "energysect", "electsect", 
                 "forestsect", "forestsect", "forestsect", "miningsect", "agsect", 
                 "tourismsect", "watersect", "foodsect", "wateruse", "privatesect",
                 "waterresource", "waterresource", "waterresource", "wastewater", 
                 "waterquality", "watershortage", "waterconserv", "watereffic",
                 "watersupply", "watershortage", "watersecurity", "watermanage", 
                 "electric", "coexist", "coexist", "", "publicparticipation", "climatechange")



parse_sentences <- function(html, index) {
  sentences <-  unlist(strsplit(html[index],split="\\.")) 
  # BoW replacement
  gsub.mult <- function(n) {
    sentences <<- gsub(toreplace[n], replacewith[n], sentences)
  }
  sentences <- lapply(c(1:length(toreplace)), gsub.mult)[[length(toreplace)]]
  sentences <- paste(sentences, ".")
  # removes sentences that have less than 10 characters
  for (sentence in sentences) {
    sentence <- sentence[nchar(sentence) > 10]
  }
  # subsets sentences for NSA mentions
  subset_sentences<-function(Match){
    sentences[grep(Match,sentences)]}
  subsetted <- lapply(toMatch, subset_sentences)
  subsetted <- unlist(subsetted[lapply(subsetted, length)>0])
  subsetted <- paste(subsetted, collapse ="") # combines all sentences together
  return(subsetted)
}


results = data.frame(matrix(NA, nrow = nrow(htmls), ncol = 1)) # previously length(f_files)
results_meta = data.frame(matrix(NA, nrow = nrow(htmls), ncol = 1))
colnames(results) <-c("result")
colnames(results_meta) <- c("meta")

for (i in 1:nrow(htmls)) {
  results$result[i] <- parse_sentences(htmls, i)
  results_meta$meta[i] <- i
}

results <- results$result[results$result != ""]

# combine with metadata 
results.df <- data.frame(text=results, doc_name=htmls_df$doc_name, doc_type=htmls_df$doc_type)

write.csv(results.df, "Parsed_ndc_lts_combined_data.csv", row.names = FALSE)

results2 <- read_csv("Parsed_ndc_lts_combined_data.csv")
results2 <- results2[!results2$result == "",]

results <- gsub("\\s+na\\s+|na\\s+", " ", results2$result)

## AH removed this part for now - summary stats calculated later
#n_words <- function(i) {
#  l <- data.frame(words = unlist(strsplit(as.character(results2$result[i]), " ")))
#  return(nrow(l)) }

#lengths <- unlist(lapply(seq(1, 124), n_words))

# additional cleaning - not sure why this is done here
results2$result <- as.character(results2$text)
results2$result <- gsub(" na ", " ", results2$text)
results2$result <- gsub("\\s+", " ", results2$text)
results2$result <- gsub("[.]", "", results2$text)

# vocab_size <- unlist(lapply(seq(1, 124), n_words))

# lengths_begin <- unlist(lapply(seq(1, 124), n_words))

# vocab_end <- unlist(lapply(seq(1, 124), n_words))


write.csv(results2, "revised_cleaned_ndc_data.csv", row.names = FALSE)

results2 <- read_csv("revised_cleaned_ndc_data.csv")
# stefan previous code to provide identifier
# mtd_subset <- as.vector(unlist(results2['meta']))

### need to add metadata 
# metadata_all <- results %>% dplyr::mutate(iso = substr(doc_name, 1,3)) %>%
#                dplyr::select(iso, doc_name) %>%
#                mutate(iso = toupper(iso), length=nchar(iso),
#                       iso = case_when(length < 3 ~ NA, TRUE ~ iso)) %>%
#                dplyr::select(-length) %>%
#                write_csv("../Merged Texts NDC and LTS/metadata_all.csv") # then hand filled

### AH STARTED HERE
##### read in combined LTS/NDC Corpus
results2 <- read_csv("Merged Texts NDC and LTS/merged_NDC_LTS_texts.csv") 

# mutate text column in metadata_all
metadata_all <- read_csv("Merged Texts NDC and LTS/metadata_all.csv")

metadata_all <- metadata_all %>% left_join(results2 %>% dplyr::select(result, doc_name))

### additional cleaning - BoW replacements
results2 <- results2 %>% mutate(text = str_replace_all(text, "public participation", "publicparticipation"),
                                text = str_replace_all(text, "climate change", "climatechange"))

htmls_processed_2 <- textProcessor(documents=results2$text, metadata=metadata_all,
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
save(prepped, file = "Merged Texts NDC and LTS/Corpora/NDC_LTS_corpus_STM_041522.Rdata")

### test k=6 and k=9 as well as Spectral/LDA 
topic_search <- stm::searchK(prepped$documents, 
                             prepped$vocab,
                             K = c(4,5,6,7,8,9,10,11,12,13,14,15), 
                             init.type="Spectral",
                             N=floor(0.5*length(prepped$documents)), 
                             proportion=0.5, 
                             cores=4, seed=1234)


plot(topic_search) 


stm_covariate_1 <- stm(documents=prepped$documents, 
                     vocab=prepped$vocab,
                     K = 9, 
                     data=prepped$meta, 
                     init.type="Spectral", 
                     verbose=FALSE, 
                     seed=1234)

labelTopics(stm_covariate_1, c(1:9))

pdf("plots/ndc_lts_top_topics_8_topic_041522.pdf", width=8.5)
par(mfrow=c(1,1))
plot(stm_covariate_2, type = "summary")
dev.off()
  
# write.csv(ap_documents,"document_topic_prob_k=8.csv")

# write out results
actor_stm <- data.frame(prepped$meta, stm_covariate_1$theta)

# add a column that puts the top topic for each actor
for(i in 1:nrow(actor_stm)){
  actor_stm$top_topic[i] <- which.max(actor_stm[i,colnames(actor_stm[,grep("X[0-9]", colnames(actor_stm))])])
}

#write out file
write_csv(actor_stm, "Merged Texts NDC and LTS/actor_stm_041522.csv")

corrs <- topicCorr(stm_covariate_1, 
          method = c("simple", "huge"), 
          cutoff = 0.01, 
          verbose = TRUE)


pdf("plots/ndc_lts_topic_corrs.pdf")
plot(corrs, main = "Topic Correlations")
dev.off()

shortdoc <- sapply(prepped$meta$text, substring, 1, 500)
shortdoc <- paste(prepped$meta$doc_name,
                  prepped$meta$iso,
                  prepped$meta$doc_type,
                  ' - ',
                  shortdoc)

### AH revision - looping through to export word clouds
K <- 9
for (i in 1:K) {
  png(filename=paste("Merged Texts NDC and LTS/figures/", i, "word_cloud.png", sep=""))
  stm::cloud(stm_covariate_1, topic=i, max.words=20)
  dev.off()
  
  png(filename=paste("Merged Texts NDC and LTS/figures/", i, "word_samples.png", sep=""), height=700, width=700)
  thoughts1 <- findThoughts(stm_covariate_1, texts=shortdoc, n=10, topics=c(i))
  plotQuote(thoughts1$docs[[1]][c(1,2,3,5)], width=80, text.cex=0.9)
  dev.off()
}

# TOPIC 1
pdf("Merged Texts NDC and LTS/figures/ndc_lts_word-cloud/topic_1_cloud.pdf", width=6,height=6)
stm::cloud(stm_covariate_1, topic = 1, max.words = 18)
dev.off()

# theta = matrix, shows you the probability of a document belonging to a topic

top_n <- first.sentence$meta[which(l$theta[,1] > 0.5)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #1 Quotes")


# TOPIC 2
pdf(file = "Merged Texts NDC and LTS/figures/ndc_lts_word-cloud/topic_2_cloud.pdf", width=6,height=6)
stm::cloud(stm_covariate_1, topic = 2, max.words = 18)
dev.off()

top_n <- first.sentence$meta[which(l$theta[,2] > 0.9)]
plotQuote(top_n, 
          width=100, 
          text.cex = 1,
          main = "Topic #2 Quotes")


# TOPIC 3
pdf(file = "Merged Texts NDC and LTS/figures/ndc_lts_word-cloud/topic_3_cloud.pdf", width=6,height=6)
stm::cloud(stm_covariate_1, 
           topic = 3, 
           max.words = 25)
dev.off()

top_n <- first.sentence$meta[which(l$theta[,3] > 0.95)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #3 Quotes")


# TOPIC 4
pdf(file = "Merged Texts NDC and LTS/figures/ndc_lts_word-cloud/topic_4_cloud.pdf", width=6,height=6)
stm::cloud(stm_covariate_1, 
           topic = 4, 
           max.words = 20)
dev.off()

top_n <- first.sentence$meta[which(l$theta[,4] > 0.95)]
plotQuote(top_n[c(1,2,7,8,9,15)], 
          width=100, 
          text.cex = 1,
          main = "Topic #4 Quotes")

# TOPIC 5
pdf(file = "Merged Texts NDC and LTS/figures/ndc_lts_word-cloud/topic_5_cloud.pdf", width=6,height=6)
stm::cloud(stm_covariate_1, 
           topic = 5, 
           max.words = 20)
dev.off()

top_n <- first.sentence$meta[which(l$theta[,5] > 0.8)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #5 Quotes")


# TOPIC 6
pdf(file = "Merged Texts NDC and LTS/figures/ndc_lts_word-cloud/topic_6_cloud.pdf", width=6,height=6)
stm::cloud(stm_covariate_1, 
           topic = 6, 
           max.words = 25)
dev.off()

top_n <- first.sentence$meta[which(l$theta[,6] > 0.9)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #6 Quotes")

# TOPIC 7
pdf(file = "Merged Texts NDC and LTS/figures/ndc_lts_word-cloud/topic_7_cloud.pdf", width=6,height=6)
stm::cloud(stm_covariate_1, 
           topic = 7, 
           max.words = 25)
dev.off()

top_n <- first.sentence$meta[which(l$theta[,7] > 0.9)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #7 Quotes")

# TOPIC 8
pdf(file = "Merged Texts NDC and LTS/figures/ndc_lts_word-cloud/topic_8_cloud.pdf", width=6,height=6)
stm::cloud(stm_covariate_1, 
           topic = 8, 
           max.words = 25)
dev.off()

top_n <- first.sentence$meta[which(l$theta[,8] > 0.9)]
plotQuote(top_n[1:8], 
          width=100, 
          text.cex = 1,
          main = "Topic #8 Quotes")


# TOPIC 9
pdf(file = "Merged Texts NDC and LTS/figures/ndc_lts_word-cloud/topic_9_cloud.pdf", width=6,height=6)
stm::cloud(stm_covariate_1, 
           topic = 9, 
           max.words = 25)
dev.off()


#### PLOTS ####
# mean topic prevalence by document type 
# top terms plot
topics <- tidy(stm_covariate_1)

top_terms <- topics %>%
  group_by(topic) %>%
  top_n(10, beta) %>%
  ungroup() %>%
  arrange(topic, -beta)

pal <- wes_palette("Darjeeling1", 9, type = "continuous")

labels <- c("1"="1. Monitoring and Planning",
            "2"= "2. International Organizations",
            "3"="3. Public Institutions",
            "4"="4. Adaptation",
            "5"="5. NSA Institutions",
            "6"="6. Public and Citizen Measures",
            "7"="7. Adaptation and Development",
            "8"="8. Government and Business",
            "9"="9. Women and Gender")

cairo_pdf("plots/top_terms_per_topic_ndc_lts_041522.pdf", width=10, height=9)
top_terms %>%
  mutate(term = reorder_within(term, beta, topic)) %>%
  ggplot(aes(beta, term, fill = factor(topic))) +
  geom_col(show.legend = FALSE) +
  scale_fill_manual(values=pal)+
  facet_wrap(~ topic, scales = "free", labeller=as_labeller(labels)) +
  scale_y_reordered() +
  theme_ipsum()
dev.off()

# add topic prevalences to actor stm
actor_stm_new <- data.frame(prepped$meta, stm_covariate_1$theta)

# match in developing/developed country and region
dict <- read.csv("~/Documents/GitHub/text-analysis/input/country_dict.csv", header=T, stringsAsFactors = F)
actor_stm_new$dev_develping <- dict$dev_develping[match(actor_stm_new$iso, dict$iso)]
actor_stm_new$region <- dict$region[match(actor_stm_new$iso, dict$iso)]

# some region are missing
sel <- which(is.na(actor_stm_new$region))
actor_stm_new$region[sel] <- "Europe"

# some missing developed/developing
sel <- which(is.na(actor_stm_new$dev_develping))
actor_stm_new$dev_develping[sel] <- "developed"

table(actor_stm_new$dev_develping) # 81 developed; 102 developing
table(actor_stm_new$region)

# plot 
# pal <- wes_palette("Darjeeling1", 9, type = "continuous")

cairo_pdf("plots/actor_region_distribution_041522.pdf", width=4.5, height=6)
actor_stm_new %>% group_by(region) %>%  mutate(count = n(), region=str_replace_all(region, "Latin America and Caribbean", "Latin America\nand Caribbean"),
                                               region=str_replace_all(region, "East Asia and the Pacific", "East Asia\nand the Pacific"), region=str_replace_all(region, "Middle East and North Africa", 
                                                                                                                                                                 "Middle East\nand North Africa"), region=str_replace_all(region, "Europe and Central Asia", "Europe\nand Central Asia"),) %>%
  ggplot(aes(x=reorder(region, count), fill=region)) +
  geom_bar(show.legend=FALSE, fill="#00A08A")+
  geom_text(stat='count', aes(label=..count..), vjust=-1)+
  #scale_fill_manual(values=pal) +
  labs(y="Number of cities", x="") +
  theme_ipsum() +
  theme(axis.text.x = element_text(angle=90))
dev.off()

## Mean probability of topics plot
docs_gamma_stm <- tidy(stm_covariate_1, matrix = "gamma") # doesn't have the actors associated

# filter the actor_stm for relevant columns
actor_stm_new$document <- seq(1:nrow(actor_stm_new))

# join the entity_types with the docs_gamma_stm
docs_gamma_stm <- docs_gamma_stm %>%
  left_join(actor_stm_new, by="document")

# write out the means
gamma_stats <- docs_gamma_stm %>%
  group_by(dev_develping, topic) %>%
  summarise(mean = mean(gamma), sd=sd(gamma))

# stacked bar chart of topic prevalence
df_labels <- data.frame(topic=seq(1,9,1), labels=labels)
gamma_stats$topic_label <- df_labels$labels[match(gamma_stats$topic, df_labels$topic)]

# count of distinct developed/developing
actor_stm_new %>% distinct(iso, dev_develping) %>% group_by(dev_develping) %>% summarise(count=n())

cairo_pdf("plots/topic_gamma_by_actor_041522.pdf", width=8.5, height=6)
gamma_actor <- gamma_stats %>% mutate(dev_develping=str_replace_all(dev_develping, "developing", "developing (n=84)"),
                       dev_develping=str_replace_all(dev_develping, "developed", "developed (n=41)")) %>%
  ggplot(aes(x=topic, y=mean, fill=dev_develping))+
  geom_bar(stat="identity") +
  geom_text(aes(label=ifelse(dev_develping=="developed (n=41)", as.character(topic_label), "")),stat="identity", position = "identity", angle=90, vjust=0.5, hjust=-.05, check_overlap=TRUE, family = "Myriad Pro Light", size=3)+
  scale_fill_manual(name="", values=c("#E63946","#6BB3DD"))+
  #scale_x_continuous(breaks=c(seq(1,9,1)))+
  xlab("")+
  ylab("Mean Probability")+
  theme_ipsum() +
  theme(axis.text.x=element_blank(), axis.ticks.x=element_blank(), legend.position = c(0.15, 0.85), 
        legend.title=element_blank(), legend.text=element_text(size=12),  legend.background = element_rect(linetype = 1, size = 0.25, colour = 1))
gamma_actor
dev.off()

# by document type
actor_stm_new %>% distinct(iso, doc_type) %>% group_by(doc_type) %>% summarise(count=n())

gamma_stats <- docs_gamma_stm %>%
  group_by(doc_type, topic) %>%
  summarise(mean = mean(gamma), sd=sd(gamma))

gamma_stats$topic_label <- df_labels$labels[match(gamma_stats$topic, df_labels$topic)]

cairo_pdf("plots/topic_gamma_by_doc_type_041522.pdf", width=8.5, height=6)
gamma_doc <- gamma_stats %>% mutate(doc_type=str_replace_all(doc_type, "NDC", "NDC (n=118)"),
                       doc_type=str_replace_all(doc_type, "LTS", "LTS (n=49)")) %>%
  ggplot(aes(x=topic, y=mean, fill=doc_type))+
  geom_bar(stat="identity")+
  geom_text(aes(label=ifelse(doc_type=="LTS (n=49)", as.character(topic_label), "")),stat="identity", position = "identity", angle=90, vjust=0.5, hjust=-.05, check_overlap=TRUE, family = "Myriad Pro Light", size=3)+
  scale_fill_manual(name="", values=c("#00A08A", "#F2AD00"))+
  #scale_x_continuous(breaks=c(seq(1,9,1)))+
  xlab("")+
  ylab("Mean Probability")+
  theme_ipsum() +
  theme(axis.text.x=element_blank(), axis.ticks.x=element_blank(), legend.position = c(0.15, 0.85), 
        legend.title=element_blank(), legend.text=element_text(size=12),  legend.background = element_rect(linetype = 1, size = 0.25, colour = 1))
gamma_doc
dev.off()

# together side by side
cairo_pdf("plots/topic_gamma_side_by_side_041522.pdf", width=12.75, height=6)
gamma_actor + gamma_doc
dev.off()

## mean expected topic probabilities
gamma_terms <- docs_gamma_stm %>%
  group_by(topic) %>%
  summarise(gamma = round(mean(gamma),2)) %>%
  arrange(topic) %>%
  write_csv("output/topic_probabilities.csv")


### map plot
require(rgeos)
require(rgdal)
map <- readOGR("~/Documents/GitHub/text-analysis/NDC STM/data/countries.geo.json")
library(tidyr)
library(broom)
map <- gBuffer(map, byid=TRUE, width=0)
worldRobinson <- spTransform(map, CRS("+proj=robin +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"))
map <- gBuffer(worldRobinson, byid=TRUE, width=0)
map.df <- invisible(tidy(map))
map.df <- invisible(tidy(map, region = "name"))

# clean names
map.df$id[map.df$id == "United Republic of Tanzania"] <- "Tanzania"
map.df$id[map.df$id == "Democratic Republic of the Congo"] <- "Dem. Rep. Congo"
map.df$id[map.df$id == "Republic of Serbia"] <- "Serbia"

# nsa references
nsa_reference <- results2 %>% mutate(NSA_general=case_when(str_detect(text, paste(tmdf, collapse="|")) ~ "Yes", TRUE ~ "No"),
  Company=case_when(str_detect(text, "company|privatesect|corporation|business")~"Yes", TRUE ~ "No"),
                                    Local_govt=case_when(str_detect(text, "city|cities|local government|town|municipality|county|province") ~ "Yes", TRUE ~ "No"),
                                    NGOs=case_when(str_detect(text, "NGO|ngo|civil society|non-profit|non profit") ~ "Yes", TRUE ~ "No")) %>%
  left_join(metadata_all %>% dplyr::select(iso, doc_name))

facet_labels <-  c(
  'Revised NDC'="Revised NDC (n=124)",
  'LTS'="Long-term Strategy (n=59)")

# bar chart showing mentions 
cairo_pdf("plots/nsa_mentions_by_type_noNSAgeneral_041522.pdf", width=8.5, height=6)
nsa_reference %>% pivot_longer(NSA_general:NGOs, names_to="NSA_type", values_to="Mention") %>%
  filter(doc_type=="Revised NDC") %>%
  count(NSA_type, doc_type, Mention) %>%    # Group by region and species, then count number in each group
  mutate(n) %>%
  ungroup() %>%
  group_by(NSA_type, doc_type) %>%
  mutate(n_group=n, pct=n/sum(n_group)*100) %>%
  bind_rows(nsa_reference %>% pivot_longer(NSA_general:NGOs, names_to="NSA_type", values_to="Mention") %>%
              filter(doc_type=="LTS") %>%
              count(NSA_type, doc_type, Mention) %>%    # Group by region and species, then count number in each group
              mutate(n) %>%
              ungroup() %>%
              group_by(NSA_type, doc_type) %>%
              mutate(n_group=n, pct=n/sum(n_group)*100)) %>%
  filter(NSA_type != "NSA_general") %>%
  ggplot(aes(x=NSA_type, y=pct, fill=Mention))+
  geom_col(stat="count") +
   geom_text(aes(label=ifelse(doc_type=="LTS (n=49)", as.character(topic_label), "")),stat="identity", position = "identity", angle=90, vjust=0.5, hjust=-.05, check_overlap=TRUE, family = "Myriad Pro Light", size=3)+
   scale_fill_manual(name="", values=c("#D73027", "#4575B4"))+
#  scale_x_continuous(breaks=c(seq(1,30,1)))+
  xlab("")+
  ylab("Percentage")+
  theme_ipsum() +
  facet_wrap(~doc_type, labeller = as_labeller(facet_labels)) +
  theme(legend.position = "bottom", 
        legend.title=element_blank(), legend.text=element_text(size=12),  legend.background = element_rect(linetype = 1, size = 0.25, colour = 1))
dev.off()

# add country/iso to nsa reference
nsa_reference_count <- nsa_reference %>% left_join(metadata_all %>% dplyr::select(iso, doc_name)) %>%
                 gather("key", "value", c(Company, Local_govt, NGOs)) %>% 
                 group_by(iso, key, value) %>%
                 filter(value !="No") %>%
                 summarise(n=n()) %>%
                 group_by(iso) %>%
                 mutate(total=sum(n), total=case_when(total > 3 ~ 3, TRUE ~ as.numeric(total)))

nsa_reference_count$id <- country_dict$right[match(nsa_reference_count$iso, country_dict$iso)]
nsa_reference_count$dev_develping <- actor_stm_new$dev_develping[match(nsa_reference_count$iso, actor_stm_new$iso)]

## distribution of nsa counts by dev_devlping

nsa_reference_count <- nsa_reference_count %>% dplyr::rename("ref"="total")
map.df <- map.df %>% left_join(nsa_reference_count) %>%
          left_join(nsa_reference %>% dplyr::select(NSA_general, iso)) 

map.df$ref[is.na(map.df$ref) & map.df$NSA_general == "Yes"] <- 4 


map.df$ref[map.df$id == "Greenland"] <- NA
map.df$ref[map.df$id == "Antarctica"] <- NA
map.df$ref[map.df$id == "Western Sahara"] <- NA


cairo_pdf("plots/map_nsa_references_041522.pdf", width=11)
map.df %>% mutate(ref = as.character(ref), ref = str_replace_all(ref, "1", "1xCompany/Local_govt/NGO"), ref=str_replace_all(ref, "2", "2xCompany/Local/govt/NGO"),
                  ref = str_replace_all(ref, "3", "All: Company/Local_govt/NGO"),
                  ref = str_replace_all(ref, "4", "Any NSA mention")) %>%
ggplot(aes(x=long, y=lat)) +
  geom_polygon(aes(group=group, fill = as.factor(ref)), color = "grey60", size=0.35)+
  theme_void()+
  scale_fill_brewer(palette="Pastel1", name = "Reference to NSA", na.value="grey95")+
  theme(legend.box="horizontal", legend.position=c(0.5,0.175), legend.direction = "horizontal")+
  guides(fill=guide_legend(title.position="top"))
dev.off()

# map that also has number of NGO actors labeled
ngo_actors <- read_csv("Data Scraping COP2019/2019_NGO_country_stats.csv") %>%
              rename("iso"= "ISO3", "country"="Country")

# clean names
ngo_actors <- clean_country_iso(ngo_actors, country_dict, iso = 3, clean_enc = F)
ngo_actors <- fuzzify_country(ngo_actors, country_dict)

map.df <- map.df %>% left_join(ngo_actors %>% dplyr::select(iso, "ngo_count"="Count"))

# need centroids
centroids <- read_csv("data/country_centroids.csv")
centroids <- clean_country_iso(centroids, country_dict, iso = 3, clean_enc = F)
centroids <- fuzzify_country(centroids, country_dict)
centroids <- clean_country_iso(centroids, country_dict, iso = 3, clean_enc = F)

# convert to robinson projection
library(sf)
centroids <- st_as_sf(centroids, coords = c("longitude", "latitude"), crs=4326)
centroids <- st_transform(centroids, crs = 54030) 

centroids <- centroids %>% dplyr::mutate(cent_lon = sf::st_coordinates(.)[,1],
                                         cent_lat = sf::st_coordinates(.)[,2])

# join 
map.df <- map.df %>% left_join(centroids %>% dplyr::select(cent_lon, cent_lat, iso), by=c("iso")) 

cairo_pdf("plots/map_nsa_references_ngos_041522.pdf", width=11)
map.df %>% mutate(ref = as.character(ref), ref = str_replace_all(ref, "1", "1xCompany/Local_govt/NGO"), ref=str_replace_all(ref, "2", "2xCompany/Local/govt/NGO"),
                  ref = str_replace_all(ref, "3", "All: Company/Local_govt/NGO"),
                  ref = str_replace_all(ref, "4", "Any NSA mention")) %>%
  ggplot(aes(x=long, y=lat)) +
  geom_polygon(aes(group=group, fill = as.factor(ref)), color = "grey60", size=0.35)+
  geom_text(aes(label = ngo_count, x = cent_lon, y = cent_lat)) +
  theme_void()+
  scale_fill_brewer(palette="Pastel1", name = "Reference to NSA", na.value="grey95")+
  theme(legend.box="horizontal", legend.position=c(0.5,0.175), legend.direction = "horizontal")+
  guides(fill=guide_legend(title.position="top"))
dev.off()

### Descriptive stats
corpus <- actor_stm_new %>% dplyr::select(iso:doc_type, dev_develping, region) %>% left_join(results %>% dplyr::select(text, doc_name)) %>%
          mutate(doc_length=nchar(text))


# summary stats ### doesn't work as expected
corpus %>%
  dplyr::select(doc_type, dev_develping, doc_length) %>%
  split(. $doc_type) %>%
  walk(~ stargazer(., type = "text" ,
            title = "Summary Statistics by Document type", 
            summary = TRUE, 
            out = "output/ds_doctype.txt"))

# by doc_type 
corpus %>%
  dplyr::select(doc_type, dev_develping, doc_length) %>%
  group_by(doc_type) %>%
  summarise(n=n(), min=min(doc_length), max=max(doc_length), mean=round(mean(doc_length),2), sd=round(sd(doc_length),2)) %>%
  stargazer(.,                 # Export txt
            summary = FALSE,
            type = "text",
            out = "output/ds_doctype.txt")

# by dev/devlping
corpus %>%
  dplyr::select(doc_type, dev_develping, doc_length) %>%
  group_by(dev_develping) %>%
  summarise(n=n(), min=min(doc_length), max=max(doc_length), mean=round(mean(doc_length),2), sd=round(sd(doc_length),2)) %>%
  stargazer(.,                 # Export txt
            summary = FALSE,
            type = "text",
            out = "output/ds_dev_devlping.txt")

# word collocation
ndc_trigrams <- results2 %>%
  filter(doc_type == "Revised NDC") %>%
  unnest_tokens(trigram, text, token = "ngrams", n = 3) %>%
  mutate(trigram = str_replace_all(trigram, "[:digit:]", "")) %>%
  mutate_all(na_if,"") %>%
  separate(trigram, c("word1", "word2", "word3"), sep = " ") %>%
  filter(nchar(word1) > 3, nchar(word2) > 3, nchar(word3) > 3) %>%
  filter(!word1 %in% c(stopwords, stop_words$word, "^[:digit:]+$"),
         !word2 %in% c(stopwords, stop_words$word, "^[:digit:]+$"),
         !word3 %in% c(stopwords, stop_words$word, "^[:digit:]+$")) %>%
  count(word1, word2, word3, sort = TRUE) %>%
  filter(word1 != "", word2 !="", word3 !="") %>%
  arrange(desc(n))

lts_trigrams <- results2 %>%
  filter(doc_type == "LTS") %>%
  unnest_tokens(trigram, text, token = "ngrams", n = 3) %>%
  mutate(trigram = str_replace_all(trigram, "[:digit:]", "")) %>%
  mutate_all(na_if,"") %>%
  separate(trigram, c("word1", "word2", "word3"), sep = " ") %>%
  filter(nchar(word1) > 3, nchar(word2) > 3, nchar(word3) > 3) %>%
  filter(!word1 %in% c(stopwords, stop_words$word, "^[:digit:]+$"),
         !word2 %in% c(stopwords, stop_words$word, "^[:digit:]+$"),
         !word3 %in% c(stopwords, stop_words$word, "^[:digit:]+$")) %>%
  count(word1, word2, word3, sort = TRUE) %>%
  filter(word1 != "", word2 !="", word3 !="") %>%
  arrange(desc(n))

# plots
cairo_pdf("plots/word_collocations_ndc_041522.pdf")
ndc_trigrams_plot <- ndc_trigrams %>% mutate(trigrams = paste(word1, word2, word3, sep="-")) %>%
  slice_max(order_by = n, n=25) %>%
ggplot(aes(x=reorder(trigrams, n), y=n, fill="#E63946")) +
  geom_col() + 
  scale_fill_manual(values="#E63946", guide=FALSE)+
  coord_flip() +
  labs(x=NULL, y="Count",
       title="NDCs")+
  theme_ipsum()
ndc_trigrams_plot
dev.off()

cairo_pdf("plots/word_collocations_lts_041522.pdf")
lts_trigrams_plot <- lts_trigrams %>% mutate(trigrams = paste(word1, word2, word3, sep="-")) %>%
  filter(!str_detect(trigrams, "cidcidcid")) %>%
  slice_max(order_by = n, n=25) %>%
  ggplot(aes(x=reorder(trigrams, n), y=n, fill="#046C9A")) +
  geom_col() + 
  scale_fill_manual(values="#046C9A", guide=FALSE)+
  coord_flip() +
  labs(x=NULL, y="Count",
       title="LTSs")+
  theme_ipsum()
lts_trigrams_plot
dev.off()

cairo_pdf("plots/word_collocations_both_041522.pdf", width=11)
ndc_trigrams_plot + lts_trigrams_plot
dev.off()
