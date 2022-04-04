library(dplyr)
library(reshape2)

final_data <- read.csv("data/all_countries_results.csv")
final_data <- final_data[,-c(1,10)]

# combine AI and AII
final_data$annex[final_data$annex == "II"] <- "I"
final_data <- final_data[-111,]
gathered <- data.table::melt(final_data)

gathered <- gathered %>%
  group_by(annex, ldc, variable) %>%
  summarise(mean = mean(value), sd = sd(value), n=n())

gathered$sem <- gathered$sd/(sqrt(gathered$n))
gathered$annex <- as.character(gathered$annex)
gathered$ldc <- as.character(gathered$ldc)
gathered$variable <- as.character(gathered$variable)
gathered$annex[gathered$annex == "I" | gathered$annex == "II"] <- "Annex I (n=9)"  # combine Annex I and II together 
gathered$annex[gathered$annex == "No"] <- "Non-Annex I (n=140)"
gathered$ldc[gathered$ldc == "Yes"] <- "LDCs (n=47)"
gathered$variable[gathered$variable == "Topic1"] <- "Emissions Reduction"
gathered$variable[gathered$variable == "Topic2"] <- "Vulnerability and Adaptation"
gathered$variable[gathered$variable == "Topic3"] <- "Energy"
gathered$variable[gathered$variable == "Topic4"] <- "Sector-specific Collaboration"
gathered$variable[gathered$variable == "Topic5"] <- "Government and Policy Support"
gathered$variable[gathered$variable == "Topic7"] <- "Civil society collaboration"
gathered$variable[gathered$variable == "Topic8"] <- "Monitoring"
gathered <- gathered[gathered$variable != "Topic6",]


ordering <- gathered %>% filter(annex == "Non-Annex I (n=140)") %>% group_by(variable) %>% summarise(m = mean(mean))
gathered <- data.frame(left_join(gathered, ordering))

pdf("figures/Figure2.pdf", width=8.5, height=4, useDingbats = F) # change to png for png
ggplot(gathered, aes(x=reorder(variable, m), y=mean, group=factor(ldc), color=factor(ldc)))+
  geom_point() +
  geom_errorbar(aes(ymin=mean-sem, ymax=mean+sem), width=0) +
  coord_flip()+
  facet_wrap(~annex) +
  theme_bw()+
  theme(panel.grid.minor = element_blank(),
        panel.grid.major = element_blank(),
        strip.background=element_blank())+
  xlab("")+
  ylab("Mean topic prevalence")+
  theme(panel.grid.minor = element_blank(), legend.position = "bottom",legend.direction = "horizontal", legend.title=element_blank())
dev.off()
