
# coding: utf-8

# # API Calls

# In[1]:
import os, sys
import requests, time, re, json, string
from bs4 import BeautifulSoup
import csv
from multiprocessing.pool import ThreadPool
from requests.packages.urllib3.exceptions import *
from socket import gaierror
from googletrans import Translator
translator = Translator()
import pandas as pd


top_path =os.path.dirname(__file__)
print(top_path)

"""
The stem url for api calls. manipulating this variable
could allow for calls referencing pages written in languages other than english.
"""
API_URL = 'http://en.wikipedia.org/w/api.php'
language_dict = {"ESP": "es",
                 "URK": "uk",
                 "HUN": "hu",
                 "ITA": "it"}

with open(os.path.join(top_path,'reg_dict.csv'), 'r', encoding='utf-8') as x:
    reg_dict = {}
    reader = csv.reader(x)
    skip = next(reader)
    for row in reader:
        reg_dict[row[1]] = row[2]

print('load dictionary')
def get_page(title):
    if title is not None:
        # retry page processing as sometimes network errors
        # can occur. Most of the time an exception will not be thrown.
        try:
            page = requests.get('https://'+language+'.wikipedia.org/wiki/' + title)
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            try:
                page = requests.get('https://'+language+'.wikipedia.org/wiki/' + title)
            except requests.exceptions.RequestException as e:
                return None
        return BeautifulSoup(page.content, 'lxml')
    
def get_pages(titles, num_workers=20):
    """
    Use a thread pool to download multiple pages for faster batch processing.
    Can't use the standard wikimedia api multi-title feature as it increases
    the likelihood useful data won't be returned.
    """
    if type(titles) == list and len(titles) > 0:
        if len(titles) < num_workers: num_workers = len(titles)
        pool = ThreadPool(num_workers)
        pages = pool.map(get_page, titles)
        pool.close()
        pool.join()
        return [i for i in pages if i]
    
def get_url(url):
    if url is not None:
        try:
            page = requests.get(url)
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            try:
                page = requests.get(url)
            except requests.exceptions.RequestException as e:
                return None
        return BeautifulSoup(page.content, 'lxml')
    
def get_urls(urls, num_workers=20):
    """
    Use a thread pool to download multiple urls for faster batch processing.
    """
    if type(urls) == list and len(urls) > 0:
        if len(urls) < num_workers: num_workers = len(urls)
        pool = ThreadPool(num_workers)
        pages = pool.map(get_url, urls)
        pool.close()
        pool.join()
        return [i for i in pages if i]
    
def search(name,language = 'en'):
    """
    queries the wikimedia API to return {limit} matches to the search term
    """
    titles = _search_query(name,language)
    return titles
    
def _search_query(name,lan = 'en'):
    """
    the underlying api query that powers the search function.
    """



    url = 'https://' + lan + '.wikipedia.org/w/index.php'
    API_URL = 'https://' + lan + '.wikipedia.org/w/api.php'
    
    params = {
        'sort': 'relevance',
        'search': name,
        'profile': 'advanced',
        'fulltext': 1
    }

    r = requests.get(url, params=params)
    if r.status_code == 200:
        page = BeautifulSoup(r.content, 'lxml')
        titles = page.find_all('div', {'class': 'mw-search-result-heading'})
        titles = [t.find('a')['title'] for t in titles]
        return titles
    else:
        time.sleep(0.5)
        r = requests.get(API_URL, params=params)
        return titles


# # Get Country Data
# iso, wiki title mapping

# In[2]:


iso_page = requests.get('https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3').content
iso_page = BeautifulSoup(iso_page, 'lxml')
iso_page = iso_page.find('div', {'class': 'plainlist'})

iso_title = {}
title_iso = {}

for i in iso_page.find_all('li'):
    tmp = {}
    iso = i.find('span').text
    title = i.find('a')['title']
    iso_title[iso] = title
    title_iso[title] = iso
    
# # Process Infobox

# In[3]:

def clean(x):
    x = x.strip()
    x = x.replace('\xa0', ' ')
    x = re.sub(r'\[.*\]', '', x)
    x = re.sub(r'\(.*\)', '', x)
    x = re.sub('\.[^\s\d]+?(\s|$)', '', x)
    x = x.replace('- ', '').replace('•', '').replace(' \n', ', ').replace('\n', ', ').strip()
    x = re.sub('\s+', ' ', x)
    return x

