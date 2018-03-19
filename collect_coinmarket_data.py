import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from CoinMarketCap.CoinsList import CoinsList

url = 'https://coinmarketcap.com/all/views/all/'
out_dir = "data"
wait_time = 2

def get_html(url):
    r = requests.get(url)
    return r.text

def main(url, name, csv_file):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    trs = soup.find('table').find_all('tr')
    data = []

    for tr in trs[1:]:
        a = list(map(lambda x: x.string.replace(',', ''), tr.find_all('td')))
        data.append(a)

    if (data is not None and len(data[0])==7):
        df = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Market Cap'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.to_csv(csv_file)

i = 0
for coin in CoinsList().get['coin_id'].tolist():
    i += 1
    print (i, coin)
    main('https://coinmarketcap.com/currencies/' + coin + '/historical-data/?start=20100101&end=20180305',
         coin,
         out_dir + '/' + coin + '.market.csv')
    sleep(wait_time)
