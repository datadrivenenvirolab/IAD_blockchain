import urllib.request, urllib.parse, urllib.error, json, re
from bs4 import BeautifulSoup
import pandas as pd
import http, csv

# Return the results of querying url stored in a BS4 object.
def download(url):
    req = urllib.request.Request(url, headers={ 'User-Agent' : 'Mozilla/5.0' })
    response = urllib.request.urlopen(req)
    response = response.read().decode('utf-8')
    response = BeautifulSoup(response, "html.parser")
    return response

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

# get the initiative URLs.
url = 'http://climateaction.unfccc.int/cooperative-initiatives/themes/all-themes'
page = download(url)

page = page.find('div', {'id': 'theme-result-buttons'})

initiative_urls = []
for i in page.find_all('a', href=True):
    initiative_urls.append((i.find('h3').text, i['href']))

# get initiatve contextuals and members.
initiatives = {}
total = 0
for i in initiative_urls:
    initiatives[i[0]] = {}
    url = 'http://climateaction.unfccc.int' + i[1]

    # g7-climate-risk-insurance-initiative page seems to be broken.
    try:
        page = download(url)
    except http.client.BadStatusLine:
        continue

    initiatives[i[0]]['cooperative-initiative'] = i[0]
    initiatives[i[0]]['url'] = i[1]

    attrs = page.find('div', id='coop-themes')
    for p in attrs.find_all('p'):
        initiatives[i[0]]['attr_'+ '_'.join(p.string.split(' '))] = 1

    # description
    attrs.extract()
    desc = page.find('div', {'class': 'strap'})
    commitment = desc.find('p').text
    initiatives[i[0]]['raw_commitment'] = commitment

    # get baseline and target years
    years = get_matches(commitment, ['from (\d\d\d\d) to (\d\d\d\d)','by (\d\d\d\d)'])
    if (years != None and type(years) is tuple):
        initiatives[i[0]]['baseline_year'] = int(years[0])
        initiatives[i[0]]['target_year'] = int(years[1])
    elif (years != None):
        initiatives[i[0]]['target_year'] = int(years)

    # find dollar values stored in commitments
    dv = get_matches(commitment, ['USD (\d*.?\d*[a-z]?)'])
    if (dv != None):
        if 'm' in dv:
            initiatives[i[0]]['dollar_value'] = float(dv.replace('m','')) * 1000000
        elif 'b' in dv:
            initiatives[i[0]]['dollar_value'] = float(dv.replace('b','').replace('n','')) * 1000000000
        else:
            try:
                initiatives[i[0]]['dollar_value'] = float(dv)
            except ValueError:
                pass

    # add other attributes
    try:
        if 'green bond' in commitment:
            initiatives[i[0]]['green_bond'] = 1

        if 'community' in commitment:
            initiatives[i[0]]['community_wide'] = 1
    except TypeError:
        pass

    # get members
    initiatives[i[0]]['members'] = {}
    page = page.find('div', id='theme-result-buttons')

    if page == None:
        initiatives[i[0]]['members'] = None
    else:
        current_entity_type = ''
        for a in page.find_all('div'):
            if a['class'][0] == 'sectionheader':
                translate = {'companies': 'Company', 'cities': 'City', 'regions': 'Region', 'investors': 'Investor', 'countries': 'Country', 'civil society organizations': 'CSO', 'organizations': 'Organization'}
                current_entity_type = ' '.join(a.text.split(' ')[:-1]).lower() #remove entity counts from string
                total += int(a.text.split(' ')[-1].replace('(', '').replace(')', ''))
                current_entity_type = translate[current_entity_type]
            elif a['class'][0] == 'supporter':
                name = a.find('h3').text
                initiatives[i[0]]['members'][name] = {}
                initiatives[i[0]]['members'][name]['name'] = name

                try:
                    initiatives[i[0]]['members'][name]['url'] = a.parent['href']
                except KeyError:
                    initiatives[i[0]]['members'][name]['url'] = None

                try:
                    initiatives[i[0]]['members'][name]['country'] = a.find('p').text
                except AttributeError:
                    initiatives[i[0]]['members'][name]['country'] = None

                initiatives[i[0]]['members'][name]['entity_type'] = current_entity_type
    print('Scraped ' + i[0])

print('Total cooperative initiative commitments found: ' + str(total))

json.dump(initiatives, open('data/nazca_group.json', 'w'), indent=2)

# flatten and write to CSV
f = csv.reader(open('data/nazca_individual.csv', 'r'))
headers = next(f) + ['cooperative-initiative']

company_categories = json.load(open('data/company_categories.json', 'r'))

rows = []

for initiative in initiatives.keys():
    template_row = ['' for i in range(len(headers))]
    for i in initiatives[initiative].keys():
        if i != 'members':
            try:
                template_row[headers.index(i)] = initiatives[initiative][i]
            except ValueError:
                headers.append(i)
                template_row += [initiatives[initiative][i]]

    try:
        members = initiatives[initiative]['members']
        if members != None:
            for member in members.keys():
                row = [i for i in template_row]
                for k in members[member].keys():
                    row[headers.index(k)] = members[member][k]
                if row[headers.index('entity_type')] == 'Company':
                    row[headers.index('company_classification')] = company_categories[members[member]['name'] + '///' + members[member]['country']]
                rows.append(row)
    except KeyError:
        pass



f = csv.writer(open('data/nazca_group.csv', 'w'))
f.writerow(headers)
for i in rows:
    f.writerow(i)
