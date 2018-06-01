from CoinMarketCap.CoinsList import CoinsList
import argparse

data_dir = 'data'

cur_names = CoinsList().get['coin_id'].tolist()

norm_all = False
norm_block = False
pumps = [1, 1.5, 2]

unpumps = [1, 0.66, 0.5]

skip_colums = ['marketcap_altcoin_index_market_cap_by_available_supply',
               'marketcap_altcoin_index_volume_usd',
               'd_index_bitcoin-cash',
               'd_index_dash',
               'd_index_ethereum',
               'd_index_monero',
               'd_index_nem',
               'd_index_neo',
               'reddit',
               'reddit_daily',
]

norm_block_params = {('open', 'high', 'low', 'close'): 'ss',
                     'volume': '',
                     'market cap': '',
                     'marketcap_total_index_market_cap_by_available_supply': '',
                     'marketcap_total_index_volume_usd': '',
                     'marketcap_altcoin_index_market_cap_by_available_supply': '',
                     'marketcap_altcoin_index_volume_usd': '',
                     'd_index_bitcoin': '',
                     'd_index_bitcoin-cash': '',
                     'd_index_dash': '',
                     'd_index_ethereum': '',
                     'd_index_iota': '',
                     'd_index_litecoin': '',
                     'd_index_monero': '',
                     'd_index_nem': '',
                     'd_index_neo': '',
                     'd_index_others': '',
                     'd_index_ripple': '',
                     'reddit': '',
                     'reddit_daily': '',
                     'twitter': '',
                     'twitter_daily': '',
                     }

norm_all_params = {('open', 'high', 'low', 'close'): 'log',
                   'volume': 'log',
                   'market cap': 'log',
                   'marketcap_total_index_market_cap_by_available_supply': 'log',
                   'marketcap_total_index_volume_usd': 'log',
                   'marketcap_altcoin_index_market_cap_by_available_supply': 'log',
                   'marketcap_altcoin_index_volume_usd': 'log',
                   ('d_index_bitcoin','d_index_bitcoin-cash','d_index_dash','d_index_ethereum','d_index_iota','d_index_litecoin','d_index_monero','d_index_nem','d_index_neo','d_index_others','d_index_ripple'): 'ss',
                   'reddit': 'log',
                   'twitter': 'log'}

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
                     'reddit': 20,
                     'reddit_daily': 20,
                     'has_reddit': 0,
                     'twitter': 20,
                     'twitter_daily': 20,
                     'has_twitter': 0}
