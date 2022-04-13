# d&b hoovers scraper
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os, sys, traceback

p = os.path.dirname(os.path.abspath(__file__))

# load country dictionary
country_dict = pd.read_csv(p + '/../bloomberg/country_dict.csv')

# Error func decorator
def error(default_value):
    """
        adds the following properties to a function:
            - If None is passed, return default value
            - Try / except all exceptions, but print exception.
    """
    def default_decorator(func):
        def func_wrapper(*args, **kwargs):
            i = args[0]
            if i is None or (type(i) == str and i == ''):
                return default_value
            else:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
#                     print(func)
#                     print(args, kwargs)
#                     traceback.print_exc()
                    return default_value
        return func_wrapper
    return default_decorator

@error(None)
def search(name):
    """ returns a bs4 page with search results.
    """
    url = 'http://www.hoovers.com/company-information/company-search.html?term='
    url += name
    r = requests.get(url)
    r = BeautifulSoup(r.content, 'lxml')
    return r

@error(None)
def get_table(page):
    data = []
    table = page.find('div', {'class': 'data-table'}).find('tbody')
    rows = table.find_all('tr')
    if rows is not None:
        for r in rows:
            cells = r.find_all('td')

            temp = {}
            temp['name'] = cells[0].text
            temp['revenue_source'] = cells[0].find('a')['href']
            temp['location'] = cells[1].text
            temp['revenue'] = cells[2].text
            data.append(temp)
    return pd.DataFrame(data)

@error(None)
def standardize_country(x, iso=True):
    return country_dict[x]['iso_code']

@error(None)
def clean_sales(x):
    return float(x.replace('$','').replace('M','')) * 1000000

@error(None)
def clean_table(table):
    table['source_url'] = table['revenue_source'].apply(lambda x: 'http://www.hoovers.com' + x)
    table['revenue'] = table['revenue'].apply(clean_sales)
    table['revenue_units'] = 'USD'
    table['country'] = table['location'].apply(lambda x: x.split(', ')[-1])
    table['iso'] = table['country'].apply(standardize_country)
    return table

@error(None)
def get_data(name, country, entity_type):
    page = search(name)
    table = get_table(page)
    table = clean_table(table)

    country_match = table[table['iso'] == country]
    country_match = country_match.to_dict(orient='records')

    if len(country_match) > 0:
        return country_match[0]
    else:
        return table.to_dict(orient='records')[0]
