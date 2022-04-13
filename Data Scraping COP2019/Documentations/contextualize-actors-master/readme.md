### Anatomy of the package
- scraper
- scraper.contextuals
- scraper.actors

### scraper
- **get_contextuals**: runs all necessary contextual scraper outputs for a name, country, and entity_type
- **get_possible_names**: returns the titles of pages that redirect to a wikipedia page matching a name, country, and entity_type
- **get_country**: returns an iso code inferred from a wikipedia page matching a name, country, and entity_type combination
- **get_entity_type**: returns an entity type inferred from a wikipedia page matching a name, country, and entity_type combination
- **gapfill**: updates a pandas dataframe with contextuals from the get_contextuals function. 

### scraper.contextuals
- **wikipedia.get_data**
- **bloomberg.get_data**
- **hoovers.get_data**
- **util.geocode**

### scraper.actors
- **carbonn**: Most up to date version in jupyter notebook [CarbonnScraperInNotebook.ipynb](https://github.com/datadrivenyale/contextualize-actors/blob/master/scraper/src/actors/carbonn/CarbonnScraperInNotebook.ipynb)
- **EU Covenant of Mayors**: Most up to date version in jupyter notebook [EU Covenant of Mayors Scraper.ipynb](https://github.com/datadrivenyale/contextualize-actors/blob/master/scraper/src/actors/eu_covenant/EU%20Covenant%20of%20Mayors%20Scraper.ipynb)
- **nazca**

__work in progress. would like to develop scripts/modules for each actor source.__

### Full directory structure
https://docs.google.com/document/d/1W1BWMgDwLK352BXiiCJ3VcFTWXH0foNISWaiKfpZ560/edit?usp=sharing

### Adding a scraper
- This guide will be expanded
- Make sure to double check the __init__.py files. All you should have to do is add a line to contextuals/__init__.py
or actors/__init__.py and a line to the __init__.py in the directory you created.
