import requests, json, re, os, sys, traceback
from bs4 import BeautifulSoup
import pandas as pd
from multiprocessing.pool import ThreadPool
from scraper.src.contextuals.bloomberg import currency

p = os.path.dirname(os.path.abspath(__file__))

# load country dictionary
country_dict = pd.read_csv(p + '/country_dict.csv')
def standardize_country(name, iso=True):
    try:
        row = country_dict[country_dict['wrong'] == name].to_dict(orient='records')[0]
        if iso:
            return row['iso_code']
        else:
            return row['country_name']
    except:
        return name

# load market code dictionary
market_codes = pd.read_csv(p + '/market_codes.csv')
market_codes = market_codes.set_index('Unnamed: 0')
market_codes = market_codes.to_dict()['iso']
def get_country_from_market(market_code):
    """
    returns the iso country code when given a bloomberg market code.
    """
    if market_code in market_codes:
        return market_codes[market_code]
    else:
        return None

def get_yahoo_finance_ticker(name):
    """
    Searches Yahoo Finance for a company name and returns a matching ticker.
    Yahoo finance tends to handle subsidiary companies better than Google does.
    """
    url = 'https://finance.yahoo.com/_finance_doubledown/api/resource/searchassist;searchTerm={}?lang=en-US&site=financever=0.102.544'.format(name)
    page = json.loads(requests.get(url).content)
    if len(page['items']) > 0:
        r = {}
        r['ticker_symbol'] = page['items'][0]['symbol']
        r['name'] = page['items'][0]['name']
        r['public'] = 1
        return r
    else:
        return None

# Another potentially useful method that does not play a role currently
# def get_bloomberg_autocomplete(name):
#     # url = 'https://www.google.com/finance?q={}&ei=LLKbWevFFcyougT5sLcg'.format(name)
#     url = 'https://search.bloomberg.com/autocomplete.json?query={}' + name
#     page = requests.get(url).content
#     return page

def get_bloomberg_entity(name, country, number=1):
    """
    returns {number} possible bloomberg entries matching a name and country
    """
    country_code = standardize_country(country)
    url = 'https://search.bloomberg.com/lookup.json?types=Company_Private,Company_Public&group_size=10,10&fields=name,ticker_symbol&query=' + name
    page = json.loads(requests.get(url).content)

    # adds public and private data to the appropriate parts of the JSON returned
    # by bloomberg. Nothing is done with these lists as update() returns None
    # and edits the object passed to it, so all necessary information will be in page.
    [r.update({'public': 0}) for r in page[0]['results']]
    [r.update({'public': 1}) for r in page[1]['results']]

    # put public and private companies together in results now that they have
    # been tagged.
    results = page[0]['results'] + page[1]['results']

    # if a country is provided filter results so only those
    # matching the country remain.
    if country_code:
        temp = []
        for r in results:
            if get_country_from_market(r['ticker_symbol'].split(':')[1]) == country_code:
                temp.append(r)
        if len(temp) > 0:
            results = list(temp)

    # sort by the score bloomberg provides.
    results.sort(key=lambda x: x['score'], reverse=True)

    # return {number} results.
    if len(results) > 0:
        return results[0:number]
    else:
        return None

def get_ticker(name, country, entity_type, debug=False):
    """
    searches all potential data sources for the correct ticker.
    """

    yahoo_ticker = get_yahoo_finance_ticker(name)
    bloomberg_tickers = get_bloomberg_entity(name, country, number=2)

    if debug:
        print(yahoo_ticker)
        print(bloomberg_tickers)

    # resolve ticker from results above.
    # Yahoo finance has a better search function for subsidiary companies
    if yahoo_ticker is not None and yahoo_ticker['ticker_symbol'] not in [i['ticker_symbol'] for i in bloomberg_tickers]:
        return get_bloomberg_entity(yahoo_ticker['name'], country, number=2)

    return bloomberg_tickers

###########################
### Public Company Data ###
###########################

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
                    # print(func)
                    # print(args, kwargs)
                    # traceback.print_exc()
                    return default_value
        return func_wrapper
    return default_decorator

def scale_by_factor(num, factor):
    if factor == 'T' or factor == 'Trillions':
        return num * 1000000000000
    if factor == 'B' or factor == 'Billions':
        return num * 1000000000
    if factor == 'M' or factor == 'Millions':
        return num * 1000000
    else:
        print(factor)
        return 5 / 0


def convert_to_usd(src_currency, amt):
    if src_currency == 'USD':
        return ('USD', amt)
    out, success = currency.convert(src_currency, 'USD', amt)
    if success:
        return ('USD', amt)
    else:
        return (src_currency, amt)

@error(None)
def get_currency(page):
    c = page.find('span', {'class': 'currency__defc7184'})
    c = c.text.strip()
    return c

@error((None, None))
def get_market_cap(page):
    src_currency = get_currency(page)
    page = page.find('section', {'class': 'market-cap__a8440c6b'})
    mc = page.find('div', {'class': 'value__b93f12ea'})
    mc = mc.text.strip()
    factor = mc[-1]
    mc = float(mc[:-1])
    mc = scale_by_factor(mc, factor)
    return convert_to_usd(src_currency, mc)

@error(None)
def get_one_year_return(page):
    for i in page.find_all('div', {'class': 'rowListItemWrap__4121c877'}):
        if i.find('span', {'class': 'fieldLabel__9f45bef7'}).text == '1Y Rtn.':
            oyr = i.find('span', {'class': 'fieldValue__2d582aa7'})
            oyr = oyr.text.strip()
            oyr = oyr.replace('%', '')

            if oyr != '--':
                return float(oyr)

