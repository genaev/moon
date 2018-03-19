import pandas as pd     # analysing and aggregating the data
import numpy as np
import os.path
from datetime import datetime

# set the delay between requests
data_file = 'data.csv'
out_file = 'data_social.csv'
data_dir = "data"

start = datetime(2017, 1, 1)
end = datetime(2018, 2, 1)

rng = pd.date_range(start=start, end=end, freq='MS')

def header(rng):
    head = ['name', 'Reddit']
    head.extend([d.strftime('%Y-%m-%d') + '_RedditSubscribers' for d in rng])
    head.append('Twitter')
    head.extend([d.strftime('%Y-%m-%d') + '_TwitterSubscribers' for d in rng])
    return head

def make_array(rnd,file):
    row = []
    if os.path.isfile(file) is True:
        row.append(1)
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
        for date in rng:
            s = df[df['date'] == date]['subscriber_count']
            if not s.empty:
                row.append(s.item())
            else:
                row.append(0)
    else:
        row.append(0)
        row.extend([0]*len(rng))
    return row

df = pd.DataFrame(columns=header(rng))
for coin in pd.read_csv(data_file).name:
    row = [coin]
    rd_file = data_dir + '/' + coin + '.reddit.csv'
    row.extend(make_array(rng,rd_file))
    tw_file = data_dir + '/' + coin + '.twitter.csv'
    row.extend(make_array(rng, tw_file))
    df.loc[len(df)] = row

df.to_csv(out_file)
