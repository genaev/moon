import pandas as pd
import requests
import json

out_dir = "data"

def download(url,csv_file):
    request = requests.get(url)
    data = json.loads(request.text)
    df = pd.DataFrame()
    for col in data:
        if df.empty:
            df = pd.DataFrame(data[col], columns=['date', col])
        else:
            df = pd.merge(df, pd.DataFrame(data[col], columns=['date', col]), on=['date'])
    df['date'] = pd.to_datetime(df['date'], unit='ms').dt.round('1D')
    df.to_csv(csv_file)

download('https://graphs2.coinmarketcap.com/global/dominance/',        out_dir+'/'+'dominance.index.csv')
download('https://graphs2.coinmarketcap.com/global/marketcap-total/',  out_dir+'/'+'marketcap-total.index.csv')
download('https://graphs2.coinmarketcap.com/global/marketcap-altcoin/',out_dir+'/'+'marketcap-altcoin.index.csv')
