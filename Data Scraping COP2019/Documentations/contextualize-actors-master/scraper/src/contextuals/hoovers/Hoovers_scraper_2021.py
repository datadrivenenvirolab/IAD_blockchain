"""
This script is edited based on Hoovers_scraper_2020.ipynb
"""

# Initialization
import requests, pickle, time
from urllib.parse import urljoin
from multiprocessing.pool import ThreadPool, Pool
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import threading

import pandas as pd
import re
import time
from tqdm import tqdm




# To use chrome, will need to ensure that chromedriver is in the path

driver = webdriver.Chrome(r"C:\Users\wangx\Documents\GitHub\Tools\chromedriver_win32\chromedriver.exe")
driver.get("https://linc.nus.edu.sg/record=b2679651")
elem = driver.find_element_by_link_text("D&B Hoovers (formerly known as D&B Business Browser)")
elem.send_keys(Keys.RETURN)

# Enter your username and password here to send over selenium, or alt tab over to the opened browser to key in manually
username = "E0333037"
password = "redwoodcloud$844"
One_to_One = True

# def login_check(url):
def get_actor(container):
    # Get soup
    soup = BeautifulSoup(container.get_attribute('outerHTML'), 'lxml')
    # Name, sector, and location are in every actor, so no need for checks
    name = soup.find(attrs={'class': 'clickable'}).text
    href =soup.find(attrs={'class': 'clickable'})['href']
    sector = soup.find(attrs={'class': 'large-black-text'}).text
    location = re.sub('\s', '', soup.find(attrs={'class': 'location'}).text)
    # For the others (revenue, employees, etc.) it is not guaranteed the data is present
    # so need to check
    if soup.find(attrs={'class': 'sales black'}) is not None:
        revenue = soup.find(attrs={'class': 'sales black'}).text.replace('\n\xa0\n\n', '')
    else:
        revenue = 'NA'
    labels = []
    for label in soup.find_all(attrs={'class': 'data-label'}):
        labels.append(re.sub('\n|\xa0|  |•', '', label.text))
    labels = '; '.join(labels)
    # Now check for the different fields in labels and scrape whatever we can find
    # Check for employees and assets
    if bool(re.search("Employees \(This Site\)", labels)):
        employees_local = re.sub(".*?Employees \(This Site\):([0-9,\\.kMB]+).*", '\\1', labels)
    else:
        employees_local = 'NA'
    if bool(re.search("Employees \(All Sites\)", labels)):
        employees_all = re.sub(".*?Employees \(All Sites\):([0-9,\\.kMB]+).*", '\\1', labels)
    else:
        employees_all = 'NA'
    if bool(re.search("Assets", labels)):
        assets = re.sub(".*?Assets:([0-9\\.MB]+).*", '\\1', labels)
    else:
        assets = 'NA'

    # Search fiscal year if any:
    Fiscal_year = None
    try:
        report_url = 'https://app.avention.com/' + href +'#report/company_summary'
        driver.get(report_url)
        financial_info = driver.find_elements_by_class_name('data-container') # TODO: update class name
        for container in financial_info:
            cont_info = BeautifulSoup(container.get_attribute('outerHTML'), 'lxml')
            cont_label = cont_info.find(attrs={'class': 'data-label'})
            if  cont_label is not None:
                if 'Fiscal Year' in cont_label.text:
                    Fiscal_year = cont_info.find(attrs={'class': 'data-value'}).text.replace(' ','')
                    print(Fiscal_year)
    except Exception as e:
        print("Failed to get Fiscal Year",e,"--- ",name)


    actor_data = pd.DataFrame({'name': name, 'sector': sector, 'location': location,
                               'revenue': revenue, 'employees_local': employees_local,
                               'employees_all': employees_all, 'assets': assets,"Fiscal_year":Fiscal_year},
                              index=[0])
    return actor_data

def get_page(url):
    driver.get(url)
    time.sleep(5)
    # Parse info on page
    # Check if any results returned first
    num_results = driver.find_elements_by_class_name('js-total-results.total-count-number')[0].text
    if int(num_results.replace(',', '')) == 0:
        print(" No findings: ",url)
        return []
    actors = driver.find_elements_by_class_name('container-fluid')
    df = []
    if One_to_One:
        df.append(get_actor(actors[0]))
    else:
        for actor in actors:
            df.append(get_actor(actor))
    # Use the top 1 result instead of all of them
    return(df)

if __name__ == "__main__":
    # load in list to scrape
    cdp = pd.read_csv(
        r"C:\Users\wangx\Documents\GitHub\Data-Driven\Working notes\Revenue\RaceToZero_MasterParticipantsList_Companies_names_full.csv",
        encoding="UTF-8")

    ID_colname = "GCAP ID"
    print(cdp.head())
    print(cdp.shape)

    company_names = cdp.drop_duplicates()
    company_names.head()

    company_names = company_names.reset_index(drop = True)
    print(company_names.shape)

    company_names.rename(columns = {"Name":"name","UN Country":"country"},inplace = True)
    # Main Scraping loop
    stem =  'https://app.avention.com/search/company?q='
    main = []
    errors = []
    flatten = lambda l: [item for sublist in l for item in sublist]


    for i in tqdm(range(company_names.shape[0])):
        # Save every 300 names get scraped
        if i % 300 == 0 & i != 0:
            print("check_point:",i)
            # main_rm = [i for i in main if i]
            # main_export = pd.concat(flatten(main_rm))
            main_export = pd.concat(main)
            main_export.to_csv(r"C:\Users\wangx\Downloads\Hoover_NtZ_{}-{}.csv".format(300*(i-1),300*i),
                              encoding = 'UTF-8')
        try:
            url = stem + company_names['name'][i]

            page_result = get_page(url)
            if One_to_One:
                page_result = page_result[0]
            else:
                page_result = pd.concat(page_result)

            page_result['name_orig'] =company_names['name'][i]
            page_result['ID'] = company_names[ID_colname][i]
            main.append(page_result)
        except:
            print('Error scraping for ' + company_names['name'][i])
            errors.append({'name':company_names['name'][i],"ID":company_names[ID_colname][i]})

        # if i >30:
        #     break

    # Try scraping for errors again
    stem =  'https://app.avention.com/search/company?q='
    for i in tqdm(range(len(errors))):
        try:
            url = stem + errors[i]
            page_result = get_page(url)
            if One_to_One:
                page_result = page_result[0]
            else:
                page_result = pd.concat(page_result)

            page_result['name_orig'] = errors[i]['name']
            page_result['ID'] = errors[i][ID_colname]
            main.append(page_result)
        except:
            print('Error scraping for ' + errors[i])
            errors.append(errors[i])


    # main_rm = [i for i in main if i]
    main_df = pd.concat(main)


