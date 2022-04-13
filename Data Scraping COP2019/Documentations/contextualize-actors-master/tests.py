
### IMPORT TESTS ###
### If any one of these fails, there's probably a problem with the __init__.py files.

import pandas as pd
import scraper

# scraper.py file
scraper.get_contextuals
scraper.get_contextuals('Google', 'USA', 'Company')
scraper.get_contextuals('New York', 'USA', 'City')

scraper.get_country('New York')
scraper.get_entity_type('New York')
scraper.get_possible_names('New York')

# contextual scraper imports.
scraper.contextuals.bloomberg.get_data
scraper.contextuals.hoovers.get_data
scraper.contextuals.wikipedia.get_data
scraper.contextuals.util.get_lat_long

# actor scraper imports.
scraper.actors.carbonn.get_data

# test currency conversion
scraper.contextuals.bloomberg.currency.convert('TWD', 'USD', 10)
scraper.contextuals.bloomberg.currency.rates

# test ticker resolution
scraper.contextuals.get_ticker('Google', 'USA', 2)

# more concrete company tests
scraper.contextuals.bloomberg.get_data('Foxconn', None, 'Company')
scraper.contextuals.bloomberg.get_data('Alphabet', None, 'Company')
scraper.contextuals.hoovers.get_data('British Airways', None, 'Company')

# more concrete subnational tests
scraper.contextuals.wikipedia.get_data('London', 'CAN', 'City')
scraper.contextuals.wikipedia.resolve_page('London', 'CAN', 'City')['page'].redirects
scraper.contextuals.wikipedia.get_data('Oxford', 'GBR', 'University')

# gapfill
companies = pd.read_csv('output/companies.csv')
companies = companies.sample(frac=1)
companies = pd.DataFrame(companies.head(50))

companies
