LTS_data <- read.csv("LTS_text_data.csv")
NDC_data <- read.csv("NDC_text_data.csv")
total <- rbind(NDC_data, LTS_data)
write.csv(total, "merged_NDC_LTS_texts.csv", row.names = FALSE)
