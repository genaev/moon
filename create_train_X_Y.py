import pandas as pd     # analysing and aggregating the data
import os.path
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from params import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--N", type=int, help="forecast for N days")
parser.add_argument("-l", "--L", type=int, help="L days in the training set")
parser.add_argument("-w", "--W", type=int, help="move the window for W days in each step of the cycle")
args = parser.parse_args()

# будем делать прогноз на N дней
n = args.N if args.N else 30
# обучаться будем на выборке длины L
l = args.L if args.L else 90
# смещение окна будет W
w = args.W if args.W else 5
# не будем учитывать данные за первые R дней что бы избежать выбросов
r = 30

X = []
Y = []
clusters = set()
new_clusters = set()


def make_df(coin):
    market_f = data_dir + '/' + coin + '.market.csv'
    dindex_f = data_dir + '/' + 'dominance.index.csv'
    cap_index_f = data_dir + '/' + 'marketcap-total.index.csv'
    capaltcoin_index_f = data_dir + '/' + 'marketcap-altcoin.index.csv'
    reddit_f = data_dir + '/' + coin + '.reddit.csv'
    twitter_f = data_dir + '/' + coin + '.twitter.csv'
    coindar_f = data_dir + '/' + coin + '.coindar.csv'
    coinmarketcal_f = data_dir + '/' + coin + '.coinmarketcal.csv'

    if os.path.isfile(market_f):
        market = pd.read_csv(market_f, index_col='Unnamed: 0').rename(str.lower, axis='columns')
        market['volume'] = pd.to_numeric(market['volume'], errors='coerce')
        market['market cap'] = pd.to_numeric(market['market cap'], errors='coerce')
        market.date = pd.to_datetime(market.date).dt.date
        market = market.sort_values('date')

    if len(market) >= r + l:
        if os.path.isfile(cap_index_f):
            cap_index = pd.read_csv(cap_index_f, index_col='Unnamed: 0')
            cap_index.date = pd.to_datetime(cap_index.date).dt.date
            cap_index = cap_index.set_index('date').add_prefix('marketcap_total_index_')
            market = market.join(cap_index, on='date')

        if os.path.isfile(capaltcoin_index_f):
            capaltcoin_index = pd.read_csv(capaltcoin_index_f, index_col='Unnamed: 0')
            capaltcoin_index.date = pd.to_datetime(capaltcoin_index.date).dt.date
            capaltcoin_index = capaltcoin_index.set_index('date').add_prefix('marketcap_altcoin_index_')
            market = market.join(capaltcoin_index, on='date')

        if os.path.isfile(dindex_f):
            dindex = pd.read_csv(dindex_f, index_col='Unnamed: 0')
            dindex.date = pd.to_datetime(dindex.date).dt.date
            dindex = dindex.set_index('date').add_prefix('d_index_')
            market = market.join(dindex, on='date')

        if os.path.isfile(reddit_f):
            reddit = pd.read_csv(reddit_f, index_col='Unnamed: 0')
            reddit.date = pd.to_datetime(reddit.date).dt.date
            reddit = reddit.rename(index=str, columns={'subscriber_count': 'reddit', 'subscriber_daily': 'reddit_daily'}).set_index('date')
            market = market.join(reddit, on='date')
            has_reddit = 1
        else:
            market['reddit'] = 0
            market['reddit_daily'] = 0
            has_reddit = 0

        if os.path.isfile(twitter_f):
            twitter = pd.read_csv(twitter_f, index_col='Unnamed: 0')
            twitter.date = pd.to_datetime(twitter.date).dt.date
            twitter = twitter.rename(index=str, columns={'subscriber_count': 'twitter', 'subscriber_daily': 'twitter_daily'}).set_index('date')
            market = market.join(twitter, on='date')
            has_twitter = 1
        else:
            market['twitter'] = 0
            market['twitter_daily'] = 0
            has_twitter = 0

        coindar = pd.DataFrame()
        if os.path.isfile(coindar_f):
            coindar = pd.read_csv(coindar_f, index_col='Unnamed: 0')
            coindar = coindar.rename(index=str, columns={'start_date': 'date'})
            coindar.date = pd.to_datetime(coindar.date).dt.date
            coindar = coindar.set_index('date').cluster.sort_index()

        coinmarketcal = pd.DataFrame()
        if os.path.isfile(coinmarketcal_f):
            coinmarketcal = pd.read_csv(coinmarketcal_f, index_col='Unnamed: 0')
            coinmarketcal.date = pd.to_datetime(coinmarketcal.date).dt.date
            coinmarketcal = coinmarketcal.set_index('date').categories.sort_index()

        return market, coindar, has_twitter, has_reddit, coinmarketcal

    else:
        return False


