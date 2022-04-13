# importing required modules
import requests
import urllib
import pandas as pd
import numpy as np
from requests_html import HTML
from requests_html import HTMLSession
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup


def get_source(url):
    """Return the source code for the provided URL. 

    Args: 
        url (string): URL of the page to scrape.

    Returns:
        response (object): HTTP response object from requests_html. 
    """

    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)


        
def scrape_google(query):
    """
    This function returns all the links that pop up on the first page of Google results for a given query.
    
    Args:
        query (string): the query to search
    
    Returns:
        links (list): list of links (string) that were extracted from Google
    """
    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.com/search?gl=US&q="+ query)
    links = list(response.html.absolute_links)
    google_domains = ('https://www.google.', 
                      'https://google.', 
                      'https://webcache.googleusercontent.', 
                      'http://webcache.googleusercontent.', 
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.',
                      'https://translate.google.')

    for url in links[:]:
        if url.startswith(google_domains):
            links.remove(url)
        if ((url[-4:] == ".pdf") or (url[-5:] == ".docx") or (url[-4:] == ".doc") or (url[-4:] == ".xml") or (url[-5:] == ".xaml")):
            links.remove(url)

    if (len(links) < 10):
        return links
    
    return links[0:10]


def get_text_from_URL(url):
    """
    Get the raw text from a given url, stripped of all script and style elements.

    Args: 
        url (string): URL of the page to scrape.

    Returns:
        text (string): raw text extracted from the webpage passed as argument.
    """
    html = urlopen(url).read().decode('utf-8', 'ignore').encode("utf-8")
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text


COP2019 = pd.read_csv("COP2019_participation.csv", index_col=False)

# create organizations dataframe, containing only NGOs and IGOs
organizations = COP2019[(COP2019.entity_type == 'Intergovernmental organizations')|(COP2019.entity_type == 'Non-governmental organizations')].copy()
organizations1 = organizations.iloc[(-20):-1,].copy()


def scrape(organizations):
    scraped_texts = []
    org_list = list(organizations)
    for i in range(len(org_list)):
        organization = str(org_list[i])
        list_of_links = scrape_google(organization)
        for link in list_of_links:
            try:
                text = str(get_text_from_URL(link))
                scraped_texts.append(text)
            except:
                pass
    return scraped_texts

scraping_result = scrape(organizations.name)

scraping_result = [text for text in scraping_result if len(text)>1000]

df = pd.DataFrame(scraping_result,columns=['Text'])
df.to_csv("scraped_websites.csv", encoding='utf-8-sig')