# In[4]:

def fix_newlines(infobox):
    # add some newlines to make lists look nicer.
    for br in infobox.find_all("br"):
        br.replace_with("\n")
    for img in infobox.find_all("img"):
        img.replace_with("")
    for img in infobox.find_all('a', {'class': 'image'}):
        img.replace_with("")
    for li in infobox.find_all("li"):
        li.replace_with(li.text + '\n')
        
def get_top_region(infobox, data):
    # Australian cities store region at the top.
    if infobox.find('span', {'class': 'region'}):
        data['region_aus'] = [infobox.find('span', {'class': 'region'}).text]
        data['region_aus_links'] = [infobox.find('span', {'class': 'region'}).find('a')]
        data['region_aus_links'] = [a['href'] for a in data['region_aus_links'] if a and a.has_attr('href')]
    return data

def get_cats(infobox, data):
    cat = infobox.find('div', {'class': 'category'})
    if cat:
        cat = cat.text
        data['category_label'] = cat
    return data

def get_infobox(page):
    
    data = {}
    
    infobox = page.find('table', {'class': 'infobox'})
    if not infobox:
        return {}
    
    fix_newlines(infobox)
    data = get_top_region(infobox, data)
    data = get_cats(infobox, data)

    section = ''
    section_year = None
    sect_change = False
    
    # iterate through each table row.
    for i in infobox.find_all('tr'):
        key = i.find('th')
        value = i.find('td')
        if key:
            
            # mergedtoprow defines sections. This is useful to keep track of years
            # that scope over the entire section, and labels.
            if not i.has_attr('class') or (i.has_attr('class') and (i['class'][0] == 'mergedtoprow')):
                sect_change = True
                section = ''
                section_year = None
                
                # these are the only things that reliably have sections that we're interested in.
                if any(i in key.text.lower() for i in ['gdp', 'population', 'area', 
                                                       'government', 'resident', 'time']):
                    
                    # 'largest' avoid issues with New York City, which has a section
                    # starting with 'largest_borough_by_area'
                    if 'largest' not in key.text.lower():
                        section = key.text.lower()
                        
                        # years are usually in parentheses (2019)
                        section_year = re.search('\((.*\s+)?(\d\d\d\d)(\s+.*)?\)', section)
                        if section_year: section_year = section_year.group(2)
                        else:
                            section_year = re.search('\((.*)(-+|\/+)?(\d\d\d\d)(\s+.*)?\)', section)
                            if section_year:
                                section_year = section_year.group(3)
                            else:
                                section_year = re.search('\((.*\s+)?(\d\d\d\d)(-+|\/+)?(.*)?\)', section)
                                if section_year: section_year = section_year.group(2)
                                    
            if value and value.text.replace(' ', '').replace('\xa0', '') != '':
                                
                # get links in values
                value_links = value.find_all('a')
                if len(value_links) >= 1: 
                    value_links = [v for v in value_links if v.has_attr('href')]
                    value_links = [v['href'] for v in value_links]
                    # remove citations:
                    value_links = [v for v in value_links if not v.startswith('#')]
                else:
                    value_links = None

                key, value = key.text.lower(), value.text
                
                # we don't care about rank, and it messes
                # up actors like NY state
                if sect_change and 'rank' in value.lower():
                    continue
                    
                # Fixes Hangzhou GDP
                sc = re.search('((20|19|18)\d\d)', value)
                if sect_change and sc:
                    section_year = sc.group(1)
                    continue
                
                # get any year values in the key or value text.
                # these will be associated with this key.
                key_year = re.search('\((.*\s+)?(\d\d\d\d)(\s+.*)?\)', key)
                wh = 'key'
                if not key_year:
                    key_year = re.search('\((.*\s+)?(\d\d\d\d)(\s+.*)?\)', value)
                    wh = 'value'
                if key_year:
                    key_year = key_year.group(2)

                # if we have both a key year and a section year,
                # use the key year.
                if key_year:
                    year = key_year
                else:
                    year = section_year

                # clean up the text.
                section = clean(section)
                key = clean(key)
                # selecting km2 instead of sq mi
                if section == 'area' or section == 'surface' and "(" in value:
                    temp = value.split("(")
                    for val in range(len(temp)):
                        if "km2" in temp[val] or "km²" in temp[val]:
                            if type(value) == str:
                                value = [v for v in temp[val].strip(")").split('\n')]
                    # if area_units is something else
                    if 'km2' not in value[0] and "km²" not in value[0]:
                        value = [temp[0]]
                else:
                    value = [v for v in value.split('\n')]
                value = [clean(v) for v in value]
                # if multiple area types in value
                if "or" in value[0]:
                    temp = value[0].split("or")
                    for v in range(len(temp)):
                        if "km2" in temp[v] or "km²" in temp[v]:
                            value = [temp[v].strip(" ")]

                # add section to key, replace spaces.
                if section and section != key:
                    key = section + ' ' + key
                key = key.replace(' ', '_')
                key = key.replace('\xa0', '_')

                # add all this info to data dict.
                data[key] = value
                if year:
                    data[key + '_year'] = year
                if value_links:
                    data[key + '_links'] = value_links
            sect_change = False

    if 'area' in data:
        if "ha" in data['area'][0]:
            try:
                area = data['area'][0].split(" ")[0].replace(',','')
                area = float(area) / 100
                data['area'][0] = str(area) + " km2"
            except Exception as e:
                raise Exception(str(e) + 'area, line 293')
        if "sq mi" in data['area'][0]:
            try:
                area = data['area'][0].split(" ")[0].replace(',', '')
                area = float(area) * 2.58999
                data['area'][0] = str(area) + " km2"
            except Exception as e:
                raise Exception(str(e) + 'area, line 299')

    if language == 'en':
        t_data = data
    else:
        tmp = list(data.keys())
        translations = translator.translate(tmp)

        t_data = {}

        for t in translations:
            temp = []
            for y in data[t.origin]:
                try:
                    z = translator.translate(y, src=language)
                except:
                    z = translator.translate(y)
                if z.text: temp.append(z.text)
            t.text = t.text.replace('com._autónoma', 'autonomous_community')
            t_data[t.text] = temp

    return t_data

