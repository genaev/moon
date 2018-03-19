import urllib           # navigate to web page, get html data

class SocialLinks():
    def __init__(self, url):
        self.url = url
        self.links = {'reddit': None, 'twitter': None}
        self.get_html_text()

    def get_html_text(self):
        """
        Open the web page. Print warning (and continue) if page doesn't open.
        Return the html from the page, or None if the page doesn't open.
        """
        html = None
        try:
            page = urllib.request.urlopen(self.url).read()
            html = page.decode("utf8")
            self.retrieve_data(html)
        except:
            print("*** WARNING: URL " + self.url + " did not open successfully. ***")

        return html

    def retrieve_data(self, html):
        #Try to find reddit link, for example
        #https://www.reddit.com/r/bitcoin.embed?limit=9
        str = 'oScript.src = "https://www.reddit.com/r/'
        start = html.find(str)
        # make sure the search string exists
        if start != -1:
            end = html.find(".embed", start)
            if end != -1:
                self.links['reddit'] = html[start + len(str):end]
        # Try to find twitter link, for example
        #"twitter-timeline" href="https://twitter.com/ethereumproject"
        str = '"twitter-timeline" href="https://twitter.com/'
        start = html.find(str)
        if start != -1:
            end = html.find('"', start+len(str))
            if end != -1:
                self.links['twitter'] = html[start+len(str):end]

    @property
    def twitter(self):
        return self.links['twitter']

    @property
    def reddit(self):
        return self.links['reddit']
