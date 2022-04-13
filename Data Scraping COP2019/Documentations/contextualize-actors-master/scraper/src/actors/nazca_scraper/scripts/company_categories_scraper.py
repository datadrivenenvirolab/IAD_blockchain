import urllib.request, urllib.parse, urllib.error
import csv, json, re
from bs4 import BeautifulSoup
import pandas as pd

# Return the results of querying url stored in a BS4 object.
def download(url):
    req = urllib.request.Request(url, headers={ 'User-Agent' : 'Mozilla/5.0' })
    response = urllib.request.urlopen(req)
    response = response.read().decode('utf-8')
    response = BeautifulSoup(response, "html.parser")
    return response

categories = {}
page = download('http://climateaction.unfccc.int/companies')
page = page.find_all('a', href=True)
for url in page:
    if '/companies/' in url['href'] and url.text != 'View all':
        name = url.find('h3').text
        print('Sector scraped: ' + name)
        companies = download('http://climateaction.unfccc.int' + url['href'])
        companies = companies.find('div', {'class': 'company-result-buttons'})
        companies = companies.find_all('div', {'class': 'button'})
        for c in companies:
            categories[c.find('h3').text + '///' + c.find('p').text] = name

page = download('http://climateaction.unfccc.int/investors')
page = page.find_all('a', href=True)
for url in page:
    if '/investors/' in url['href'] and url.text != 'View all':
        name = url.find('h3').text
        companies = download('http://climateaction.unfccc.int' + url['href'])
        companies = companies.find('div', {'class': 'company-result-buttons'})
        companies = companies.find_all('div', {'class': 'button'})
        for c in companies:
            categories[c.find('h3').text + '///' + c.find('p').text] = name
        print('Sector scraped: ' + name)

json.dump(categories, open('data/company_categories.json', 'w'))
