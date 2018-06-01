import requests
import pandas as pd

ClientID = '688_391odjriyji8c0cs4swwc048k0wossc400k4k0w4wc88cccowg'
ClientSecret = '31wfr7zct60w4og4swgk0488gk8kw080s8wggwc0o84gk484so'
API_URL = 'https://api.coinmarketcal.com/{}'

headers = {
    "accept": "application/json",
}


def get_access_token():
    params = {
        "grant_type": "client_credentials",
        "client_id": ClientID,
        "client_secret": ClientSecret
    }
    api_method = "oauth/v2/token"
    r = requests.get(API_URL.format(api_method), params=params, headers=headers)
    return r.json()['access_token']


def get_events_page(token, page):
    api_method = "v1/events"
    params = {
        "access_token": token,
        "showMetadata": "true",
        "page": page,
        "dateRangeStart": "01/01/2016",
        "dateRangeEnd": "30/05/2028",
        "max": 150
    }
    r = requests.get(API_URL.format(api_method), params=params, headers=headers)
    return r.json()


access_token = get_access_token()
first_page = get_events_page(access_token, 1)
records = first_page['records']
pages_number = first_page['_metadata']['page_count']
for i in range(1, pages_number):
    records.extend(get_events_page(access_token, i+1)['records'])


df = pd.DataFrame.from_dict(records)
coinmarketcal = {}
for index, row in df.iterrows():
    for coin in row.coins:
        for category in row.categories:
            d = {
                'categories': category['id'],
                'is_hot': row.is_hot,
                'created_date': row.created_date,
                'date': row.date_event
                }
            if coin['id'] not in coinmarketcal:
                coinmarketcal[coin['id']] = [d]
            else:
                coinmarketcal[coin['id']].append(d)

out = 'data/{}.coinmarketcal.csv'
for cur in coinmarketcal:
    pd.DataFrame(coinmarketcal[cur]).to_csv(out.format(cur))
