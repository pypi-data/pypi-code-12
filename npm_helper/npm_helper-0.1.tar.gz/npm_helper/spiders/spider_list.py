#!usr/bin/env python
import ssl
from urllib import request, error
from bs4 import BeautifulSoup
from spider_threads.utils import message

ssl._create_default_https_context = ssl._create_unverified_context


class NpmSearchSpider(object):
    def __init__(self, url):
        self.headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11',
            'GET': url
        }
        self.url = url

    def request_urls(self):
        search_result = list()
        print('fetch {}'.format(self.url))
        try:
            req = request.Request(self.url, headers=self.headers)
            response = request.urlopen(req).read().decode('UTF-8')
            soup = BeautifulSoup(response, 'lxml')
            search_result = self.fetch_urls(soup, search_result)
        except (error.HTTPError, error.URLError, error.ContentTooShortError):
            message.error_message('http error or url error')
        except UnicodeEncodeError:
            message.error_message('encoding error')
        finally:
            return search_result

    @staticmethod
    def fetch_urls(soup, search_result):
        search_result_container = soup.find('ul', attrs={"class": "search-results"})
        search_results = search_result_container.find_all('li')
        if search_results:
            for result in search_results:
                result_head = result.find('h3').find('a', attrs={"class": "name"})
                result_url = result_head.attrs["href"]
                search_result.append(result_url)
        return search_result
