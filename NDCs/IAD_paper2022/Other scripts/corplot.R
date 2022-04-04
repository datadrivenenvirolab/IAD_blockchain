createcorplot <- function(i) {
  #temp <- results_stm[results_stm$continent.x == i,]
  temp <- results_stm[,c(3:9)]
  d <- correlate(temp) %>%
    shave()
  print(d)
  return(rplot(d, print_cor = TRUE, shape = 16)+
           theme_bw()+
           theme(axis.text.x=element_text(angle=90),
                 panel.grid.major=element_blank(),
                 panel.grid.minor=element_blank(),
                 legend.position="none")+
           scale_x_discrete(labels=c(expression(paste(" Emissions \n reduction")), expression(paste(" Institutional \n Support")), expression(paste(" Renewable \n energy")), expression(paste(" Resiliency")), expression(paste("General NSA \n collaboration")), expression(paste(" Sectoral-specific \n collaboration")), expression(paste(" Policy and \n regulations")))) + 
           scale_y_discrete(labels=c(expression(paste(" Policy and \n regulations")), expression(paste(" Sectoral-specific \n collaboration")), expression(paste(" General NSA \n Collaboration")), expression(paste(" Resiliency")), expression(paste(" Renewable \n energy")), expression(paste(" Institutional \n Support")))))
}

d <- correlate(results_stm[,c(3:9)]) %>% shave()
l <- rplot(d, print_cor = TRUE, shape = 16)+
  theme_bw()+
  theme(axis.text.x=element_text(angle=90),
        panel.grid.major=element_blank(),
        panel.grid.minor=element_blank(),
        legend.position="none")+
  scale_x_discrete(labels=c(expression(paste(" Emissions \n reduction")),
                            expression(paste(" Vulnerability & \n Adaption")),
                            expression(paste(" Energy")), 
                            expression(paste(" Sector-specific \n Collaboration")), 
                            expression(paste(" Government & \n Policy Support")), 
                            expression(paste(" Collaboration \n with Civil Society")), 
                            expression(paste(" Monitoring")))) + 
  scale_y_discrete(labels=c(expression(paste(" Monitoring")), 
                            expression(paste(" Collaboration \n with Civil Society")), 
                            expression(paste(" Government & \n Policy Support")),
                            expression(paste(" Sector-specific \n Collaboration")),
                            expression(paste(" Energy")),
                            expression(paste(" Vulnerability & \n Adaption"))))

EUPlot <- createcorplot("EU") + ggtitle("Europe")
ggsave("Allplot.png", l, device="png", dpi=200,  width = 5, height = 5, units = "in")

ASPlot <- createcorplot("AS") + ggtitle("Asia")
ggsave("ASPlot.png", ASPlot, device="png", dpi=200,  width = 5, height = 5, units = "in")


AFPlot <- createcorplot("AF") + ggtitle("Africa")
ggsave("AFPlot.png", AFPlot, device="png", dpi=200,  width = 5, height = 5, units = "in")

SAPlot <- createcorplot("AS") + ggtitle("South America")
ggsave("SAPlot.png", SAPlot, device="png", dpi=200,  width = 5, height = 5, units = "in")

OCPlot <- createcorplot("OC") + ggtitle("Oceana")
ggsave("OCPlot.png", OCPlot, device="png", dpi=200,  width = 5, height = 5, units = "in")

NAPlot <- createcorplot("North America") + ggtitle("North America")
ggsave("NAPlot.png", NAPlot, device="png", dpi=200,  width = 5, height = 5, units = "in")

##### --------- ####
#### OUTDATED #####
#### __-------___ #####
ASPlot <- createcorplot("AS") + ggtitle("Asia")+
  theme(axis.text.x = element_blank())+
  scale_y_discrete(labels=c(expression(paste(" Policy and \n regulations")), expression(paste(" Sectoral \n collaboration")), expression(paste(" Collaboration \n with NSA")), expression(paste(" Resiliency \n implementation")), expression(paste(" Renewable \n energy")), expression(paste(" Institutional \n Support"))))
AFPlot <- createcorplot("AF") + ggtitle("Africa") +
  theme(axis.text.x = element_text(vjust=-1.9)) + 
  scale_x_discrete(labels=c(expression(paste(" Emissions \n reductions")), expression(paste(" Institutional \n Support")), expression(paste(" Renewable \n energy")), expression(paste(" Resiliency \n implementation")), expression(paste("Collaboration \n with NSA")), expression(paste(" Sectoral \n collaboration")), expression(paste(" Policy and \n regulations")))) + 
  scale_y_discrete(labels=c(expression(paste(" Policy and \n regulations")), expression(paste(" Sectoral \n collaboration")), expression(paste(" Collaboration \n with NSA")), expression(paste(" Resiliency \n implementation")), expression(paste(" Renewable \n energy")), expression(paste(" Institutional \n Support"))))
SAPlot <- createcorplot("SA") + ggtitle("South America")+
  theme(axis.text.x = element_blank(),
        axis.text.y = element_blank())
OCPlot <- createcorplot("OC") + ggtitle("Oceana")+
  theme(axis.text.x = element_blank(),
        axis.text.y = element_blank())
NAPlot <- createcorplot("North America") + ggtitle("North America") +
  theme(axis.text.y = element_blank(),
        axis.text.x = element_text(angle=0, vjust=-1.9))+
  scale_x_discrete(labels=c(expression(paste(" Emissions \n reductions")), expression(paste(" Institutional \n Support")), expression(paste(" Renewable \n energy")), expression(paste(" Resiliency \n implementation")), expression(paste(" Collaboration \n with NSA")), expression(paste(" Sectoral \n collaboration")), expression(paste(" Policy and \n regulations"))))

multiplot(EUPlot, ASPlot, AFPlot, SAPlot, OCPlot, NAPlot, cols=2)


createnetworkplot <- function(i) {
  #temp <- results_stm[results_stm$continent.x == i]
  temp <- results_stm
  temp <- temp[,c(3:9)]
  colnames(temp) <- c("Emissions.reduction", "Institutional.Support", "Renewable.energy",
                      "Resiliency.implementation", "Collaboration.NSA", "Collaboration.Sectoral",
                      "Policy.Regulation")
  d <- correlate(temp) %>%
    network_plot(min_cor=0.1)
  return(d)
}



createnetworkplot("NA")


