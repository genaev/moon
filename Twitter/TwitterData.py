import urllib           # navigate to web page, get html data
from json import loads  # deserialise the html data for cleaning / parsing
import pandas as pd     # analysing and aggregating the data
import urllib.request

class TwitterData():
    def __init__(self, url):
        self.url = "https://socialblade.com/twitter/user/" + url + "/monthly"

    def get_script_text(self):
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
        except:
            print("*** WARNING: URL " + self.url + " did not open successfully. ***")
        return html

    def retrieve_data(self, html, data_type):
        """
        Find the part of the html with the total number of subscribers over time.

        Parameters:
            - html, a single string containing all the html in the page.
        Return a string containing all the subscriber data, or None if
            'total-subscribers' can't be found in the html for any reason
        """

        #Example:
        #from page https://socialblade.com/twitter/user/teamgameunits/monthly
        #"Date,Total Follower\n" + "2017-01-25,104276\n" +"2017-01-26,102157\n" +"
        #
        #from page https://socialblade.com/twitter/user/teamgameunits
        #from page "Date,Monthly Follower\n" + "2018-02-01,-4733\n" +"2018-01-01,958\n" +"2017-12-01,-547\n"



        #search_string = "\"Date,Monthly Follower\\n\" + "
        search_string = "\"Date,"+data_type+"\\n\" + "

        # In the html, the subscriber info is an array of Javascript objects (or a list
        # of python dicts), but extracted here as a single long string.
        start = html.find(search_string)
        # make sure the search string exists
        if start != -1:
            end = html.find(' , {', start)
            if end != -1:
                return html[start+len(search_string):end]
        else:
            return None

    def convert_text_to_dataframe(self, data_list, col_name):
        """
        Convert the string of subscriber data to a pandas dataframe (via JSON).

        Parameters:
            - data_list, a string containing the total-subscribers JSON
        Returns a pandas dataframe containing subscriber counts per day (as
        a date object)
        :rtype: pandas.core.frame.DataFrame
        """
        # clean up the fields
        data_list = data_list.replace("\\n\" +", "}\n")
        data_list = data_list.replace("\\n\"", "}\n")
        data_list = data_list.replace('"', '{"date": "')
        data_list = data_list.replace(',', '", "'+col_name+'": ')
        data_list = data_list.replace('}', '},')
        data_list = data_list[:-2]+"\n"
        data_list = "[\n"+data_list+"]\n";
        #{"date": "2018-01-10", "subscriber_count": 749769}
        # convert the string to a list of python dicts
        try:
            subscriber_data = loads(data_list)
        except ValueError:
            print("*** Can't parse data for " + self.url + " data_type= " + col_name + " ***")
            return None

        # convert to dataframe and parse dates from string to 'date'
        df = pd.DataFrame(subscriber_data)
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")

        return df

    @property
    def get(self):
        """
        Run all the methods above, to get the data, parse it an return the averaged
        results. Return a dataframe with the averaged results if successful, or None
        if unsuccessful.
        """
        # get the html
        text = self.get_script_text()
        # find the part that corresponds to total subscribers to the subreddit
        if text is not None:
            d = {
                "Total Follower": "subscriber_count",
                "Daily Follower": "subscriber_daily",
            }
            df = pd.DataFrame()
            for data_type,col_name in d.items():
                data_list = self.retrieve_data(text, data_type)
                if data_list is not None:
                    if df.empty is True:
                        df = self.convert_text_to_dataframe(data_list, col_name)
                    else:
                        df_new = self.convert_text_to_dataframe(data_list, col_name)
                        if df_new is not None:
                            df = df.set_index('date').join(df_new.set_index('date'))
            return df.reset_index() if df.empty is not True else None
        return None
