printf "\n\nScraping company categories\n"
python3 scripts/company_categories_scraper.py
printf "\n\nScraping individual commitments\n"
python3 scripts/NAZCA_individual.py
printf "\n\nScraping group initiatives\n"
python3 scripts/NAZCA_group.py
printf "\n\nCombining scraped CSVs\n"
python3 scripts/combine.py
printf "Final, combined data placed in the nazca_scraper folder in nazca.csv\n"
