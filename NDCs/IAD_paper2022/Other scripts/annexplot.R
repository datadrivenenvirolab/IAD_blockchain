
final_data <- read.csv("data/all_countries_results.csv")
final_data[is.na(final_data)] <- 0
final_data <- final_data[,-1]
gathered <- gather(final_data, key, value, -name, -annex, -continent, -ghg)
gathered <- gathered %>%
  group_by(annex, key) %>%
  summarise(mean = mean(value), sd = sd(value), n=n())

gathered$sem <- gathered$sd/(sqrt(gathered$n))
gathered$annex <- as.character(gathered$annex)
gathered$annex[gathered$annex == "I"] <- "Annex I only (n=19)"
gathered$annex[gathered$annex == "II"] <- "Both Annex I&II (n=24)"
gathered$annex[gathered$annex == "No"] <- "Non-Annex I (n=148)"
gathered$key[gathered$key == "Topic1"] <- "Emissions Reduction"
gathered$key[gathered$key == "Topic2"] <- "Institutional Support"
gathered$key[gathered$key == "Topic3"] <- "Renewable Energy"
gathered$key[gathered$key == "Topic4"] <- "Resiliency"
gathered$key[gathered$key == "Topic5"] <- "General NSA Collaboration"
gathered$key[gathered$key == "Topic6"] <- "Sector-Specific Collaboration"
gathered$key[gathered$key == "Topic7"] <- "Policy & Regulations"
gathered <- gathered[gathered$key != "Topic8",]


ordering <- gathered %>% filter(annex == "Non-Annex I (n=148)") %>% group_by(key) %>% summarise(m = mean(mean))
gathered <- data.frame(left_join(gathered, ordering))

pdf("figures/Figure3.pdf", width=8.5) # change to png for png
ggplot(gathered, aes(x=reorder(key, m), y=mean))+
  geom_point() +
  geom_errorbar(aes(ymin=mean-sem, ymax=mean+sem), width=0) +
  coord_flip()+
  facet_wrap(~annex) +
  theme_bw()+
  theme(panel.grid.minor = element_blank(),
        panel.grid.major = element_blank(),
        strip.background=element_blank())+
  xlab("")+
  ylab("Mean topic prevalence")
dev.off()
