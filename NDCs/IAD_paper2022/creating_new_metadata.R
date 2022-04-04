file_iso <- substr(f_files, start = 1, stop = 3)

df <- data.frame(file_iso)

library(countrycode)

df['name'] <- countrycode(df[[1]], "iso3c", "country.name")
df['continent'] <- countrycode(df[[2]], "country.name", "continent")
write.csv(df, "new_metadata.csv", row.names = TRUE)
