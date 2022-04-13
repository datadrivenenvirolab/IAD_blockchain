import requests
import re
import time
from json import JSONDecodeError
from random import random
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from itertools import chain

import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import datetime as dt
import os

current_path = os.path.dirname(__file__)

workingdir = os.path.join(current_path,"data")
os.makedirs(workingdir,exist_ok=True)
print(workingdir)

# ----- global params -----
url = 'http://www.covenantofmayors.eu/about/covenant-community/signatories.html?tmpl=response&limit=all&filter_order=a.signatory_name&filter_order_Dir=ASC&start=0&tmpl=response'
page = BeautifulSoup(requests.get(url).content, 'lxml')
links = [i['href'] for i in page.find_all('a')]
print("Number of links:", len(links))
baseline_df = []
action_plan_df = []
progress_df = []
key_actions_df = []
overview_df = []

# ----------- Processing functions -----------

# 1. per link
def get_page(url):
    p = requests.get(url).content
    p = BeautifulSoup(p, "lxml")
    return p


def overview(link):
    print("\n===== overview df =====\n")
    #     l = link.replace('action-plan', 'overview')
    p = get_page(link)

    name = p.find('div', {'class': 'api-sidebar'}).find('h3').text

    # sidebar info.
    tmp = p.find('div', {'class': 'api-sidebar'}).find_all('p')
    country = tmp[0].text
    population = tmp[1].text.replace(',', '')
    adhesion_date = tmp[2].text

    # lat, lng
    coords = p.find('iframe')['src'].split('=')[1].split('&')[0].split(',')
    coords = [float(c) for c in coords]
    lat, lng = coords[0], coords[1]

    return {'name': name, 'country': country, 'population': population,
            'adhesion_date': adhesion_date, 'latitude': lat, 'longitude': lng, 'url': link}

# Baseline Review
baseline_stems = [('percent_emissions_', 'tons_co2_', 'emissions_baseline_year',
                   '?task=baseline_review.emissions_per_sector_12&orgid='),
                  ('percent_energy_consumption_', 'mwh_energy_consumption_', 'energy_consumption_baseline_year',
                   '?task=baseline_review.consumption_per_sector_12&orgid='),
                  ('percent_energy_consumption_from_', 'mwh_energy_consumption_from_',
                   'energy_consumption_baseline_year', '?task=baseline_review.consumption_per_carrier_1&orgid=')]


def baseline(link):
    print("\n===== baseline df =====\n")
    l = link.replace('overview', 'baseline-review')
    stem_url = l.split('?')[0]
    city_id = l.split('?')[1].split('=')[1]
    p = get_page(l)

    data = {}
    for percent_label, value_label, baseline_label, s in baseline_stems:
        url = stem_url + s + city_id
        try:
            result = requests.get(url).json()
        except JSONDecodeError:
            continue

        if 'rname' in result:
            print("Baseline: -- Getting rname")
            labels = [r.lower() for r in result['rname']]
            per = dict(zip([percent_label + l for l in labels], result['percentage']))
            amt = dict(zip([value_label + l for l in labels], result['rvalue']))

            data[baseline_label] = result['year']
            data.update(per)
            data.update(amt)

    if p.find_all('table') is not None:
        emissions_info = p.find_all('table')
        if len(emissions_info) > 0: emissions_info = emissions_info[0].find_all('td')
        if len(emissions_info) > 0:
            print("Baseline: -- Getting emissions_info")
            data['emissions_factor'] = emissions_info[0].text
            data['tons_co2_per_capita'] = emissions_info[1].text
            data['mwh_per_capita'] = emissions_info[2].text

    return data

# action plan
action_stems = [('planned_percent_emissions_reduction_', 'planned_emissions_reduction_tonnes_co2_',
                 '?task=actionplan.estimated_reduction&orgid=')]


