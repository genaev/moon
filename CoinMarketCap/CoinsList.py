import urllib           # navigate to web page, get html data
from bs4 import BeautifulSoup
import pandas as pd

class CoinsList():
    def __init__(self):
        self.url = 'https://coinmarketcap.com/coins/views/all/'
        self.df = pd.DataFrame(columns=['coin_id','coin_symbol','coin_name'])
        self.get_html_text()

    def get_html_text(self):
        """
        Open the web page. Print warning (and continue) if page doesn't open.
        Return the html from the page, or None if the page doesn't open.
        """
        html = None
        req = urllib.request.Request(
            self.url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        try:
            page = urllib.request.urlopen(req).read()
            html = page.decode("utf8")
            self.retrieve_data(html)
        except:
            print("*** WARNING: URL " + self.url + " did not open successfully. ***")

        return html

    def retrieve_data(self, html):
        soup = BeautifulSoup(html, 'lxml')
        tds = soup.find('table').find_all('td', class_='no-wrap currency-name')
        for td in tds:
            self.df = self.df.append(dict(zip(list(self.df), [
                td.find('a').get('href').split('/')[2], #link_name
                td.find('a').text, #cur_symbol
                td.find('a', class_='currency-name-container').text #cur_name
            ])), ignore_index=True)

    @property
    def get(self):
        return self.df
