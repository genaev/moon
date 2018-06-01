import requests
import pandas as pd


class CoinsList():
    def __init__(self):
        self.df = None
        self.make_df()

    def make_df(self):
        link = 'https://api.coinmarketcap.com/v2/ticker/?start={}&structure=array'
        starts = [1 + i*100 for i in range(16)]
        cur_list = []
        for i in starts:
            data = requests.get(link.format(i)).json()
            for elem in data['data']:
                cur_list.append(elem)
        cur_list = pd.DataFrame(cur_list).set_index('rank')
        cur_list['price'] = cur_list.quotes.map(lambda x: x['USD']['price'])
        cur_list['volume_24h'] = cur_list.quotes.map(lambda x: x['USD']['volume_24h'])
        cur_list['market_cap'] = cur_list.quotes.map(lambda x: x['USD']['market_cap'])
        cur_list = cur_list.rename(columns={'name': 'coin_name', 'website_slug': 'coin_id', 'symbol': 'coin_symbol'})
        cur_list = cur_list[['coin_id', 'coin_symbol', 'coin_name', 'price', 'volume_24h', 'market_cap']]
        self.df = cur_list

    @property
    def get(self):
        return self.df