# In[5]:


# get_infobox(get_page('Hartlepool'))


# In[6]:

def infer_type(categories):
    city_score = 0
    region_score = 0
    country_score = 0
    company_score = 0
    university_score = 0
    
    cats = [c.lower() for c in categories]
    
    if any(i in cats for i in ['communities of belgium']):
        return 'Region'
    
    cats = ' '.join(cats).split(' ')
    if any(i in cats for i in ['births', 'temples']):
        return None
    
    for w in cats:
        
        if w in ['list', 'lists']: return None
                
        if w in ['city', 'cities', 'municipality', 'municipalities', 'town', 'towns', 'capital', 'capitals',
                 'populated', 'partidos', 'geography', 'places', 'comarcas', 'villages', 'communes', 'wards',
                 'ward']:
            if w in ['villages', 'cities', 'towns']:
                city_score += 2
            else:
                city_score += 1
            
        if w in ['arrondissements', 'arrondissement', 'province', 'provinces', 'canton', 'entity',
                 'region', 'regions', 'nuts', 'county', 'counties', 'states', 'districts',
                 'state', 'territory', 'territories', 'emirate', 'geography', 'voivodeship', 'gmina',
                 'canterbury,', 'island']:
            region_score += 1
            
        if w in ['country', 'countries', 'states', 'state', 'nations']:
            country_score += 1
            
        if w in ['companies']:
            company_score += 1
            
        if w in ['universities']:
            university_score += 1
        
        if w in ['disambiguation']:
            return 'Disambiguation'
                
    max_score = max((city_score, region_score, country_score, company_score, university_score))
    if max_score == 0: return None
    if city_score == max_score: return ('City', max_score)
    if company_score == max_score: return ('Company', max_score)
    if region_score == max_score: return ('Region', max_score)
    if country_score == max_score: return ('Country', max_score)
    if university_score == max_score: return ('University', max_score)
    

# In[7]:


