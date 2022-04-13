
# coding: utf-8

# In[165]:

# Cameron Yick
# 10/14/2016
# Thursday Evening


# In[119]:

import os
import pandas as pd
import matplotlib.pyplot as plt

# scraper boilerplate
from bs4 import BeautifulSoup
import requests

# lightweight munging
import re
import json
import time

# In this case, it was just 1 level up. Other times it might be two.
PROJ_ROOT = os.pardir

# Backoff time for large scrapes
THROTTLE_TIME = .05

# In[19]:

# Download page data
# root_url = "https://www.compactofmayors.org/cities/"
# result = requests.get(root_url)
# print result.status_code
# c = result.content
# soup = BeautifulSoup(c, 'lxml')


# In[20]:

# trows = soup.find_all("a") #  for some reason not all anchor tags are coming back?!
# print("Found {0} entities".format(len(trows)))
# cities = soup.find(class_="city-link")
# print len(cities)


# In[41]:

# Backup plan- go to page source, execute "City_Data", use browsers JSON save macro, and put the data into our raw folder.
# File saved with
# console.save(City_Data['data'], 'mayor_compact_cities.json'). Learned some lessons about using SED for fast regex replacement.
# Link: http://unix.stackexchange.com/questions/169207/remove-backslashes-from-a-text-file?newreg=0e85460cbd4647388c131ae2a2e7bbe7

# Open up the json file.
all_cities_path = os.path.join(PROJ_ROOT, 'data', 'raw', 'compact_mayors_cities.json')
with open(all_cities_path) as data_file:
    city_data = json.load(data_file)


# In[43]:

# Load up the dataframe!
all_cities = pd.DataFrame(city_data['cities'])
all_cities.info()


# In[44]:

all_cities.head()


# In[48]:

all_cities['target_year'].hist(range=[2000, 2100])


# In[45]:

all_cities['reduction'].hist()


# In[99]:

# Save all the website text

site_url = "https://www.compactofmayors.org/cities/mexico-city/"
result = requests.get(site_url)
if result.status_code is 200:
    c = result.content
    soup = BeautifulSoup(c, 'lxml')
else:
    print "Site is down!"


# In[100]:

climate_hold  = soup.find(class_="all_climate_data")
emit_hold     = soup.find(class_="climate_data emissions")
risks_hold = soup.find(id="risks_hazards")


# In[98]:

print risks_hold


# ### Total Annual GHG Emissions:
# Total amount of greenhouse gas generated within a city’s boundary per year and released into the atmosphere, expressed as CO2 equivalent.
#
# ### Targets:
# The amount by which cities have committed to reduce their GHG emissions, expressed either as a percent reduction or an absolute reduction target in tons.
#
# ### Potential Impact of GHG Emissions Target:
# The amount by which GHG emissions will be reduced if a city meets its target for reduction, expressed as total CO2 equivalent.

# In[130]:

# What the metrics mean is listed above
def getClimateData(climate_hold):
    climate_blocks = climate_hold.find_all(class_="cell label has_tooltip")
    climate_lbls = ['Total Annual GHG', 'Target Reduction (% or Tons)', 'Potential Impact']
    climate_data = []
    for block in climate_blocks:
        num = block.find_next(class_="cell")
        climate_data.append(num.text)

    # assume consistently just 3 common column names
    return climate_data
#     return zip(climate_lbls, climate_data)

def getClimateLinks(climate_hold):
    links = []
    linkHolder = climate_hold.find(class_="external_links")
    if linkHolder:
        for link in linkHolder.find_all('a'):
            blob = {}
            blob['name'] = link.text
            blob['url']  = link['href']
            links.append(blob)
    return links


# In[124]:

# all values are percentages
def getEmissionsData(emit_hold):
    emit_blocks = emit_hold.find_all("p", class_="regular")
    len(emit_blocks)
    emit_lbls = []
    emit_data = []
    for block in emit_blocks:
        emit_lbls.append(block.text)
        viz = block.find_next(class_="d3")
        emit_data.append(viz['data-value'])

    # return these arrays zipped up.
#     zip(emit_lbls, emit_data)
    # assume common industry units
    return emit_data


# In[125]:

# analyze risks and hazards
# returns 2 lists
def getHazards_Actions(risks_hold):
    risks_cols = risks_hold.find_all(class_="vc_column_container")

    # Detects action if it lacks "default"
    hazards   = risks_cols[0].find_all("p", attrs={'class': None})
    p_actions = risks_cols[1].find_all("p", attrs={'class': None}) # priority actions

    list_risks   = [x.text.strip() for x in hazards   ]
    list_actions = [x.text.strip() for x in p_actions ]
    return list_risks, list_actions


# In[190]:

def makeSoup(link):
    print("."),
    time.sleep(THROTTLE_TIME)
    site_url = link
    result = requests.get(site_url)
    if result.status_code is 200:
        return BeautifulSoup(result.content, 'lxml').find('body')
    else:
        print "Site is down!"


# In[122]:

all_cities['soup'] = all_cities['link'].map(makeSoup)


# In[142]:

# put everything together
def parseSoup(soup):
    data = {}
    # Block out the page's subsections
    climate_hold  = soup.find(class_="all_climate_data")
    emit_hold     = soup.find(class_="climate_data emissions")
    risks_hold    = soup.find(id="risks_hazards")
    data['Total_GHG'], data['Targets'], data['Impact_of_Target'] = getClimateData(climate_hold)
    data['action_Links'] = getClimateLinks(climate_hold)

    data['emit_Buildings'], data['emit_Transportation'], data['emit_Waste'], data['emit_Industry'], data['emit_Other'] = getEmissionsData(emit_hold)
    data['key_risks'], data['priority_action'] = getHazards_Actions(risks_hold)
    print("."),
    return data
    # Parse locally collocated data items


# In[143]:

# make some soup
all_cities['page_data'] = all_cities['soup'].map(parseSoup)


# In[144]:

all_cities.info()


# In[145]:

pages_df = pd.DataFrame(list(all_cities["page_data"]))
print pages_df.columns
pages_df.head()


# In[146]:

pages_df.info()


# In[160]:

allCols = all_cities.columns
origCols = allCols[:-2] # ignore redundant object and soup


# In[161]:

full = pages_df.join(all_cities[origCols])


# In[162]:

full.head


# In[187]:

export_path = os.path.join(PROJ_ROOT, 'data', 'raw', 'compact_mayors_scrape.xls')
soup_path = os.path.join(PROJ_ROOT, 'data', 'raw', 'soups', 'compact_mayors_soup.json')


# In[186]:

full.to_excel(export_path)


# In[191]:

# keep a copy of the full data stored in the soup folder
all_cities.to_json(soup_path)


# In[166]:

# Do a quick missing values audit
import missingno as msno


# In[179]:

# do some type casting
floatCols = ["emit_Buildings", "emit_Industry", "emit_Other", "emit_Transportation", "emit_Waste"]
intCols   = [ 'reduction', 'population']


# In[180]:

# full[floatCols] = full[floatCols].strip()
# full[floatCols] = full[floatCols].astype(float)
full[intCols] = full[intCols].astype(int)


# In[181]:

msno.matrix(full)


# In[170]:

type(full['emit_Buildings'][0])


# In[182]:

# TODO
# strip commas from population
# cast datatypes correctly (nums to strings)
# productionize the data cleaning
# pipeline the other stuff too
# normalize phase, risks, hazards, etc later