def action_plan(link):
    print("\n===== action_plan df =====\n")
    l = link.replace('overview', 'action-plan')
    p = get_page(l)
    stem_url = link.split('?')[0]
    city_id = link.split('?')[1].split('=')[1]

    data = {}
    for percent_label, value_label, s in action_stems:
        url = stem_url + s + city_id
        try:
            result = requests.get(url).json()
        except JSONDecodeError:
            continue

        if 'rname' in result:
            print("action_plan: -- Getting emissions_info")
            labels = [r.lower() for r in result['rname']]
            per = dict(zip([percent_label + l for l in labels], result['percentage']))
            amt = dict(zip([value_label + l for l in labels], result['rvalue']))

            data.update(per)
            data.update(amt)

    url = stem_url + '?task=actionplan.expected_evolution&orgid=' + city_id
    result = requests.get(url).json()
    if 'rvalue' in result:
        print("action_plan: -- Getting emissions_info")
        data['expected_emissions_co2_' + result['rname'][1]] = result['rvalue'][1]
        data['baseline_emissions_co2'] = result['rvalue'][0]

    date_info = p.find('ul', {'class': 'gen-fields'}).find_all('li')
    if len(date_info) > 0:
        print("action_plan: -- Getting dates")
        data['approval_date'] = date_info[0].find_all('span')[1].text
        if len(date_info) > 1: data['submission_date'] = date_info[1].find_all('span')[1].text

    try:
        target_info = p.find_all('table')[1].find_all('td')
        float(target_info[1].text)
    except:
        try:
            target_info = p.find_all('table')[0].find_all('td')
            float(target_info[1].text)
        except:
            target_info = False

    a = 0
    if target_info:
        while target_info:
            a += 1
            data['target_year_' + str(a)] = target_info[0].text
            data['percent_reduction_' + str(a)] = target_info[1].text
            data['estimated_tonnes_reduced_' + str(a)] = target_info[2].text
            del target_info[:3]
    else:
        if len(date_info) > 0:
            tmp = date_info[-1].find_all('span')
            if len(tmp) > 0:
                tmp = tmp[1].text.replace('%', '')
                if "-" not in tmp: data['percent_reduction_1'] = tmp

    tmp = p.find_all('p')
    if len(tmp) > 1:
        print("action_plan: -- append to data strategy")
        data['strategy'] = tmp[-2].text

    return data

progress_stems = [('status_', '?task=actionplan.mitigation_actions&orgid='),
                  ('overall_budget_spent', '?task=actionplan.budget_spent&orgid='),
                  ('budget_per_sector', '?task=actionplan.monitoring_budget_spent_per_sector&orgid='),
                  ('estimated_ghg_reduction', '?task=actionplan.monitoring_estimated_reduction_by_status&orgid='),
                  ('emissions_per_sector', '?task=actionplan.monitoring_emission_per_sector&orgid='),
                  ('energy_consumption', '?task=actionplan.monitoring_consumption_per_carrier&orgid='),
                  ('energy_consumption_fuel', '?task=actionplan.monitoring_consumption_per_carrier&orgid='),
                  ('local_electricity_production', '?task=actionplan.monitoring_local_energy_production_electricity&orgid='),
                  ('local_heatcold_production', '?task=actionplan.monitoring_local_energy_production_heatcold&orgid=')]


def progress(link, id_info):
    print("\n===== progress df =====\n")
    # test scity_id=11794 .. This is Paris
    l = link.replace('overview', 'progress')
    p = get_page(l)
    stem_url = l.split('?')[0]
    city_id = l.split('?')[1].split('=')[1]

    # get list of all years where data has been updated
    years = p.find(attrs={'id': 'syear'})

    # if there's a year value
    # TODO: could not get the year info from progress page.
    if years is not None:
        print("progress: -- getting value in years")
        # look for multiple values
        if years.find_all('option'):
            years = [year.text for year in years.find_all('option')]
        # look for single value (different schema)
        elif 'value' in years:
            years = [years['value']]
        else:
            return {}
    # if not year, cease running since there won't be data
    else:
        return {}

    d = []
    print("progress: -- appending info for years in progress_stems")
    for year in years:
        for k, s in progress_stems:
            url = stem_url + s + city_id + '&syear=+' + year
            try:
                result = requests.get(url).json()
            except:
                continue
            try:
                # skip empty charts.
                if result is not None:
                    if 'rkey' in result and (len(result['rkey']) == 0 or result['rkey'][0] == ''):
                        continue

                    if 'mstatus' in result and result['mstatus'] == 0:
                        continue

                    if 'pstatus' in result and result['pstatus'] == 0:
                        continue

                    if 'rstatus' in result and result['rstatus'] == 0:
                        continue

                    if 'rkey' in result:
                        data = []
                        for y in result['rkey']:

                            for n, i in enumerate(result['all_status'][y]):
                                temp = dict(id_info)
                                if k != 'status_':
                                    temp['year'] = y
                                    temp['key'] = k
                                    temp['value'] = i
                                    temp['sector'] = result['total_status'][n].lower()
                                    data.append(temp)

                                else:
                                    temp['key'] = k + y
                                    temp['value'] = i
                                    temp['sector'] = result['total_status'][n].lower()
                                    temp['year'] = year
                                    data.append(temp)

                            d += data

                    if ('pstatus' in result or 'mstatus' in result) and 'rname' in result:
                        data = []
                        for n, l in enumerate(result['rname']):
                            temp = dict(id_info)
                            temp['year'] = result['year']
                            temp['sector'] = l.lower()
                            temp['value'] = result['rvalue'][n]
                            temp['key'] = k
                            data.append(temp)

                        d += data
            except:
                continue
    return d
