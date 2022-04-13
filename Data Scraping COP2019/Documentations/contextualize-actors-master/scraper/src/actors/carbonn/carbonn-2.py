import urllib.request, urllib.parse, urllib.error, json, re, random
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
import datetime as dt

# function that takes in a url and returns the html soup

THROTTLE_TIME = 0.3

def getPage(link):
    time.sleep(THROTTLE_TIME * (random.random() * 2))
    result = ''
    while result == '':
        try:
            result = requests.get(url)
        except:
            print("Connection refused by the server, sleeping for 15 seconds...")
            time.sleep(15)
            print("Continuing...")
            continue
    if result.status_code == 200:
        response = result.content.decode('utf-8')
        response = BeautifulSoup(response, "html.parser")
        return response
    else:
        print("Request failed")
        return None

# initialize dataframes that will eventually output as csvs
summary_stats = pd.DataFrame()
targets = pd.DataFrame()
mitigation_actions = pd.DataFrame()
adaptation_actions =pd.DataFrame()
action_plans = pd.DataFrame()
inventories = pd.DataFrame()
sector_breakdowns = pd.DataFrame()
skipped_cities = pd.DataFrame()

# read in output of first scraper, which will give entity names and city profile URLs
cities = pd.read_csv('../../../../output/actors/carbonn/carbonn.csv')
cities = cities.rename(columns={'city': 'name'})

# main scraping loop -- currently takes FOREVER
i=1
length = len(cities['name'])