def clean_numbers(x):
    x = x.replace(',', '')
    units = None
    if '€' in x:
        units = 'EUR'
        x = x.replace('€', '')
    if '¥' in x:
        units = 'RMB'
        x = x.replace('¥', '')
    if 'CNY' in x:
        units = 'RMB'
        x = x.replace('CNY', '')
    if 'US$' in x:
        units = 'USD'
        x = x.replace('US$', '')
    if '$' in x:
        units = 'USD'
        x = x.replace('$', '')
    if '/km2' in x:
        units = '/km2'
        x = x.replace('/km2', '')
    if 'km2' in x or 'km²' in x:
        units = 'km2'
        x = x.replace('km2', '').replace('km²', '')
    if 'acres' in x:
        units = 'acres'
        x = x.replace('acres', '')
    if 'ha' in x:
        units = 'ha'
        x = x.replace('ha', '')
    if 'km' in x:
        units = 'km'
        x = x.replace('km', '')
    if '/sq mi' in x:
        units = '/sq mi'
        x = x.replace('/sq mi', '')
    if '/sqmi' in x:
        units = '/sq mi'
        x = x.replace('/sqmi', '')
    if 'sq mi' in x:
        units = 'sq mi'
        x = x.replace('sq mi', '')
    if 'sqmi' in x:
        units = 'sqmi'
        x = x.replace('sq mi', '')
    if 'miles' in x:
        units = 'mi'
        x = x.replace('miles', '')
    if 'mi' in x:
        units = 'mi'
        x = x.replace('mi', '')
    if 'm' in x:
        units = 'm'
        x = x.replace('m', '')
    if 'ft' in x:
        units = 'ft'
        x = x.replace('ft', '')
    
    factor = 1
    if 'thousand' in x: factor = 1000
    if 'million' in x: factor  = 1000000
    if 'billion' in x: factor  = 1000000000
    if 'trillion' in x: factor = 1000000000000
    x = x.replace('thousand', '').replace('million', '').replace('billion', '').replace('trillion', '')
            
    x = [c for c in x if c in '1234567890.']
    x = ''.join(x)
    x = x.strip('.')
    if x == '': return None, None
    try:
        result = float(x) * factor
    except Exception as e:
        raise Exception(str(e) + 'line 440')
    return result, units



#### In[8]:


from collections import Counter

def process_page(page):

    data = {}
    
    data['title']   = page.find('h1', {'class': 'firstHeading'}).text
    if data['title'].startswith('File:'): return None
    
    # get coords in decimal degrees
    latlon = page.find('span', {'class': 'geo'})
    if latlon and "," not in str(latlon.text):
        try:
            data['lat'] = float(latlon.text.split("; ")[0])
            data['lng'] = float(latlon.text.split("; ")[1])
        except Exception as e:
            raise Exception(str(e) +'lat long line 464')


    # attempt to get a wiki_iso. 
    data['wiki_iso'] = None
    infobox = page.find('table', {'class': 'infobox'})
    if infobox:
        for i in infobox.find_all('a'):
            if i.has_attr('title'):
                title = i['title']

                # translator
                if language != 'en':
                    title = translator.translate(title, src=language).text
                if title in title_iso:
                    data['wiki_iso'] = title_iso[title]
                    break

    if not data['wiki_iso']:
        ps = [p for p in page.find_all('p') if not p.has_attr('class')]
        if len(ps) >= 1:
            for i in ps[0].find_all('a'):
                if i.has_attr('title'):
                    title = i['title']
                    # translator
                    if language != 'en':
                        title = translator.translate(title, src=language).text

                    if title in title_iso:
                        data['wiki_iso'] = title_iso[title]
                        break

    data['infobox'] = get_infobox(page)

    if not data['wiki_iso']:
        if 'country' in data['infobox']:
            country= data['infobox']['country'][0]
               # translator
            if language != 'en':
                country  = translator.translate(country, src=language).text
            if country in title_iso:
                data['wiki_iso'] = title_iso[country]

    # These 3 introduce a lot of noise. Indiana -> India, for example. 
    # necessary for some actors though. :(

    if not data['wiki_iso']:
        ps = [p for p in page.find_all('p') if not p.has_attr('class')]
        if len(ps) >= 1:
            for k, v in title_iso.items():
                if k in ps[0].text:
                    data['wiki_iso'] = v
                    break

    if not data['wiki_iso']:
        if infobox:
            infobox_TEXT = infobox.text
           # translator
            if language != 'en':
                infobox_TEXT  = translator.translate(infobox_TEXT, src=language).text

            for k, v in title_iso.items():
                if k in infobox_TEXT:
                    data['wiki_iso'] = v
                    break
    
    if not data['wiki_iso']:
        data_title = data['title']
        # translator
        if language != 'en' and data_title:
            data_title = translator.translate(data_title, src=language).text
        for k, v in title_iso.items():


            if k in data_title:
                data['wiki_iso'] = v
                break
    
    data['categories'] = []
    cat = page.find('div', {'id': 'mw-normal-catlinks'})
    if cat:
        data['categories'] = [i.text for i in cat.find_all('li')]
    if 'category_label' in data['infobox']:
        data['categories'].append(data['infobox']['category_label'])  
    data['wiki_type'] = infer_type(data['categories'])
    if type(data['wiki_type']) == tuple : data['wiki_type'] = data['wiki_type'][0]
    
    for k,v in data['infobox'].items():
        if 'area' in k and 'links' not in k and 'year' not in k and 'code' not in k and 'coordinates' not in k and k != 'areas' and 'rank' not in k:
            data['area'] = data['infobox'][k]
            data['area'], data['area_units'] = clean_numbers(data['area'][0])
            if k+'_year' in data['infobox']:
                data['area_year'] = data['infobox'][k+'_year']
            break      
    for k,v in data['infobox'].items():
        if 'population' in k and 'links' not in k and 'year' not in k and 'municipality' not in k:
            data['population'] = data['infobox'][k]
            data['population'], _ = clean_numbers(data['population'][0])
            if k+'_year' in data['infobox']:
                data['population_year'] = data['infobox'][k+'_year']
            break

    for k,v in data['infobox'].items():
        if 'gdp' in k and 'links' not in k and 'year' not in k:
            data['gdp'] = data['infobox'][k]
            if 'USD' in data['gdp'][0] and 'CNY' in data['gdp'][0]:
                data['gdp'] = ["USD " + data['gdp'][0].split("USD")[1]]
            data['gdp'], data['gdp_units'] = clean_numbers(data['gdp'][0])
            if k+'_year' in data['infobox']:
                data['gdp_year'] = data['infobox'][k+'_year']
            break
                
    for k,v in data['infobox'].items():
        if 'elevation' in k and 'links' not in k and 'year' not in k:
            data['elevation'] = data['infobox'][k][0]
            break
        
    return data

