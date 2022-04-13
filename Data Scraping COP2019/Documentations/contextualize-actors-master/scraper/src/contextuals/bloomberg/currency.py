import requests
from bs4 import BeautifulSoup

rates = {}

def scrape_rate(src_currency, out_currency):
    url = 'http://www.xe.com/currencyconverter/convert/?Amount=1&From={}&To={}'.format(src_currency, out_currency)
    page = BeautifulSoup(requests.get(url).content, 'lxml')
    amt = page.find('span', {'class': 'uccResultAmount'}).text.strip()
    amt = float(amt)

    rates[(src_currency, out_currency)] = amt

    return amt

def convert(src_currency, out_currency, amount, debug=False, return_success=True):
    identifier = (src_currency, out_currency)
    try:
        if identifier in rates:
            amount = rates[identifier] * amount
        else:
            rate = scrape_rate(src_currency, out_currency)
            amount = rate * amount
        success = True
    except Exception as e:
        success = False
        if debug:
            print('currency exception')
            print(e)

    if return_success: return (amount, success)
    else: return amount