for city, row in cities.iterrows():
    name = row['name']
    country = row['country']
    url = row['city_profile_url']
    url = url.split('&text')[0]
    soup = getPage(url)
    if soup == None:
        holder = {}
        holder['city'] = name
        holder['url'] = url
        skipped_cities = skipped_cities.append(holder, ignore_index=True)
        continue

    # progress
    if i % 25 == 0 and i > 1:
        print('Progress: ' + str(i) + '/' + str(length) + ' entities')

    # SUMMARY STATS

    holder = {}
    holder['city'] = name
    holder['country'] = country
    results = soup.find('div', id='tab1')
    if results is not None:
        counters = results.find_all(class_='counter')
        pop = counters[0].get_text()
        area = counters[1].get_text()
        gdp = counters[2].get_text()
        target = counters[3].get_text()
    holder['population'] = pop
    holder['area (km2)'] = area
    holder['gdp'] = gdp
    holder['target'] = target
    summary_stats = summary_stats.append(holder, ignore_index=True)

    # TARGETS

    # get baseline data

    results = soup.find('div', id='tab2')
    if results is not None:

        results = results.find_all('div', class_='frame')

        if results is not None and len(results) > 0:

            # GHG commitments
            holder = {}

            # Baseline data
            chart_data = results[0].find('div', {'class': 'chart_div'})
            if chart_data is not None:
                chart_unit = chart_data['data-unit']
                chart_data = eval(chart_data['data-chart'])
                if chart_unit == 'CO2e':
                    holder['baseline_year'] = chart_data[0][0].replace('Base year ', '')
                    holder['target_year'] = chart_data[1][0].replace('Target year ', '')
                    holder['baseline_year_emissions'] = chart_data[0][1]
                    holder['target_year_emissions'] = chart_data[1][1]
                    holder['emissions_reduction_by_target_year'] = chart_data[1][2]
                else:
                    holder['baseline_year'] = chart_data[0][0].replace('Base year ', '')
                    holder['target_year'] = chart_data[1][0].replace('Target year ', '')
                    holder['percent_reduction'] = chart_data[1][2]


            ghg_coms = results[0].find_all('div', class_='text')
            for com in ghg_coms:
                holder['city'] = name
                holder['country'] = country
                commitment = com.get_text()
                commitment = commitment.replace('\n', ' ')
                commitment = commitment.replace('\xa0', ' ')
                commitment = commitment.replace('.', '. ')
                holder['commitment'] = commitment
                holder['commitment_type'] = 'GHG emmission reduction target'
                targets = targets.append(holder, ignore_index=True)

            # Renewable energy commitments
            holder = {}
            renewable_coms = results[1].find_all('div', class_='text')
            for com in renewable_coms:
                holder['city'] = name
                holder['Country'] = country
                commitment = com.get_text()
                commitment = commitment.replace('\n', ' ')
                commitment = commitment.replace('\xa0', ' ')
                commitment = commitment.replace('.', '. ')
                holder['commitment'] = commitment
                holder['commitment_type'] = 'Renewable energy target'
                targets = targets.append(holder, ignore_index=True)

            # Energy efficiency commitments
            holder = {}
            energy_coms = results[2].find_all('div', class_='text')
            for com in energy_coms:
                holder['city'] = name
                holder['country'] = country
                commitment = com.get_text()
                commitment = commitment.replace('\n', ' ')
                commitment = commitment.replace('\xa0', ' ')
                commitment = commitment.replace('.', '. ')
                holder['commitment'] = commitment
                holder['commitment_type'] = 'Energy efficiency target'
                targets = targets.append(holder, ignore_index=True)

            # Other mitigation commitments
            holder = {}
            other_coms = results[3].find_all('div', class_='text')
            for com in other_coms:
                holder['city'] = name
                holder['country'] = country
                commitment = com.get_text()
                commitment = commitment.replace('\n', ' ')
                commitment = commitment.replace('\xa0', ' ')
                commitment = commitment.replace('.', '. ')
                holder['commitment'] = commitment
                holder['commitment_type'] = 'Other mitigation target'
                targets = targets.append(holder, ignore_index=True)

            # Adaptation & resilience commitments
            holder = {}
            adapt_coms = results[4].find_all('div', class_='text')
            for com in adapt_coms:
                holder['city'] = name
                holder['country'] = country
                commitment = com.get_text()
                commitment = commitment.replace('\n', ' ')
                commitment = commitment.replace('\xa0', ' ')
                commitment = commitment.replace('.', '. ')
                holder['commitment'] = commitment
                holder['commitment_type'] = 'Adaptation and resilience target'
                targets = targets.append(holder, ignore_index=True)

    # ACTIONS

    holder = {}
    # action plans
    results = soup.find('div', id='tab5')
    if results is not None:
        plans = results.find_all('div', class_='frame')
        for plan in plans:
            holder['city'] = name
            holder['country'] = country
            plan_text = plan.find('a', class_='opener').get_text()
            plan_text = name.replace('\n', '')
            plan_text = name.replace('                ', '')
            plan_text = name.replace('              ', '')
            holder['plan_name'] = plan_text
            text = plan.li.get_text()
            year = text.split(': ')[1]
            holder['start year'] = year
            text2 = plan.li.next_sibling.next_sibling.get_text()
            type_ = text2.split(': ')[1]
            holder['plan_type'] = type_
            action_plans = action_plans.append(holder, ignore_index=True)

    holder = {}
    # mitigation actions
    results = soup.find('div', id='tab6')
    if results is not None:
        actions = results.find_all('div', class_='frame')
        for action in actions:
            holder['city'] = name
            holder['country'] = country
            action_name = action.find('a', class_='opener').get_text()
            holder['name'] = action_name
            text = action.li.get_text()
            year = text.split(': ')[1]
            holder['start year'] = year
            text2 = action.li.next_sibling.next_sibling.get_text()
            type_ = text2.split(': ')[1]
            holder['type'] = type_
            text3 = action.li.next_sibling.next_sibling.next_sibling.next_sibling.get_text()
            status = text3.split(': ')[1]
            holder['status'] = status
            description = action.find('div', class_='text-holder').p.get_text()
            holder['description'] = description
            text4 = action.find('ul', class_='sectors-list').get_text()
            mitigation_actions = mitigation_actions.append(holder, ignore_index=True)

    holder = {}
    # adaptation actions
    results = soup.find('div', id='tab7')
    if results is not None:
        actions = results.find_all('div', class_='frame')
        for action in actions:
            holder['city'] = name
            holder['country'] = country
            action_name = action.find('a', class_='opener').get_text()
            holder['action'] = action_name
            text = action.li.get_text()
            year = text.split(': ')[1]
            holder['start year'] = year
            text2 = action.li.next_sibling.next_sibling.get_text()
            type_ = text2.split(': ')[1]
            holder['type'] = type_
            text3 = action.li.next_sibling.next_sibling.next_sibling.next_sibling.get_text()
            status = text3.split(': ')[1]
            holder['status'] = status
            description = action.find('div', class_='text-holder').p.get_text()
            holder['description'] = description
            adaptation_actions = adaptation_actions.append(holder, ignore_index=True)

    holder = {}
    # GHG Inventories
    results = soup.find('div', id='tab8')
    if results is not None:
        actions = results.find_all('div', class_='frame')
        for action in actions:
            holder['city'] = name
            holder['country'] = country
            inventory_type = action.find('a', class_='opener').get_text()
            holder['inventory_type'] = inventory_type
            description = action.p.get_text()
            #             holder['description'] = description
            graph_title = action.find('strong', class_='graph-title').get_text()
            #             holder['graph_title'] = graph_title
            chart_data_all = action.find_all('div', class_='chart_div')
            for chart_data in chart_data_all:
                holder2 = {}
                chart_type = chart_data.get('data-chart-type')
                #                 holder[chart_type] = chart_type
                chart_id = chart_data.get('id')
                #                 holder[chart_id] = chart_id
                if 'inventory' in chart_type.lower():
                    for entry in json.loads(chart_data.get('data-chart')):
                        if entry:
                            year, emissions = entry[0], entry[1]
                            holder2['year'] = year
                            holder2['emissions'] = emissions
                            holder2.update(holder)
                            inventories = inventories.append(holder2, ignore_index=True)
                elif 'latest' in chart_type.lower():
                    # Use if you want sector emissions in one column with a dictionary of breakdown by sector
                    # holder['sector_emissions'] = {k:v for k,v in json.loads(chart_data.get('data-chart'))}
                    # Use if you want each sector emissions in their own column
                    if not ['N/A', 0] in json.loads(chart_data.get('data-chart')):
                        [holder2.update({sector: emissions}) for sector, emissions in
                         json.loads(chart_data.get('data-chart'))]
                        holder2.update(holder)
                        sector_breakdowns = sector_breakdowns.append(holder2, ignore_index=True)
                else:
                    print('Warning: A GHG emissions chart is not in a known format')
                    print('{}, {}'.format(country, name))
                    print(json.loads(chart_data.get('data-chart')))

    i += 1

    if i == length:
        print('Complete!')

# output dataframes to csv
date = dt.datetime.today().strftime("%m.%d.%y")
summary_stats.to_csv('../../../../output/actors/carbonn/'+date+'carbonn_summary_stats.csv')
targets.to_csv('../../../../output/actors/carbonn/'+date+'carbonn_commitments.csv')
adaptation_actions.to_csv('../../../../output/actors/carbonn/'+date+'carbonn_adaptation_actions.csv')
mitigation_actions.to_csv('../../../../output/actors/carbonn/'+date+'carbonn_mitigation_actions.csv')
action_plans.to_csv('../../../../output/actors/carbonn/'+date+'carbonn_action_plans.csv')
inventories.to_csv('../../../../output/actors/carbonn/'+date+'carbonn_inventories.csv')
sector_breakdowns.to_csv('../../../../output/actors/carbonn/'+date+'carbonn_sector_breakdowns.csv')
skipped_cities.to_csv('../../../../output/actors/carbonn/'+date+'carbonn_skipped_cities.csv')
