import urllib.request, urllib.parse, urllib.error
import csv, json, re
from bs4 import BeautifulSoup
import pandas as pd

### NOTE: This file has ugly code. It was made by copying and pasting several files
###       into the same script so that it could be run from the scraper module.
###       if there's ever time, re-factor it.

# Return the results of querying url stored in a BS4 object.
def download(url):
    req = urllib.request.Request(url, headers={ 'User-Agent' : 'Mozilla/5.0' })
    response = urllib.request.urlopen(req)
    response = response.read().decode('utf-8')
    response = BeautifulSoup(response, "html.parser")
    return response

def get_individual_actions():
    # Return regex matches in a string in the specified type (int or float supported)
    def get_matches(text, regex_strings, typ=''):
        for s in regex_strings:
            r = re.compile(s, re.DOTALL)
            x = []
            try:
                x = r.findall(text)
            except TypeError:
                pass

            try:
                if(typ == 'int'): return int(x[0])
                elif(typ == 'float'): return float(x[0])
                else: return x[0]
            except (IndexError, ValueError) as e:
                continue
        return None

    # Get the total number of individual commitments
    url = 'http://climateaction.unfccc.int/tccommitments.aspx?filterbyid=All&sortdir=ASC&page=1&type=individual&country=0#individual'
    total_commitments = int(download(url).find("div", {"class": "strap"}).span.string)
    print(str(total_commitments) + ' Individual commitments')

    # initialize the dataframe used to store the commitment data
    actions = pd.DataFrame()

    # 50 results per page, calculates number of pages to scrape
    nPages = int(total_commitments / 50) + 1

    # corporations category dictionary
    company_categories = json.load(open('data/company_categories.json', 'r'))

    # Main scraping loop.
    for i in range(1, nPages+1):
        # load commitments on each page.
        template_url = 'http://climateaction.unfccc.int/tccommitments.aspx?filterbyid=All&sortdir=ASC&page={}&type=individual&country=0#individual'.format(i)
        page = download(template_url)
        results = page.find("div", {"id": "theme-result-buttons"})

        # write periodically
        if i % 10 == 0 and i > 1:
            actions.to_csv('data/nazca_individual.csv')
            print('Progress: ' + str(i)+'/'+str(nPages+1) + ' pages')

        # extract data
        for result in results.find_all("div", {"class" : "button"}):
            row = {}
            row['name'] = result.a.h3.string
            row['entity_type']  = result.find("div" , {"class": "entity-type"}).string
            row['url'] = result.a['href']
            row['country'] = result.p.string
            row['raw_commitment'] = result.find("p" , {"class": "action"}).string

            commitment = row['raw_commitment']

            # NAZCA commitment tags
            attrs = result.find("div", {"class" : "commitment-type"})
            for attribute in attrs.find_all("p"):
                row['attr_'+ '_'.join(attribute.string.split(' '))] = 1

            row['percent_reduction'] = get_matches(commitment, ['by (\d*.?\d*)%', 'to (\d*.?\d*)%'], 'int')

            # get baseline and target years
            years = get_matches(commitment, ['from (\d\d\d\d) to (\d\d\d\d)','by (\d\d\d\d)'])
            if (years != None and type(years) is tuple):
                row['baseline_year'] = int(years[0])
                row['target_year'] = int(years[1])
            elif (years != None):
                row['target_year'] = int(years)

            # find dollar values stored in commitments
            row['dollar_value'] =get_matches(commitment, ['USD (\d*.?\d*[a-z]?)'])
            if (row['dollar_value'] != None):
                if 'm' in row['dollar_value']:
                    row['dollar_value'] = float(row['dollar_value'].replace('m','')) * 1000000
                elif 'b' in row['dollar_value']:
                    row['dollar_value'] = float(row['dollar_value'].replace('b','').replace('n','')) * 1000000000
                try:
                    row['dollar_value'] = float(row['dollar_value'])
                except ValueError:
                    pass

            # get commitment sources
            src = result.select('div.svg.more')
            sources = []
            for i in src:
                c = i['class']
                for j in ['more', 'svg', 'black']:
                    if j in c:
                        c.remove(j)
                row[c[0].replace('external', '').replace('cofmayors', 'covenant_of_mayors')] = 1


            # add other attributes
            try:
                if 'green bond' in commitment:
                    row['green_bond'] = 1

                if 'community' in commitment:
                    row['community_wide'] = 1
            except TypeError:
                pass

            # company category
            try:
                row['company_classification'] = company_categories[row['name'] + '///' + row['country']]
            except KeyError:
                pass

            actions = actions.append(row, ignore_index=True)

    actions.to_csv('data/nazca_individual.csv')
    return actions

def get_group_actions(headers, company_categories):














#