def make_x_y(market, coindar, has_twitter, has_reddit, coinmarketcal):
    global clusters
    pumps_count = {i: 0 for i in pumps}
    unpumps_count = {i: 0 for i in unpumps}

    if not coindar.empty:
        new_clusters = set(coindar).difference(clusters)
        clusters = clusters.union(set(coindar))
        for cluster in new_clusters:
            for elem in Y:
                elem['past_events' + str(cluster)] = 0
                elem['future_events' + str(cluster)] = 0

    market = market.drop_duplicates(subset='date', keep='first')
    nan_filling(market)
    if norm_all:
        norm_market = norm(market, norm_all_params)
    else:
        norm_market = market

    ids_count = (len(market) - n - r - l) // w
    start = len(market) - n - l - w * ids_count - 1

    for i in range(ids_count + 1):
        end = start + l
        table_part = norm_market[start + 1:end + 1]
        table_part = table_part.assign(id=coin + str(ids_count - i)).assign(date=range(l))

        if not table_part.isnull().any().any():

            X.append(table_part)

            y = market.low[end: end + n].max() / np.mean([market.high.iloc[end], market.low.iloc[end]])
            uny = market.high[end: end + n].min() / np.mean([market.high.iloc[end], market.low.iloc[end]])
            y_elem = {'id': coin + str(ids_count - i),
                      'y': y,
                      'start': market.date.iloc[start],
                      'end': market.date.iloc[end],
                      'predicted': market.date.iloc[end + n],
                      'has_reddit': has_reddit,
                      'has_twitter': has_twitter,
                      'age': i,
                      'less_0.01': int(market.low[end] < 0.01),
                      'less_1': int(0.01 < market.low[end] < 1),
                      'less_100': int(1 < market.low[end] < 100),
                      'more_100': int(100 < market.low[end])
                      }
###############################################
            if not coindar.empty:
                future_events = coindar[y_elem['end']:y_elem['predicted']].value_counts()
                past_events = coindar[y_elem['start']:y_elem['end']].value_counts()
                for cluster in clusters:
                    if cluster in future_events:
                        y_elem['future_events' + str(cluster)] = future_events[cluster]
                    else:
                        y_elem['future_events' + str(cluster)] = 0

                    if cluster in past_events:
                        y_elem['past_events' + str(cluster)] = past_events[cluster]
                    else:
                        y_elem['past_events' + str(cluster)] = 0
            else:
                for cluster in clusters:
                    y_elem['future_events' + str(cluster)] = 0
                    y_elem['past_events' + str(cluster)] = 0

            for category in range(1, 16):
                y_elem['future_coinmarketcal' + str(category)] = 0
                y_elem['past_coinmarketcal' + str(category)] = 0
            if not coinmarketcal.empty:
                future_events = coinmarketcal[y_elem['end']:y_elem['predicted']].value_counts()
                past_events = coinmarketcal[y_elem['start']:y_elem['end']].value_counts()
                for category, count in future_events.iteritems():
                    y_elem['future_coinmarketcal' + str(category)] = count
                for category, count in past_events.iteritems():
                    y_elem['pust_coinmarketcal' + str(category)] = count


            for i in pumps:
                if y_elem['y'] > i:
                    pumps_count[i] += 1
                y_elem['pump' + str(i)] = pumps_count[i]
                y_elem['pump_p' + str(i)] = pumps_count[i] / (ids_count + 1)

            for i in unpumps:
                if uny < i:
                    unpumps_count[i] += 1
                y_elem['unpump' + str(i)] = unpumps_count[i]
                y_elem['unpump_p' + str(i)] = unpumps_count[i] / (ids_count + 1)

            months = set(market.date[end: end + n].map(lambda x: x.month))
            for month in range(1,13):
                if month in months:
                    y_elem['month' + str(month)] = 1
                else:
                    y_elem['month' + str(month)] = 0

            Y.append(y_elem)

        start += w


def nan_filling(df):
    for i in interpolate_params:
        if i in df:
            df[i] = df[i].interpolate(limit=interpolate_params[i], limit_direction='both')


def f_norm(df, norm_type):
    if norm_type == 'log':
        return np.log(df + 1)
    elif norm_type == 'ss':
        scaler = StandardScaler()
        scaler.fit(df.values.reshape(-1, 1).astype(np.float64))
        return scaler.transform(df)
    elif norm_type == 'mm':
        scaler = MinMaxScaler()
        scaler.fit(df.values.reshape(-1, 1).astype(np.float64))
        return scaler.transform(df)
    else:
        return df


def key_to_list(key):
    if type(key) is tuple:
        return list(key)
    else:
        return [key]


def norm(df, params):
    norm_df = df.copy()
    for columns, param in params.items():
        columns_list = key_to_list(columns)
        if set(columns_list).issubset(set(df)):
            norm_df[columns_list] = f_norm(df[columns_list], param)
        else:
            print(*columns_list, 'not in df')
    return norm_df


for coin in cur_names:
    dfs = make_df(coin)
    if dfs:
        print(coin)
        make_x_y(*dfs)

X = pd.concat(X, ignore_index=True)
Y = pd.DataFrame(Y)
p = '_N'+str(n)+'L'+str(l)+'W'+str(w)
Y.to_csv('Y'+p+'.csv', index=False)
X.drop(skip_colums,axis=1).to_csv('X'+p+'.csv', index=False)
