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

        self.session = requests.session()
        self.proxy = proxy
        if self.proxy:
            self.session.proxies = {"http": self.proxy, "https": self.proxy}
        self.session.headers.update({'User-Agent': user_agent})
        self.browser = None
        self.max_depth = max_depth
        self.delayer = Delayer(delay)
        if type(root_url) is str:
            self.root_urls = [root_url]
        else:
            self.root_urls = list(root_url)
        self.depth_functions = {}
        self.stay_on_domain = stayondomain
        self.user_agent = self.__firefox_agent
        self.callback_function = None
        self.seen = dict()
        self.extracted_data = list()
        self.url_pattern = url_pattern
        self.cache = cache
        self.__depth_executed = list()
        self.follow_robotstxt = follow_robotstxt

    def crawl(self, sitemap=False):
        """
        Starts the crawling process, beginning with the root_url.
        """
        self.seen = {}
        while self.root_urls:
            current_root_url = self.root_urls.pop()
            crawler_queue = [current_root_url]

            if self.follow_robotstxt:
                robots_parser = self.get_robotstxt(current_root_url)
            if sitemap:
                sitemaps = self.get_sitemaps(current_root_url)
                # Check for sitemaps
                for sitemap in sitemaps:
                    crawler_queue.extend(self.parse_sitemap(sitemap))
            for link in crawler_queue:
                self.seen[link] = 0

            while crawler_queue:
                url = crawler_queue.pop()
                depth = self.seen[url]

                if self.cache and url in self.cache:
                    # checks if cached content is available

                    print("Using cache for url: ", url)
                    content = self.cache[url]

                else:
                    self.delayer.wait(url)
                    # Delays download

                    if (self.follow_robotstxt and robots_parser.can_fetch(self.user_agent, url)) or not self.follow_robotstxt:
                        # checks if it's ok to start the download with the robots.txt directive.

                        content = self.download(url)
                    else:
                        print("Robots.txt prevented url from downloading. set follow_robotstxt to False: ", url)

                    if self.cache:
                        # If a caching system is available use it to store the html in it
                        self.cache[url] = content
                        self.cache.save()

                if self.callback_function:
                    # calls extraction callback

                    result = self.callback_function(content, depth)
                    if result is not None:
                        self.extracted_data.append(result)

                if depth < self.max_depth:

                    for link in self.get_links(content):

                        link = self.normalize_link(current_root_url, link)

                        if self.url_pattern.findall(link) and link not in self.seen:
                            self.seen[link] = depth + 1
                            if link.startswith("http"):
                                if self.stay_on_domain:
                                    if self.are_in_same_domain(url, link):
                                        crawler_queue.append(link)
                                else:
                                    crawler_queue.append(link)
                    self.__execute_functions(depth)
            #if self.root_urls:
            #    self.crawl()


    def get_robotstxt(self, url):
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

    def normalize_link(self, root_url, link):
        """
        Normalizes link by adding domain and removing hash
        """
        link, _ = urldefrag(link)
        link = urljoin(root_url, link)
        return link

    def __execute_functions(self, depth):
        """
        Executes all functions on a determined depth. Called when depth has changed
        """
        if 'all' in self.depth_functions:
            for function in self.depth_functions['all']:
                function()
        if depth in self.depth_functions and depth not in self.__depth_executed:
            for function in self.depth_functions[depth]:
                function()
            self.__depth_executed.append(depth)

    def are_in_same_domain(self, url1, url2):
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
        if self.browser:
            self.browser.get(url)
            html = self.browser.page_source
        else:
            response = self.session.get(url)
            if 500 <= response.status_code < 600 and num_retries:
                print("Download error, retrying: " + url)
                self.download(url, num_retries=num_retries - 1)
            html = response.text
        return html

    def get_links(self, html):
        """
        Returns all links from a html content
        """
        return self.__link_regex.findall(html)

    def get_session(self):
        """
        Returns the current session
        """
        return self.session

    def get_web_driver(self):
        """
        Returns the web driver
        """
        return self.browser

    def use_browser(self, browser, path=None):
        """
        Sets and initializes the web driver.
        If needed, provide a full path to the web driver.
        """
        if browser:
            try:
                if browser == self.FIREFOX:
                    if self.proxy:
                        proxy = Proxy({
                            'proxyType': ProxyType.MANUAL,
                            'httpProxy': self.proxy,
                            'ftpProxy': self.proxy,
                            'sslProxy': self.proxy,
                            'noProxy': ''
                        })
                        if path:
                            self.browser = webdriver.Firefox(executable_path=path, proxy=proxy)
                        else:
                            self.browser = webdriver.Firefox(proxy=proxy)
                    else:
                        if path:
                            self.browser = webdriver.Firefox(executable_path=path)
                        else:
                            self.browser = webdriver.Firefox()
                elif browser == self.CHROME:
                    if path:
                        self.browser = webdriver.Chrome(executable_path=path)
                    else:
                        self.browser = webdriver.Chrome()
                elif browser == self.PHANTOMJS:
                    if self.proxy:
                        service_args = [
                            '--proxy=' + self.proxy,
                            '--proxy-type=socks5',
                        ]
                        if path:
                            self.browser = webdriver.PhantomJS(executable_path=path, service_args=service_args)
                        else:
                            self.browser = webdriver.PhantomJS(service_args=service_args)
                    else:
                        if path:
                            self.browser = webdriver.PhantomJS(executable_path=path)
                        else:
                            self.browser = webdriver.PhantomJS()

                elif browser == self.OPERA:
                    if path:
                        self.browser = webdriver.Opera(executable_path=path)
                    else:
                        self.browser = webdriver.Opera()
                elif browser == self.SAFARI:
                    if path:
                        self.browser = webdriver.Safari(executable_path=path)
                    else:
                        self.browser = None
            except:
                self.browser = None
                raise NoBrowserError("Browser cannot be found in path: \"" + path + "\"")
        else:
            self.browser = None

    def set_extraction_callback(self, callback_function, depth=None):
        """
        Sets the extraction callback
        """
        if callback_function:
            if isinstance(callback_function, Extractor):
                self.callback_function = callback_function
            else:
                self.callback_function = Extractor(callback_function=callback_function, depth=depth)

    def add_depth_change_callback(self, function, depth=None):
        """
        Executes functions when entering depth
        """
        if callable(function):
            if depth is None:
                if 'all' not in self.depth_functions:
                    self.depth_functions['all'] = list()
                self.depth_functions['all'].append(function)
            else:
                if type(depth) is int:
                    if depth not in self.depth_functions:
                        self.depth_functions[depth] = list()
                    self.depth_functions[depth].append(function)
                elif type(depth) is list:
                    for d in depth:
                        self.add_depth_change_callback(function, depth=d)
        else:
            raise AttributeError("Function must be callable")

    def update_headers(self, values):
        """
        Updates headers' content
        """
        self.session.headers.update(values)

    def flush_session(self):
        """
        Resets current session
        """
        self.session = requests.session()
        if self.proxy:
            self.session.proxies = {"http": self.proxy, "https": self.proxy}


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
        self.callback = callback_function
        if type(depth) is int:
            depth = [depth]
        self.__depth = depth

    def set_callback(self, callback_function):
        """
        Sets a callback function
        """
        self.callback = callback_function

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
        return self.callback(html)

    def __call__(self, content, depth):
        if self.__depth is not None and depth in self.__depth:
                return self.callback(content)
        elif self.__depth is None:
            return self.callback(content)
        else:
            return None
