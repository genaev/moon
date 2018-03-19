import pandas as pd     # analysing and aggregating the data
from Reddit.RedditData import RedditData
from Twitter.TwitterData import TwitterData
from CoinMarketCap.SocialLinks import SocialLinks
from CoinMarketCap.CoinsList import CoinsList
from time import sleep
import os.path

# set the delay between requests
wait_time = 2
data_file = 'data.csv'
out_dir = "data"

def to_csv(data,csv_file):
    df = pd.DataFrame(data)
    if (df is not None and not df.empty):
        df.to_csv(csv_file)

def download_by_coin(coin,out_dir,rewrite):
    l = SocialLinks("https://coinmarketcap.com/currencies/"+coin+"/")
    print(coin," reddit",l.reddit, " twitter",l.twitter)
    # reddit data downloading
    if l.reddit != None:
        if (os.path.isfile(out_dir + '/' + coin + '.reddit.csv') is not True or rewrite is True):
            rd = RedditData(l.reddit)
            to_csv(rd.get,out_dir + '/' + coin + '.reddit.csv')
    # twitter data downloading
    if l.twitter != None:
        if (os.path.isfile(out_dir + '/' + coin + '.twitter.csv') is not True or rewrite is True):
            tw = TwitterData(l.twitter)
            to_csv(tw.get, out_dir + '/' + coin + '.twitter.csv')

# download data for several coin
#download_by_coin("ethereum",out_dir,True)
#exit(0)

# download data for all coins
i = 0
#for coin in pd.read_csv(data_file).name:
for coin in CoinsList().get['coin_id'].tolist():
    i+=1
    download_by_coin(coin,out_dir,True)
    # Pause before next request, to avoid DoS'ing the website
    sleep(wait_time)