# In[9]:


def get_region_hierarchy(data):
    
    # generate a list of region triples. 
    # (key, page['title'], page['area'], page['population'])
    
    region_words = ['region', 'state', 'province', 'county', 'emirate', 'gmina', 'island',
                    'district', 'raion', 'prefecture', 'territory', 'canton',
                    'governorate', 'administrative_region', 'mkhare', 'metropolitan_city',
                    'oblast', 'autonomous_region', 'commune', 'entity', 'sovereign_state',
                    'municipality', 'provinces', 'marz', 'republic', 'cercle',
                    'autonomous_community', 'provincekind', 'governorates', 
                    'locale', 'subdivision', 'voblast', 'voivodeship', 'parish',
                    'constituent_country', 'ceremonial_county', 'arrondissement', 'admin', 'country']
    
    tmp = []
    for k,v in data['infobox'].items():
        if '_links' in k or '_year' in k or 'postcode' in k or 'area_' in k or 'population_' in k or 'gdp_' in k \
            or 'congressional_' in k or 'government_' in k or 'highest_' in k or '_electorate' in k or 'nuts_' in k \
            or 'historical_' in k or '_bird' in k or '_fish' in k or '_flower' in k or '_stone' in k or 'animal' in k \
            or '_languages' in k or 'historic_' in k: continue
        if k.startswith("sub") and k.endswith('s'): continue
        if any(w in k for w in region_words):
            for i in v:
                if any(char.isdigit() for char in i) or i.lower().startswith("list") or "," in i: break
                if i != '':
                    tmp += [[k, i]]
                    
    if len(tmp) > 0 and ('country' in tmp[-1][0] or 'sovereign_state' in tmp[-1][0]):
        return tmp[::-1]
    
    return tmp


# In[10]:


