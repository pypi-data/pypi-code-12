import datetime
import re
import time
import urllib.robotparser
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from selenium import webdriver
from selenium.webdriver.common.proxy import *

from WebLurker.exception import NoBrowserError


class WebLurker:
    """
    Main class. Provides all the functions and the logic of a web spider
    """

    FIREFOX = "firefox"
    PHANTOMJS = "phantomjs"
    CHROME = "chrome"
    OPERA = "opera"
    SAFARI = "safari"
    __firefox_agent = "Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.1.3) Gecko/20091020 Ubuntu/10.04 (lucid) Firefox/4.0.1"
    __link_regex = re.compile(r'<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    __sitemap_regex = re.compile(r'Sitemap: (.*?\.xml)')  # Used in robots.txt to find sitemaps
    __sitemap_link_regex = re.compile(r'<loc>(.*?)</loc>')  # Used in finding urls in a sitemap
    __all_links = re.compile(r'(.*?)')

    def __init__(self, root_url, max_depth=0, delay=0, user_agent=__firefox_agent, follow_robotstxt=True,
                 url_pattern=__all_links,
                 cache=None, stayondomain=True, proxy=None):

        self.__session = requests.session()
        self.__proxy = proxy
        if self.__proxy:
            self.__session.proxies = {"http": self.__proxy, "https": self.__proxy}
        self.__session.headers.update({'User-Agent': user_agent})
        self.__browser = None
        self.__max_depth = max_depth
        self.__delayer = Delayer(delay)
        if type(root_url) is str:
            self.__root_urls = [root_url]
        else:
            self.__root_urls = list(root_url)
        self.__stay_on_domain = stayondomain
        self.__user_agent = user_agent
        self.__callback_function = None
        self.__seen = dict()
        self.__extracted_data = list()
        self.__url_pattern = url_pattern
        self.__cache = cache
        self.__follow_robotstxt = follow_robotstxt
        self.__pre_load_routine = None
        self.__post_load_routine = None

    def crawl(self, sitemap=False, num_retries=2):
        """
        Starts the crawling process, beginning with the root_url.
        """
        self.__seen = {}
        while self.__root_urls:
            current_root_url = self.__root_urls.pop()
            crawler_queue = [current_root_url]
            if self.__follow_robotstxt:
                robots_parser = self.get_robotstxt(current_root_url)
            if sitemap:
                sitemaps = self.get_sitemaps(current_root_url)
                # Check for sitemaps
                for sitemap in sitemaps:
                    crawler_queue.extend(self.parse_sitemap(sitemap))
            for link in crawler_queue:
                self.__seen[link] = 0

            while crawler_queue:
                url = crawler_queue.pop()
                depth = self.__seen[url]

                if self.__cache and url in self.__cache:
                    # checks if cached content is available

                    print("Using cache for url: ", url)
                    content = self.__cache[url]

                else:
                    self.__delayer.wait(url)
                    # Delays download

                    if (self.__follow_robotstxt and robots_parser.can_fetch(self.__user_agent,
                                                                          url)) or not self.__follow_robotstxt:
                        # checks if it's ok to start the download with the robots.txt directive.

                        content = self.download(url, num_retries=num_retries)
                    else:
                        print("Robots.txt prevented url from downloading. set follow_robotstxt to False: ", url)

                    if self.__cache:
                        # If a caching system is available use it to store the html in it
                        self.__cache[url] = content

                if self.__callback_function:
                    # calls extraction callback

                    result = self.__callback_function(content, depth)
                    if result is not None:
                        self.__extracted_data.append(result)

                if depth < self.__max_depth:

                    for link in self.get_links(content):

                        link = self.normalize_link(current_root_url, link)

                        if self.__url_pattern.findall(link) and link not in self.__seen:
                            self.__seen[link] = depth + 1
                            if link.startswith("http"):
                                if self.__stay_on_domain:
                                    if self.are_in_same_domain(url, link):
                                        crawler_queue.append(link)
                                else:
                                    crawler_queue.append(link)

    @staticmethod
    def get_robotstxt(url):
        """
        Gets and reads the robots.txt file in a page
        """
        robots_txt = urllib.robotparser.RobotFileParser()
        robots_txt.set_url(url)
        robots_txt.read()
        return robots_txt

    def get_sitemaps(self, root_url):
        """
        Gets sitemaps from robots.txt of a webpage
        """
        robots_url = self.normalize_link(root_url, '/robots.txt')
        robotstxt = self.download(robots_url)
        a = re.findall(self.__sitemap_regex, robotstxt)
        return list(a)

    def parse_sitemap(self, sitemap_url):
        """
        Searchs sitemap for links. If more sitemaps are found, they get parse.
        """
        sitemap_content = self.download(sitemap_url)
        links = list(re.findall(self.__sitemap_link_regex, sitemap_content))
        for link in links:
            if link.endswith('.xml'):
                # if for some reason a sitemap contains more sitemaps we gotta parse them, right?
                links.extend(self.parse_sitemap(link))
                links.remove(link)

        return links

    @staticmethod
    def normalize_link(root_url, link):
        """
        Normalizes link by adding domain and removing hash
        """
        link, _ = urldefrag(link)
        link = urljoin(root_url, link)
        return link

    @staticmethod
    def are_in_same_domain(url1, url2):
        """
        Checks if two url are in the same domain.
        """
        return urlparse(url1).netloc == urlparse(url2).netloc

    def download(self, url, num_retries=2):
        """
        Downloads html content from an url.
        If a browser is set, it waits until the browser has finished downloading the page.
        If not, it uses a simple request.
        """
        print("Downloading: " + url)
        if self.__browser:
            if self.__pre_load_routine:
                self.__pre_load_routine(self.__browser)

            self.__browser.get(url)

            if self.__post_load_routine:
                self.__post_load_routine(self.__browser)
            html = self.__browser.page_source
        else:
            try:
                response = self.__session.get(url)
                html = response.content
                if 500 <= response.status_code < 600 and num_retries:
                    print("Download error, retrying: " + url)
                    html = self.download(url, num_retries=num_retries - 1)
                if 'text/html' in response.headers['content-type']:
                    html = response.text
            except:
                html = self.download(url, num_retries=num_retries - 1)
        return html

    def get_links(self, html):
        """
        Returns all links from a html content
        """
        if type(html) is bytes:
            return []
        return self.__link_regex.findall(html)

    def get_session(self):
        """
        Returns the current session
        """
        return self.__session

    def get_web_driver(self):
        """
        Returns the web driver
        """
        return self.browser

    def get_root_urls(self):
        return self.__root_urls

    def get_visited_urls(self):
        return self.__seen

    def set_url_pattern(self, url_pattern):
        try:
            re.findall(url_pattern, "")
            self.__url_pattern = url_pattern
        except:
            raise TypeError("Url pattern must be a compiled regular expression")

    def set_cache_system(self, cache):
            self.__cache = cache

    def is_stay_on_domain(self):
        return self.__stay_on_domain

    def set_stay_on_domain(self, boolean):
        self.__stay_on_domain = boolean

    def set_pre_load_routine(self, function):
        if callable(function):
            self.__pre_load_routine = function
        else:
            raise TypeError("Function must be callable")

    def set_post_load_routine(self, function):
        if callable(function):
            self.__post_load_routine = function
        else:
            raise TypeError("Function must be callable")

    def use_browser(self, browser, path=None, pre_load_routine=None, post_load_routine=None):
        """
        Sets and initializes the web driver.
        If needed, provide a full path to the web driver.
        """
        if browser:
            try:
                if browser == self.FIREFOX:
                    if self.__proxy:
                        proxy = Proxy({
                            'proxyType': ProxyType.MANUAL,
                            'httpProxy': self.__proxy,
                            'ftpProxy': self.__proxy,
                            'sslProxy': self.__proxy,
                            'noProxy': ''
                        })
                        if path:
                            self.__browser = webdriver.Firefox(executable_path=path, proxy=proxy)
                        else:
                            self.__browser = webdriver.Firefox(proxy=proxy)
                    else:
                        if path:
                            self.__browser = webdriver.Firefox(executable_path=path)
                        else:
                            self.__browser = webdriver.Firefox()
                elif browser == self.CHROME:
                    if path:
                        self.__browser = webdriver.Chrome(executable_path=path)
                    else:
                        self.__browser = webdriver.Chrome()
                elif browser == self.PHANTOMJS:
                    if self.__proxy:
                        service_args = [
                            '--proxy=' + self.__proxy,
                            '--proxy-type=socks5',
                        ]
                        if path:
                            self.__browser = webdriver.PhantomJS(executable_path=path, service_args=service_args)
                        else:
                            self.__browser = webdriver.PhantomJS(service_args=service_args)
                    else:
                        if path:
                            self.__browser = webdriver.PhantomJS(executable_path=path)
                        else:
                            self.__browser = webdriver.PhantomJS()

                elif browser == self.OPERA:
                    if path:
                        self.__browser = webdriver.Opera(executable_path=path)
                    else:
                        self.__browser = webdriver.Opera()
                elif browser == self.SAFARI:
                    if path:
                        self.__browser = webdriver.Safari(executable_path=path)
                    else:
                        self.__browser = None
            except:
                self.__browser = None
                raise NoBrowserError("Browser cannot be found in path: \"" + path + "\"")
            self.__pre_load_routine = pre_load_routine
            self.__post_load_routine = post_load_routine
        else:
            self.browser = None

    def set_extraction_callback(self, callback_function, depth=None):
        """
        Sets the extraction callback
        """
        if callback_function:
            if isinstance(callback_function, Extractor):
                self.__callback_function = callback_function
            else:
                self.__callback_function = Extractor(callback_function=callback_function, depth=depth)

    def get_extracted_data(self):
        return self.__extracted_data

    def update_headers(self, values):
        """
        Updates headers' content
        """
        self.__session.headers.update(values)

    def flush_session(self):
        """
        Resets current session
        """
        self.__session = requests.session()
        if self.__proxy:
            self.__session.proxies = {"http": self.__proxy, "https": self.__proxy}


class Delayer:
    """
    Makes thread sleep if the last time it accessed the domain's url is greater than the delay in seconds set
    """

    def __init__(self, seconds):
        self.delay = seconds
        self.last_access_to_domains = {}

    def wait(self, url):
        """
        Called each time an url is about to being crawled
        """
        domain = urlparse(url).netloc
        if self.delay > 0:
            last_visited = self.last_access_to_domains.get(domain)
            if last_visited:
                sleep_time = self.delay - (datetime.datetime.now() - last_visited).total_seconds()
                if sleep_time > 0:
                    time.sleep(sleep_time)
        self.last_access_to_domains[domain] = datetime.datetime.now()


class Extractor:
    """
    Extracts data from html
    """

    def __init__(self, callback_function=None, depth=None):
        self.__callback = callback_function
        if type(depth) is int:
            depth = [depth]
        self.__depth = depth

    def set_callback(self, callback_function):
        """
        Sets a callback function
        """
        self.__callback = callback_function

    def change_depth(self, newdepth):
        """
        Changes depth in which the callback function will be called
        """
        if type(newdepth) is int:
            newdepth = [newdepth]
        self.__depth = newdepth

    def extract(self, html):
        """
        Extracts data from html
        """
        return self.__callback(html)

    def __call__(self, content, depth):
        if self.__depth is not None and depth in self.__depth:
            return self.__callback(content)
        elif self.__depth is None:
            return self.__callback(content)
        else:
            return None
