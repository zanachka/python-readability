import urllib2

class UrlFetch():
    """
    A class for fetching URLs.  This provides a layer of abstraction that can
    be easily replaced for testing.
    """

    def urlread(self, url):
        return urllib2.urlopen(url).read()


class MockUrlFetch(UrlFetch):

    def __init__(self, urldict):
        self._urldict = urldict

    def urlread(self, url):
        path = self._urldict[url]
        with open(path, 'r') as f:
            return f.read()
