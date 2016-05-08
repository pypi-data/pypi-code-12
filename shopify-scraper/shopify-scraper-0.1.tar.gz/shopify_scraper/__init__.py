from scraper import Scraper
import threading
from multiprocessing.dummy import Pool as ThreadPool

class ShopifyScraper(Scraper):

    def __init__(self, *args, **kwargs):
        Scraper.__init__(self, *args, **kwargs)
        self.shopify_app_handle = kwargs.get("shopify_app_handle", None)
        self.shopify_app_url = kwargs.get("shopify_app_url", None)
        self.tloc = threading.local()
        self.shop_urls = []

    def _get_url(self):
        if self.shopify_app_handle:
            return "https://apps.shopify.com/%s"%self.shopify_app_handle
        else:
            return self.shopify_app_url

    def extract_reviews(self):
        first_url = self._get_url()
        first_page = self.make_request(first_url)
        pages = first_page.xpath('//div[@class="pagination"]/a')
        pages_to_scrap = { first_url : {"html":first_page} }
        for page in pages:
            page_url = page.attrib["href"]
            if page_url not in pages_to_scrap:
                pages_to_scrap[page_url] = {"url": "https://apps.shopify.com%s"%page_url}

        def _extract_shop_urls(data):
            page_data = data[0]
            if not page_data:
                page_data = self.make_request(data[1])

            links = page_data.xpath('//a[@itemprop="author"]')
            self.shop_urls += [link.attrib["href"].replace("http://","").replace("https://","") for link in links]

        pool = ThreadPool(10)
        params = [ (data.get("html", None), data.get("url", None)) for page_url, data in pages_to_scrap.items() ]
        pool.map(_extract_shop_urls, params)

        return self.shop_urls



