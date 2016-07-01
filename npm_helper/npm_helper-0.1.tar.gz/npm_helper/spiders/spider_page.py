#!usr/bin/env python
import ssl
import re
from urllib import request, error
from bs4 import BeautifulSoup
from spider_threads.utils import message
from ..data import database_creator

ssl._create_default_https_context = ssl._create_unverified_context

NPM_URL = 'https://www.npmjs.com{url}'
GITHUB = 'https://github.com{github}'


class NpmPageSpider(object):
    def __init__(self, url):
        url = NPM_URL.format(url=url)
        self.headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11',
            'GET': url
        }
        self.url = url

    def request_page(self):
        print('fetch {}'.format(self.url))
        try:
            req = request.Request(self.url, headers=self.headers)
            response = request.urlopen(req).read().decode('UTF-8')
            soup = BeautifulSoup(response, 'lxml')
            self.fetch_page(soup)
        except (error.HTTPError, error.URLError, error.ContentTooShortError):
            message.error_message('http error or url error')
        except UnicodeEncodeError:
            message.error_message('encoding error')

    @staticmethod
    def fetch_page(soup):
        package = {}

        # fetch name & desc
        content = soup.find('div', attrs={"class": "content-column"})
        package_name_container = content.find('h1', attrs={"class": "package-name"})
        package_name = package_name_container.find('a').string.strip()
        package_desc = content.find('p', attrs={"class": "package-description"}).string.strip()
        package["name"] = package_name
        package["desc"] = package_desc[0:30:]

        # fetch sidebar info
        sidebar = soup.find('div', attrs={"class": "sidebar"})
        info_boxs = sidebar.find_all('ul', attrs={"class": "box"})
        if info_boxs:
            for index, info_box in enumerate(info_boxs):
                info_box_string = str(info_box)

                github_url = re.findall(r'>.*github.com(.*)</a>', info_box_string)
                if github_url:
                    package["github"] = GITHUB.format(github=github_url[0])
                monthly_download = re.search(r'monthly-downloads', info_box_string)
                if monthly_download:
                    downloads_number_container = info_box.find('strong', attrs={"class": "monthly-downloads"})
                    monthly_downloads = downloads_number_container.string.strip()
                    package["download"] = int(monthly_downloads)

        else:
            package["github"] = 'https://github.com/explore'
            package["download"] = 0

        database = database_creator()
        database.append_data(package)
