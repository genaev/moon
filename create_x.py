import pandas as pd     # analysing and aggregating the data
import os.path
import numpy as np
from sklearn.preprocessing import StandardScaler
#from CoinMarketCap.CoinsList import CoinsList
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--N", type=int, help="forecast for N days")
parser.add_argument("-l", "--L", type=int, help="L days in the training set")
parser.add_argument("-w", "--W", type=int, help="move the window for W days in each step of the cycle")
args = parser.parse_args()

data_dir = 'data'

# будем делать прогноз на N дней
n = args.N if args.N else 30
# обучаться будем на выборке длины L
l = args.L if args.L else 30
# смещение окна будет W
w = args.W if args.W else 15
# не будем учитывать данные за первые R дней что бы избежать выбросов
r = 30

#f = open('cur_list')
#cur_names = eval(f.read())
#f.close()
#cur_names = CoinsList().get['coin_id'].tolist()

log_norm = False
norm_in_block = False
interpolate_params ={'date': 0,
                     'open': 1,
                     'high': 1,
                     'low': 1,
                     'close': 1,
                     'volume': 1,
                     'market cap': 1,
                     'marketcap_total_index_market_cap_by_available_supply': 1,
                     'marketcap_total_index_volume_usd': 1,
                     'marketcap_altcoin_index_market_cap_by_available_supply': 1,
                     'marketcap_altcoin_index_volume_usd': 1,
                     'd_index_bitcoin': 1,
                     'd_index_bitcoin-cash': 1,
                     'd_index_dash': 1,
                     'd_index_ethereum': 1,
                     'd_index_iota': 1,
                     'd_index_litecoin': 1,
                     'd_index_monero': 1,
                     'd_index_nem': 1,
                     'd_index_neo': 1,
                     'd_index_others': 1,
                     'd_index_ripple': 1,
                     'reddit': 5,
                     'has_reddit': 0,
                     'twitter': 5,
                     'has_twitter': 0}

table = []
Y = []


def nan_filling(df):
    for i in interpolate_params:
        df[i] = df[i].interpolate(limit=interpolate_params[i])


def norm_block(df):
    price = ['open', 'high', 'low', 'close']
    df[price] = StandardScaler().fit_transform(market[price])
    df['volume'] = StandardScaler().fit_transform(market['volume'])
    df['market cap'] = StandardScaler().fit_transform(market['market cap'])


def norm_all(df):
    normed_colums = ['open', 'high', 'low', 'close', 'volume', 'market cap']
    df[normed_colums] = np.log(df[normed_colums])


dindex_f = data_dir + '/' + 'dominance.index.csv'
cap_index_f = data_dir + '/' + 'marketcap-total.index.csv'
capaltcoin_index_f = data_dir + '/' + 'marketcap-altcoin.index.csv'

if os.path.isfile(cap_index_f):
    cap_index = pd.read_csv(cap_index_f, index_col='Unnamed: 0')
    cap_index.date = pd.to_datetime(cap_index.date).dt.date
    cap_index = cap_index.set_index('date').add_prefix('marketcap_total_index_')

if os.path.isfile(capaltcoin_index_f):
    capaltcoin_index = pd.read_csv(capaltcoin_index_f, index_col='Unnamed: 0')
    capaltcoin_index.date = pd.to_datetime(capaltcoin_index.date).dt.date
    capaltcoin_index = capaltcoin_index.set_index('date').add_prefix('marketcap_altcoin_index_')

if os.path.isfile(dindex_f):
    dindex = pd.read_csv(dindex_f, index_col='Unnamed: 0')
    dindex.date = pd.to_datetime(dindex.date).dt.date
    dindex = dindex.set_index('date').add_prefix('d_index_')


for coin in ['ethereum']:#cur_names:
    print(coin)
    reddit_f  = data_dir + '/' + coin + '.reddit.csv'
    twitter_f = data_dir + '/' + coin + '.twitter.csv'
    market_f  = data_dir + '/' + coin + '.market.csv'
    coindar_f = data_dir + '/' + coin + '.market.csv'

    if os.path.isfile(market_f):
        market = pd.read_csv(market_f, index_col='Unnamed: 0').rename(str.lower, axis='columns')
        market['volume'] = pd.to_numeric(market['volume'], errors='coerce')
        market['market cap'] = pd.to_numeric(market['market cap'], errors='coerce')
        market.date = pd.to_datetime(market.date).dt.date

        if os.path.isfile(cap_index_f):
            market = market.join(cap_index, on='date')

        if os.path.isfile(capaltcoin_index_f):
            market = market.join(capaltcoin_index, on='date')

        if os.path.isfile(dindex_f):
            market = market.join(dindex, on='date')

        if os.path.isfile(reddit_f):
            reddit = pd.read_csv(reddit_f, index_col='Unnamed: 0')
            reddit.date = pd.to_datetime(reddit.date).dt.date
            reddit = reddit.rename(index=str, columns={'subscriber_count': 'reddit'}).set_index('date')
            market = market.join(reddit, on='date')
            market['has_reddit'] = 1
        else:
            market['reddit'] = 0
            market['has_reddit'] = 0

        if os.path.isfile(twitter_f):
            twitter = pd.read_csv(twitter_f, index_col='Unnamed: 0')
            twitter.date = pd.to_datetime(twitter.date).dt.date
            twitter = twitter.rename(index=str, columns={'subscriber_count': 'twitter'}).set_index('date')
            market = market.join(twitter, on='date')
            market['has_twitter'] = 1
        else:
            market['twitter'] = 0
            market['has_twitter'] = 0

        market = market.drop_duplicates(subset='date', keep='first')

        nan_filling(market)
        if log_norm:
               norm_all()

        start = n
        ids_count = (len(market) - start - r - l) // w
        for i in range(ids_count):
            e = start + i * w
            s = start + i * w + l
            table_part = market[e: s]

            table_part = table_part.assign(id=coin+str(i)).assign(date=range(l))
            if norm_in_block:
                norm_block(table_part)

            if not table_part.isnull().any().any():
                table.append(table_part)

            y = market.low[e - n: e].max() / np.mean([market.high.iloc[e],market.low.iloc[e]])
            Y.append([coin + str(i), y, market.date.iloc[s], market.date.iloc[e]])

table = pd.concat(table, ignore_index=True)
Y = pd.DataFrame(Y, columns=['id', 'y', 'start', 'end'])

p = '_N'+str(n)+'L'+str(l)+'W'+str(w)
Y.to_csv('Y'+p+'.csv', index=False)
table.to_csv('X'+p+'.csv', index=False)

print(len(Y))