# get the links to all member pages.


# Key Actions
def clean_action_text(x):
    return x.replace('\n', ' ')

def get_action_data(category, l):
    for a in l:
        s = a.find_all('span')
        if s is not None:
            if s[0].text == category:
                return clean_action_text(s[1].text)

def key_actions(link, id_data):
    print("\n===== key_actions df =====\n")
    data = []
    l = link.replace('overview', 'key-actions')
    p = get_page(l)
    actions = p.find('ul', {'class': 'accordion'})
    if actions is not None: actions = actions.find_all('div', {'class': 'inner'})
    if actions is not None:
        print("key_actions: -- appending key_actions info ")
        for a in actions:
            tmp = dict(id_data)
            s = a.find_all('li')
            if s is not None:
                tmp['action_description'] = s[0].find_all('p')[1].text
                tmp['language'] = get_action_data('Language:', s[1:])
                tf = get_action_data('Implementation timeframe:', s[1:])
                tmp['action_start_year'] = tf.split('-')[0]
                tmp['action_end_year'] = tf.split('-')[1]
                tmp['action_cost'] = get_action_data('Implementation cost:', s[1:])
                tmp['action_website'] = get_action_data('Website:', s[1:])
                tmp['action_co2_reduction'] = get_action_data('CO2 reduction:', s[1:])
            data.append(tmp)
    return data

# Updating Progress Page (Nov 2019)
# Code below runs only for progress loop. For update run done in Nov 2019. Remove/Comment out for future scrapes

# Run scraper loop just for progress page

def progress_helper(link):
    progress_df= []
    p = get_page(link)
    name = p.find('div', {'class': 'api-sidebar'}).find('h3').text
    tmp = p.find('div', {'class': 'api-sidebar'}).find_all('p')
    country = tmp[0].text
    id_data = {'name': name, 'country': country}
    t = progress(link, id_data)
    progress_df.append(t)


# Helper Functions
# Helper function that runs all functions for 1 link
def get_data(link):

    print("\n<<<<<<<<processing ID:{} >>>>>>>>>".format(link.split('=')[-1]))
    # baseline_df = []
    # action_plan_df = []
    # progress_df = []
    # key_actions_df = []
    # overview_df = []

    data = {}
    try:
        data.update(overview(link))
        id_data = {'name': data['name'], 'country': data['country']}
    except Exception as e:
        print(e,'--Error at get overview')
        id_data= {}

    try:
        t = baseline(link)
    except Exception as e:
        print(e,'--Error at get baseline')
        t= {}
    t.update(id_data)
    baseline_df.append(t)

    try:
        t = action_plan(link)
    except Exception as e:
        print(e,'--Error at get action_plan')

    t.update(id_data)
    action_plan_df.append(t)


    # Using += returns an error, change to append
    try:
        t = progress(link, id_data)
    except Exception as e:
        print(e,'--Error at get progress')

    progress_df.append(t)

    try:
        t = key_actions(link, id_data)
    except Exception as e:
        print(e,'--Error at get key_actions')

    key_actions_df.append(t)

    overview_df.append(data)

    # return baseline_df,action_plan_df,progress_df,key_actions_df,overview_df



# function that converts action_plan data from wide to long (each action has its own row)

