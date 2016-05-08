import mechanize
import cookielib
from lxml import etree
from StringIO import StringIO
import random

class Scraper(object):

    def __init__(self, *args, **kwargs):
        self.proxies = []
        self.max_tries = kwargs.get("max_tries", 1)

        if kwargs.get("proxies", None):
            self.proxies = kwargs["proxies"]
            self.proxy_user = kwargs.get("proxy_user", None)
            self.proxy_password = kwargs.get("proxy_password", None)
            self.last_proxy_used = 0

    def set_proxy(self, br, url):

        if self.proxies:

            next_proxy = random.choice(self.proxies)

            br.set_proxies({"http": next_proxy})
            if self.proxy_user and self.proxy_password:
                br.add_proxy_password(self.proxy_user, self.proxy_password)

            self.last_proxy_used += 1
            if self.last_proxy_used >= len(self.proxies):
                self.last_proxy_used = 0

    def make_request(self, url):

        br = mechanize.Browser()

        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)

        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)

        #logger = logging.getLogger("mechanize")
        #logger.addHandler(logging.StreamHandler(sys.stdout))
        #logger.setLevel(logging.INFO)

        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

        response = ""
        for x in range(0, self.max_tries):
            try:
                self.set_proxy(br, url)
                response = br.open(url,timeout=5).read()

                parser = etree.HTMLParser()
                return etree.parse(StringIO(response), parser)

            except Exception, e:
                print "Trying again %s, error: %s" % (url, e)
                continue

        return None
