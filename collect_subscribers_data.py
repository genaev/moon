import pandas as pd     # analysing and aggregating the data
from Reddit.RedditData import RedditData
from Twitter.TwitterData import TwitterData
from CoinMarketCap.SocialLinks import SocialLinks
from CoinMarketCap.CoinsList import CoinsList
from time import sleep
import os.path

# set the delay between requests
wait_time = 1
#data_file = 'data.csv'
out_dir = "data"

def to_csv(data,csv_file):
    df = pd.DataFrame(data)
    if (df is not None and not df.empty):
        df.to_csv(csv_file)

def update_data (cur_data,new_data):
    cur_data['date'] = pd.to_datetime(cur_data['date'])
    new_data['date'] = pd.to_datetime(new_data['date'])
    cur_data.set_index('date', inplace=True)
    new_data.set_index('date', inplace=True)
    data = pd.concat([cur_data, new_data]).reset_index().sort_values(by=['date', 'subscriber_count']).drop_duplicates(
        subset=['date'], keep='first').reset_index(drop=True)
    return data


def download_by_coin(coin,out_dir,rewrite):
    l = SocialLinks("https://coinmarketcap.com/currencies/"+coin+"/")
      
    print(coin," reddit",l.reddit, " twitter",l.twitter)
    # reddit data downloading
    if l.reddit != None:
        rd = RedditData(l.reddit)
        rd_file = out_dir + '/' + coin + '.reddit.csv'
        if (os.path.isfile(rd_file) is True and os.path.isfile(rd_file) is not True):
            cur_data = pd.read_csv(rd_file,index_col="Unnamed: 0")
            new_data = rd.get
            data = update_data(cur_data,new_data)
            to_csv(data, rd_file)
            # print ("cur=", cur_data.head(), cur_data.shape )
            # print ("new=", new_data.head(), new_data.shape )
            # print ("data=", data.head(), data.shape, data.info() )
        else:
            to_csv(rd.get,rd_file)
            
    # twitter data downloading
    if l.twitter != None:
        tw_file = out_dir + '/' + coin + '.twitter.csv'
        tw_user = l.twitter
        tw = TwitterData(tw_user)
        if (os.path.isfile(tw_file) is True and rewrite is not True):
            cur_data = pd.read_csv(tw_file,index_col="Unnamed: 0")
            new_data = tw.get
            data = update_data(cur_data,new_data)
            to_csv(data, tw_file)
        else:
            to_csv(tw.get, tw_file)



# download data for several coin
#download_by_coin("zcash",out_dir,False)
#exit(0)

# download data for all coins
i = 0
#for coin in pd.read_csv(data_file).name:
for coin in CoinsList().get['coin_id'].tolist():
    i+=1
    download_by_coin(coin,out_dir,False)
    # Pause before next request, to avoid DoS'ing the website
    sleep(wait_time)