def wide_to_long(action_plan_df):
    final = []

    new_labels = ['target_year_1', 'percent_reduction_1', 'estimated_tonnes_reduced_1', 'target_year_2',
                  'percent_reduction_2', 'estimated_tonnes_reduced_2', 'target_year_3', 'percent_reduction_3',
                  'estimated_tonnes_reduced_3']
    action_labels = ["target_year", "percent_reduction", "estimated_tonnes_reduced"]

    for x in action_plan_df:
        labs = list(x.keys())
        labels = list(set(labs) - set(new_labels))
        add = {}
        for l in labels:
            add[l] = x[l]
        for a in action_labels:
            if a + "_1" in labs: add[a] = x[a + "_1"]
        final.append(add)
        for z in range(2, 4):
            add = {}
            for y in labels:
                add[y] = x[y]
            if 'percent_reduction_%s' % z in labs:
                for a in action_labels:
                    add[a] = x[a + "_%s" % z]
                final.append(add)

    return final



if __name__ == "__main__":
    url = 'http://www.covenantofmayors.eu/about/covenant-community/signatories.html?tmpl=response&limit=all&filter_order=a.signatory_name&filter_order_Dir=ASC&start=0&tmpl=response'
    page = BeautifulSoup(requests.get(url).content, 'lxml')
    links = [i['href'] for i in page.find_all('a')]
    print("Number of links:", len(links))
    links = links[1000:1010]


    baseline_df = []
    action_plan_df = []
    progress_df = []
    key_actions_df = []
    overview_df = []

    stop = 15000

    for n, link in tqdm(enumerate(links)):
        if n > stop: break # What does this mean?

    pool = ThreadPool(1)
    jobs = pool.map_async(get_data, links, chunksize=1)
    pool.close()
    # Print how many links left at every minute to ensure code is running
    while True:
        if not jobs.ready():
            print('There are %s links left to scrape.' % jobs._number_left)
            time.sleep(60)
        else:
            break
    pool.join()

    # Check for length of scraped data
    print("overview_df",len(overview_df) )
    print("baseline_df", len(baseline_df))
    print("action_plan_df", len(action_plan_df))

    # Cell to convert action_plan data from wide to long

    action_plan_df = wide_to_long(action_plan_df)
    len(action_plan_df)

    # Check which actor didn't get scraped
    overview_pddf = pd.DataFrame(overview_df)
    miss = list(set(links[:10]) - set(overview_pddf['url']))
    # Scrape the link that did not get scraped in the main loop
    for link in miss:

        get_data(link)

    overview_pddf = pd.DataFrame(overview_df)
    baseline_pddf = pd.DataFrame(baseline_df)
    action_plan_pddf = pd.DataFrame(action_plan_df)

    print("checks")
    # Clean up the other dataframes
    ##### flatten = lambda l: [item for sublist in l for item in sublist]
    progress_pddf = pd.DataFrame(list(chain.from_iterable(progress_df)))
    key_actions_pddf = pd.DataFrame(list(chain.from_iterable(key_actions_df))) # Flatten the list of list into list of dict

    overview_pddf['ACTION'] = baseline_pddf['emissions_factor'].apply(lambda x: 0 if pd.isnull(x) else 1)
    #
    overview_pddf['MONITOR'] = baseline_pddf['emissions_factor'].apply(lambda x: 0 if pd.isnull(x) else 1)

    if not progress_pddf.empty:
        progress_pddf[['name', 'country']].drop_duplicates().shape
        progress_pddf.info

        #
        x = progress_pddf[['name', 'country']]
        x['MONITOR'] = 1
        overview_pddf = overview_pddf.merge(x, on=['name', 'country'], how='left')  # Not sure what this merge is for
    #
        overview_pddf['MONITOR'] = overview_pddf['MONITOR'].apply(lambda x: 0 if pd.isnull(x) else 1)

    print("checks")

    # # Save to csv
    date = dt.datetime.today().strftime("%m.%d.%y")
    if not baseline_pddf.empty:
        baseline_pddf.to_csv(workingdir+'/' + date + 'baseline.csv', encoding="utf-8")

    if not action_plan_pddf.empty:
        action_plan_pddf.to_csv(workingdir+'/' + date + 'action_plan.csv', encoding="utf-8")
    if not progress_pddf.empty:
        progress_pddf.to_csv(workingdir+'/' + date + 'progress.csv', encoding="utf-8")
    if not key_actions_pddf.empty:
        key_actions_pddf.to_csv(workingdir+'/' + date + 'key_actions.csv', encoding="utf-8")

    if not overview_pddf.empty:
        overview_pddf.to_csv(workingdir+'/' + date + 'overview.csv', encoding="utf-8")