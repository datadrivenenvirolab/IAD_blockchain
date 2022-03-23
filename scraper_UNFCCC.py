import pandas as pd 
import numpy as np
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

def get_page_source1(url):
	# Assumes chromedriver is installed on computer;
	# check chromedriver website!
    wd = webdriver.Chrome("/usr/local/bin/chromedriver")
    wd.get(url)
    html_page = wd.page_source
    return html_page


NGO_url = "http://unfccc.int/process/parties-non-party-stakeholders/non-party-stakeholders/admitted-ngos/list-of-admitted-ngos"
NGO_page = get_page_source1(NGO_url)
NGO_unfccc = pd.read_html(NGO_page, header = 0)[0]
print(NGO_unfccc.head())