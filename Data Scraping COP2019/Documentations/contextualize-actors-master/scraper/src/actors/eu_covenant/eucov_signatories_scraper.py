"""
This is a scraper for signatories page

"""

import pandas as pd
import requests

import datetime

from bs4 import BeautifulSoup
import bs4
# get the links to all member pages.

# url = 'http://www.covenantofmayors.eu/about/covenant-community/signatories.html?tmpl=response&limit=all&filter_order=a.signatory_name&filter_order_Dir=ASC&start=0&tmpl=response'
url = "https://www.covenantofmayors.eu/about/covenant-community/signatories.html?limit=all&filter_order=a.signatory_name&filter_order_Dir=ASC&start=0"
page = BeautifulSoup(requests.get(url).content, 'lxml')

output_list = []
check = page.find_all(id = 'loadItems')
index = 0
for item in check[0].contents:
    try:
        city_dict = {}
        if isinstance(item,bs4.element.NavigableString):
            continue
        infos = item.find_all("td")

        name_line = infos[0]
        pop_line = infos[1]
        commitments = infos[2]
        status_line = infos[3]
        adhesion_line = infos[4]

        # extract city name
        city_dict['name'] = name_line.text
        city_dict['population'] = pop_line.text
        commit_temp = commitments.text.split('\n')
        commit_year = [i for i in commit_temp if i != '']
        city_dict['commitments'] = commit_year
        city_dict['adhesion date'] = adhesion_line.text
        output_list.append(city_dict)

        if index % 1000 == 0:
            print("Finished {} rows".format(index))

        index +=1
    except Exception as e:
        print(e, index)

output_df = pd.DataFrame(output_list)
date = datetime.datetime.today().strftime("%m.%d.%y")
output_path = '../../../../output/actors/EU Covenant/{}signatories.csv'.format(date)
output_df.to_csv(output_path)

print("scraper ends")
