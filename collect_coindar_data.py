import pandas as pd
import re
import nltk
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import os.path
from CoinMarketCap.CoinsList import CoinsList


def tokenize_and_stem(text):
    stemmer = SnowballStemmer("english")
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems

def download_and_clust(url,csv_file,n_clust):
    #nltk.download('popular')
    df = pd.read_json(url)
    events = df.caption.tolist()

    tfidf_vectorizer = TfidfVectorizer(max_df=0.80, max_features=200,
                                     min_df=0.04, stop_words='english',
                                     use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))

    tfidf_matrix = tfidf_vectorizer.fit_transform(events) #fit the vectorizer to synopses
    print('Shape is ',tfidf_matrix.shape)
    if n_clust==0:
        #n_clust = tfidf_matrix.shape[1]
        n_clust = 9
    km = KMeans(n_clusters=n_clust)
    km.fit(tfidf_matrix)
    df['cluster'] = km.labels_.tolist()
    df.to_csv(csv_file)

def to_csv(data,csv_file):
    df = pd.DataFrame(data)
    if (df is not None and not df.empty):
        df.to_csv(csv_file)

url = 'https://coindar.org/api/v1/lastEvents'
coindar_csv_file = 'coindar_data.csv'
out_dir = 'data'

#if os.path.isfile(coindar_csv_file) is not True:
print('download and clust data')
download_and_clust(url,coindar_csv_file,0)
print('DONE')

event_df = pd.read_csv(coindar_csv_file)
coins_df = CoinsList().get
result = pd.merge(event_df, coins_df, how='inner', on=['coin_name','coin_symbol'])
#result = pd.merge(event_df, coins_df, how='inner', on=['coin_symbol'])
result = result.drop(result.columns[[0]],axis=1)
grouped = result.groupby('coin_id')
#print("KMeans results:\n",result.cluster.value_counts(normalize=True))
result.cluster = result.cluster.map({k: v for k, v in zip(result.cluster.value_counts(normalize=True).index, range(9))})
print("KMeans results:\n",result.cluster.value_counts(normalize=True))
print(len(grouped)," coins were found in the CoinDar events")
for name, group in grouped:
    group = group.reset_index(drop=True)
    group['public_date'] = pd.to_datetime(group['public_date'])
    group['start_date'] = pd.to_datetime(group['start_date'])
    group['end_date'] = pd.to_datetime(group['end_date'])
    group = group.sort_values(by='start_date')
    group = group.reset_index(drop=True)
    to_csv(group, out_dir + '/' + name + '.coindar.csv')


if os.path.isfile(coindar_csv_file) is not True:
    os.remove(coindar_csv_file)