@error(None)
def get_description(page):
    desc = page.find('section', {'class': 'description__bff5f1e8'})
    desc = desc.text.strip()
    return desc

@error(None)
def get_website(page):
    web = page.find('section', {'class': 'website__a0690a57'})
    web = web.find('a')
    web = web.text.strip()
    return web

@error(None)
def get_address(page):
    addr = page.find('section', {'class': 'address__5f5e7ed3'})
    addr = addr.find('div', {'class': 'value__b93f12ea'})
    addr = addr.text.strip()
    return addr

@error(None)
def get_sector(page):
    sec = page.find('a', {'class': 'sector__1549170a'})
    sec = sec.text.strip()
    return sec

@error(None)
def get_industry(page):
    ind = page.find('a', {'class': 'industry__6b8e09a1'})
    ind = ind.text.strip()
    return ind

@error((None, None))
def get_table_value(tag, src_currency, factor):
    val = tag.find('div', {'class': 'value__01a1ae38'})
    val = val.text.strip()

    if '%' in val:
        val = val.replace('%', '')
        val = float(val)
        return ('%', val)

    if ',' in val:
        val = val.replace(',', '')
        val = float(val)

    val = float(val)
    val = scale_by_factor(val, factor)
    return convert_to_usd(src_currency, val)

def get_table_values(page):
    data = {}

    tables = page.find_all('section', {'class': 'container__05b58806'})
    for table in tables:
        factor = table.find('div', {'class': 'header__3ce42ab3'})
        factor = factor.text.split('(')[1].split(' ')[0]

        src_currency = table.find('div', {'class': 'header__3ce42ab3'})
        src_currency = src_currency.text.split('(')[1].split(' ')[1].replace(')', '')

        for row in table.find_all('li', {'class': 'row__140fcf6e'}):
            key = row.find('div', {'class': 'title__4342a471'}).text.lower().replace(' ', '_')
            data[key + '_units'], data[key] = get_table_value(row, src_currency, factor)

    return data

def get_public_company_data(ticker, debug=False):
    """
    Get contextual information for a publicly listed company.
    """

    if debug: print('\n', ticker)

    # Download page.
    url = 'https://www.bloomberg.com/quote/' + ticker
    page = BeautifulSoup(requests.get(url).content, 'lxml')

    # Extract data.
    temp = {}
    temp['source_url'] = url
    temp['headquarters'] = get_address(page)
    temp['description'] = get_description(page)
    temp['website'] = get_website(page)
    temp['GICS_Sector_Name'] = get_sector(page)
    temp['GICS_Industry_Group_Name'] = get_industry(page)
    temp['market_cap_units'], temp['market_cap'] = get_market_cap(page)
    temp['percent_year_return'] = get_one_year_return(page)
    temp.update(get_table_values(page))

    return temp

def get_data(name, country, entity_type, debug=False):
    """
    Wraps ticker resolution and information gathering.
    Also gathers private company information.
    """

    if debug: print('Finding Ticker: ')
    data = get_ticker(name, country, entity_type, debug=debug)

    if data is None:
        return None

    out = {}

    # company is private
    if data[0]['public'] == 0:

        if debug: print('Company is private')

        out['ticker'] = data[0]['ticker_symbol']
        out['public'] = data[0]['public']
        out['bloomberg_name'] = data[0]['name']

        url = 'https://www.bloomberg.com/profiles/companies/' + out['ticker']
        page = BeautifulSoup(requests.get(url).content, 'lxml')
        out['GICS_Sector_Name'] = page.find('div', {'class': 'sector'}).text.replace('Sector: ', '')
        out['GICS_Industry_Group_Name'] = page.find('div', {'class': 'industry'}).text.replace('Industry: ', '')
        out['GICS_Sub_Industry_Name'] = page.find('div', {'class': 'sub_industry'}).text.replace('Sub-Industry: ', '')
        out['description'] = page.find('div', {'class': 'description'}).text
        out['headquarters'] = page.find('div', {'class': 'address'}).text.strip().replace('\n', ', ')
        try:
            out['website'] = page.find('div', {'class': 'website'}).find('a', href=True)['href']
        except: pass
        out['source_url'] = url

    # company is public.
    # return the potential listing with the most data.
    else:
        if len(data) == 1 or data[0]['name'] != data[1]['name']:
            out['ticker'] = data[0]['ticker_symbol']
            out['public'] = data[0]['public']
            out['bloomberg_name'] = data[0]['name']
            d = get_public_company_data(data[0]['ticker_symbol'], debug=debug)
            out.update(d)
        else:
            pool = ThreadPool(2)
            results = pool.map(get_public_company_data, [data[0]['ticker_symbol'], data[1]['ticker_symbol']])
            pool.close()
            pool.join()

            d0 = results[0]
            d1 = results[1]

            if debug:
                print(d0)
                print(d1)

            d0_count = sum([0 if (d is None) else 1 for d in d0.values()])
            d1_count = sum([0 if (d is None) else 1 for d in d1.values()])

            if debug: print('\n', data[0]['ticker_symbol'], d0_count)
            if debug: print(data[1]['ticker_symbol'], d1_count)

            if d1_count > d0_count:
                out['ticker'] = data[1]['ticker_symbol']
                out['public'] = data[1]['public']
                out['bloomberg_name'] = data[1]['name']
                out.update(d1)
            else:
                out['ticker'] = data[0]['ticker_symbol']
                out['public'] = data[0]['public']
                out['bloomberg_name'] = data[0]['name']
                out.update(d0)

    return out
