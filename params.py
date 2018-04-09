from CoinMarketCap.CoinsList import CoinsList
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--N", type=int, help="forecast for N days")
parser.add_argument("-l", "--L", type=int, help="L days in the training set")
parser.add_argument("-w", "--W", type=int, help="move the window for W days in each step of the cycle")
args = parser.parse_args()

data_dir = 'data_test'

# будем делать прогноз на N дней
n = args.N if args.N else 30
# обучаться будем на выборке длины L
l = args.L if args.L else 50
# смещение окна будет W
w = args.W if args.W else 10
# не будем учитывать данные за первые R дней что бы избежать выбросов
r = 30

cur_names = CoinsList().get['coin_id'].tolist()

norm_all = False
norm_block = False
pumps = [1, 1.5, 2]

skip_colums = ['marketcap_altcoin_index_market_cap_by_available_supply',
               'marketcap_altcoin_index_volume_usd',
               'd_index_bitcoin-cash',
               'd_index_dash',
               'd_index_ethereum',
               'd_index_monero',
               'd_index_nem',
               'd_index_neo',
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
                     'twitter': ''}

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
                     'has_reddit': 0,
                     'twitter': 20,
                     'has_twitter': 0}