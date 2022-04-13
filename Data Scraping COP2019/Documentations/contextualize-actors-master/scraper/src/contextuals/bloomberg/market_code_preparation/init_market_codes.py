# http://ultumus.com/bloomberg-exchange-code-to-mic-mapping/
# Bloomberg dataset that maps exchange codes to iso country codes

import os
import pandas as pd

country_dict = pd.read_csv('country_dict.csv')

def standardize_country(name, iso=True):
    try:
        row = country_dict[country_dict['wrong'] == name].to_dict(orient='records')[0]
        if iso:
            return row['iso_code']
        else:
            return row['country_name']
    except:
        try:
            name = name.replace(': ', ':')
            row = country_dict[country_dict['wrong'] == name].to_dict(orient='records')[0]
            if iso:
                return row['iso_code']
            else:
                return row['country_name']
        except:
            print(name)
            return name

standardize_country('ISO 3166-1:' + 'TH')

mic_mappings = pd.read_excel(p + 'Scraper/bloomberg_2/Bloomberg-Exchange-Code-to-MIC-Mapping.xlsx')
mic_mappings.head()

def add_iso_prefix(x):
    try:
        return 'ISO 3166-1:' + x
    except:
        print(x)
        return x
mic_mappings['ISO COUNTRY'] = mic_mappings['ISO COUNTRY'].apply(add_iso_prefix)
mic_mappings['ISO COUNTRY'] = mic_mappings['ISO COUNTRY'].apply(standardize_country)
mic_mappings[pd.isnull(mic_mappings['ISO COUNTRY'])]

mic_mappings.iloc[297]['ISO COUNTRY'] = 'NAM'

import numpy as np
mic_mappings = mic_mappings.replace('NONE', np.nan)
mic_mappings = mic_mappings.replace('No Exchange', np.nan)
mic_mappings = mic_mappings.replace('No Exchange ', np.nan)
mic_mappings = mic_mappings.replace('No Composite Code', np.nan)


mic_mappings.info()

mic_mappings


mic_mappings.iloc[0]['EQUITY EXCH NAME']

market_codes = {}
for n,i in mic_mappings.iterrows():
    if not pd.isnull(i['MIC']):
        if i['MIC'] in market_codes and i['ISO COUNTRY'] != market_codes[i['MIC']]['iso']:
            print(i['MIC'], i['ISO COUNTRY'])
        if not pd.isnull(i['MIC EXCHANGE NAME']):
            market_codes[i['MIC']] = {'iso': i['ISO COUNTRY'], 'name': i['MIC EXCHANGE NAME'], 'type': 'MIC'}
        elif not pd.isnull(i['CORP EXCHANGE']):
            market_codes[i['MIC']] = {'iso': i['ISO COUNTRY'], 'name': i['CORP EXCHANGE'], 'type': 'MIC'}
        elif not pd.isnull(i['EQUITY EXCH NAME']):
            market_codes[i['MIC']] = {'iso': i['ISO COUNTRY'], 'name': i['EQUITY EXCH NAME'], 'type': 'MIC'}
        else:
            market_codes[i['MIC']] = {'iso': i['ISO COUNTRY'], 'name': None, 'type': 'MIC'}
    if not pd.isnull(i['Operating MIC']):
        if i['Operating MIC'] in market_codes and i['ISO COUNTRY'] != market_codes[i['Operating MIC']]['iso']:
            print(i['Operating MIC'], i['ISO COUNTRY'])
        if not pd.isnull(i['MIC EXCHANGE NAME']):
            market_codes[i['Operating MIC']] = {'iso': i['ISO COUNTRY'], 'name': i['MIC EXCHANGE NAME'], 'type': 'Operating MIC'}
        elif not pd.isnull(i['CORP EXCHANGE']):
            market_codes[i['Operating MIC']] = {'iso': i['ISO COUNTRY'], 'name': i['CORP EXCHANGE'], 'type': 'Operating MIC'}
        elif not pd.isnull(i['EQUITY EXCH NAME']):
            market_codes[i['Operating MIC']] = {'iso': i['ISO COUNTRY'], 'name': i['EQUITY EXCH NAME'], 'type': 'Operating MIC'}
        else:
            market_codes[i['Operating MIC']] = {'iso': i['ISO COUNTRY'], 'name': None, 'type': 'Operating MIC'}
    if not pd.isnull(i['EQUITY EXCH CODE']):
        if i['EQUITY EXCH CODE'] in market_codes and i['ISO COUNTRY'] != market_codes[i['EQUITY EXCH CODE']]['iso']:
            print(i['EQUITY EXCH CODE'], i['ISO COUNTRY'])
        if not pd.isnull(i['EQUITY EXCH NAME']):
            market_codes[i['EQUITY EXCH CODE']] = {'iso': i['ISO COUNTRY'], 'name': i['EQUITY EXCH NAME'], 'type': 'Equity Exchange'}
        elif not pd.isnull(i['CORP EXCHANGE']):
            market_codes[i['EQUITY EXCH CODE']] = {'iso': i['ISO COUNTRY'], 'name': i['CORP EXCHANGE'], 'type': 'Equity Exchange'}
        elif not pd.isnull(i['MIC EXCHANGE NAME']):
            market_codes[i['EQUITY EXCH CODE']] = {'iso': i['ISO COUNTRY'], 'name': i['MIC EXCHANGE NAME'], 'type': 'Equity Exchange'}
        else:
            market_codes[i['EQUITY EXCH CODE']] = {'iso': i['ISO COUNTRY'], 'name': None, 'type': 'Equity Exchange'}
    if not pd.isnull(i['Composite Code']):
        if i['Composite Code'] in market_codes and i['ISO COUNTRY'] != market_codes[i['Composite Code']]['iso']:
            print(i['Composite Code'], i['ISO COUNTRY'])
        if not pd.isnull(i['EQUITY EXCH NAME']):
            market_codes[i['Composite Code']] = {'iso': i['ISO COUNTRY'], 'name': i['EQUITY EXCH NAME'], 'type': 'Composite Code'}
        elif not pd.isnull(i['CORP EXCHANGE']):
            market_codes[i['Composite Code']] = {'iso': i['ISO COUNTRY'], 'name': i['CORP EXCHANGE'], 'type': 'Composite Code'}
        elif not pd.isnull(i['MIC EXCHANGE NAME']):
            market_codes[i['Composite Code']] = {'iso': i['ISO COUNTRY'], 'name': i['MIC EXCHANGE NAME'], 'type': 'Composite Code'}
        else:
            market_codes[i['Composite Code']] = {'iso': i['ISO COUNTRY'], 'name': None, 'type': 'Composite Code'}

market_codes_df = pd.DataFrame(market_codes).T

market_codes_df['name'] = market_codes_df['name'].str.title()
market_codes_df.to_csv(p+'data/interim/market_ codes.csv')
