library(ggfortify)

df <- df[df['income_group']!='',]

pca_res <- prcomp(df[4:7], scale. = FALSE)

df[,8] <- sapply(df[,8], as.factor)
# colnames(df)[8] <- 'Most Prevalent Topic'
p <- autoplot(pca_res, 
         data = df, 
         colour = 'most_prevalent_topic', 
         loadings = TRUE,
         loadings.label = TRUE,
         loadings.label.size = 4) + ggtitle("PCA Decomposition of Topic Proportions for All NGOs and IGOs \n (COP 2019, 4-topic LDA model, n = 1118)") + theme_classic()
p$labels$colour <- "Most Prevalent Topic"
p

g <- autoplot(pca_res, 
              data = df, 
              colour = 'income_group', 
              loadings = TRUE,
              loadings.label = TRUE,
              loadings.colour = "black",
              loadings.label.colour = "black",
              loadings.label.size = 4) + ggtitle("PCA Decomposition of Topic Proportions for All NGOs and IGOs \n (COP 2019, 4-topic LDA model, n = 1118)") + theme_classic()
g$labels$colour <- "Income Group"
g




