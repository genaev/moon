import pandas as pd     # analysing and aggregating the data
import os.path
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from params import *
import datetime

X = []
Y = []
clusters = set()
new_clusters = set()
pred = n
n = 0


def make_df(coin):
    market_f = data_dir + '/' + coin + '.market.csv'
    dindex_f = data_dir + '/' + 'dominance.index.csv'
    cap_index_f = data_dir + '/' + 'marketcap-total.index.csv'
    capaltcoin_index_f = data_dir + '/' + 'marketcap-altcoin.index.csv'
    reddit_f = data_dir + '/' + coin + '.reddit.csv'
    twitter_f = data_dir + '/' + coin + '.twitter.csv'
    coindar_f = data_dir + '/' + coin + '.coindar.csv'

    if os.path.isfile(market_f):
        market = pd.read_csv(market_f, index_col='Unnamed: 0').rename(str.lower, axis='columns')
        market['volume'] = pd.to_numeric(market['volume'], errors='coerce')
        market['market cap'] = pd.to_numeric(market['market cap'], errors='coerce')
        market.date = pd.to_datetime(market.date).dt.date
        market = market.sort_values('date')

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
            reddit = reddit.rename(index=str, columns={'subscriber_count': 'reddit'}).set_index('date')
            market = market.join(reddit, on='date')
            has_reddit = 1
        else:
            market['reddit'] = 0
            has_reddit = 0

        if os.path.isfile(twitter_f):
            twitter = pd.read_csv(twitter_f, index_col='Unnamed: 0')
            twitter.date = pd.to_datetime(twitter.date).dt.date
            twitter = twitter.rename(index=str, columns={'subscriber_count': 'twitter'}).set_index('date')
            market = market.join(twitter, on='date')
            has_twitter = 1
        else:
            market['twitter'] = 0
            has_twitter = 0

        if os.path.isfile(coindar_f):
            coindar = pd.read_csv(coindar_f, index_col='Unnamed: 0')
            coindar = coindar.rename(index=str, columns={'start_date': 'date'})
            coindar.date = pd.to_datetime(coindar.date).dt.date
            coindar = coindar.set_index('date').cluster.sort_index()
        else:
            coindar = pd.DataFrame()

        return market, coindar, has_twitter, has_reddit

    else:
        return False


def make_x_y(market, coindar, has_twitter, has_reddit):
    global clusters
    pumps_count = {i: 0 for i in pumps}

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
        table_part = norm_market[start+1:end+1]
        table_part = table_part[::-1]
        table_part = table_part.assign(id=coin + str(ids_count - i)).assign(date=range(l))

        if not table_part.isnull().any().any():

            x_elem = table_part

            if end + pred > len(market):
                y = market.low[end: end + pred].max() / np.mean([market.high.iloc[end], market.low.iloc[end]])
            else:
                y = np.nan

            y_elem = {'id': coin + str(ids_count - i),
                      'y': y,
                      'start': market.date.iloc[start],
                      'end': market.date.iloc[end],
                      'predicted': market.date.iloc[end] + datetime.timedelta(days=pred),
                      'has_reddit': has_reddit,
                      'has_twitter': has_twitter,
                      'age': i,
                      'less_0.01': int(market.low[end] < 0.01),
                      'less_1': int(0.01 < market.low[end] < 1),
                      'less_100': int(1 < market.low[end] < 100),
                      'more_100': int(100 < market.low[end])
                      }

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

            for i in pumps:
                if y_elem['y'] > i:
                    pumps_count[i] += 1
                    y_elem['pump' + str(i)] = pumps_count[i]
                    y_elem['pump_p' + str(i)] = pumps_count[i] / (ids_count + 1)
                else:
                    y_elem['pump' + str(i)] = pumps_count[i]
                    y_elem['pump_p' + str(i)] = pumps_count[i] / (ids_count + 1)
        start += w

    try:
        X.append(x_elem)
        Y.append(y_elem)
        print(' added ')
    except:
        print()


def nan_filling(df):
    for i in interpolate_params:
        if i in df:
            df[i] = df[i].interpolate(limit=interpolate_params[i])


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


#for coin in cur_names:
for coin in ["sagacoin","wanchain","bitcoin","eccoin","energycoin","ethereum","ixcoin","jewels","ripple"]:
    dfs = make_df(coin)

    if dfs:
        print(coin , end='')
        make_x_y(*dfs)

X = pd.concat(X, ignore_index=True)
Y = pd.DataFrame(Y)
p = '_N'+str(pred)+'L'+str(l)+'W'+str(w)
Y.to_csv('small_new_Y'+p+'.csv', index=False)
X.drop(skip_colums,axis=1).to_csv('small_new_X'+p+'.csv', index=False)
#