def handle_disambig(name, iso, entity_type, disambig, debug=False):
    page = get_page(disambig['title'])
    page = page.find('div', {'class': 'mw-parser-output'})
    if debug: print('Disambiguating')
    if page:
        for i in page.find_all('li'):
            a = i.find('a')
            if a and a.has_attr('title'):
                data = process_page(get_page(a['title']))
                if debug: print(data['title'], data['wiki_type'], data['wiki_iso'])
                if data['wiki_type'] == entity_type and data['wiki_iso'] == iso:
                    data['region_hierarchy'] = get_region_hierarchy(data)
                    if data['infobox'] == {} or data['infobox'] == None:
                        if debug: print('no infobox')

                    del data['infobox']
                    data['categories'] = '; '.join(data['categories'])
                    return data
    return {}


# In[11]:


def get_data(name, iso, entity_type, check_country=True, debug=False, check_disambig=True,EN = True):
    global language
    if EN:
        language = 'en'
    else:
        language = language_dict[iso]



    name = name.replace('!', '')
    name = name.replace('Aggregazione ', '')
    if "," in name: titles = search(name,language)
    else: titles = search(name + ", " + iso_title[iso],language)
    if not check_country and debug: print(titles)
    pages = get_pages(titles)
    if not pages:
        if debug: print('pages null')
        return {}
    pages = [process_page(page) for page in pages]
    
    
    if debug:
        for p in pages: print(p)

    if len(pages) != 0:
        disambig = [i for i in pages if i['wiki_type'] == 'Disambiguation']
        if len(disambig) > 0: disambig = disambig[0]
        else: disambig = None
        
        # filter iso
        if iso:
            iso_pages = [i for i in pages if 'wiki_iso' in i]
            iso_pages = [i for i in iso_pages if i['wiki_iso'] == iso]
            
            if len(iso_pages) == 0:
                name = name.lower().replace('dimos', 'municipality')
                if disambig and check_disambig:
                    d = handle_disambig(name, iso, entity_type, disambig, debug=debug)
                    if d and d != {}: return d
                if check_country and iso in iso_title:
                    if debug: print('\nchecking country')
                    name = name.replace('d\'', '')
                    return get_data(name + ", " + iso_title[iso], iso, entity_type, check_country=False, debug=debug,EN=EN)
        else: iso_pages = pages
        
        # filter entity_type
        et_pages = [i for i in iso_pages if i['wiki_type'] == entity_type]
     
        if len(et_pages) == 0:
            name = name.lower().replace('dimos', 'municipality')
            if disambig and check_disambig:
                d = handle_disambig(name, iso, entity_type, disambig, debug=debug)
                if d and d != {}: return d
            if check_country and iso in iso_title:
                if debug: print('\nchecking country')
                name = name.replace('d\'', '')
                return get_data(name + ", " + iso_title[iso], iso, entity_type, check_country=False, debug=debug,EN=EN)
        else:
            max_score = 0
            rank = 0
            for page_num in range(len(et_pages)):
                score = infer_type(et_pages[0]['categories'])[1]
                if score > max_score:
                    max_score = score
                    rank = page_num
            data = et_pages[rank]
            data['region_hierarchy'] = get_region_hierarchy(data)
        
            if data['infobox'] == {} or data['infobox'] == None:
                if debug: print('no infobox')

            del data['infobox']
            data['categories'] = '; '.join(data['categories'])
            
            return data
    return {}


def post_process_admin_level(data):
    # create new cols
    new_col_list = []
    for index, row in data.iterrows():
        new_dic = {"admin_1": None,
                   "admin_1_type": None,
                   "state": None,
                   "state_type": None}
        if not isinstance(row['region_hierarchy'], float):

            iso = row['iso']
            if len(eval(row['region_hierarchy'])) > 0:
                admin_1 = eval(row['region_hierarchy'])[-1]
                new_dic["admin_1"] = admin_1[1]
                new_dic["admin_1_type"] = admin_1[0]

                for reg in eval(row['region_hierarchy']):

                    if iso in reg_dict:
                        if reg[0] in reg_dict[iso].lower():
                            new_dic["state"] = reg[1]
                            new_dic["state_type"] = reg[0]

                    else:
                        new_dic["state"] = admin_1[1]
                        new_dic["state_type"] = admin_1[0]

        new_col_list.append(new_dic)
    new_cols_df = pd.DataFrame(new_col_list)

    merged_data = data.merge(new_cols_df, left_index=True, right_index=True)

    return merged_data

if __name__ == "__main__":

    # a Test case
    data = get_data('Parco Sorgenti Del Torrente Lura', "ITA", "City",EN = False)
    print(data)




