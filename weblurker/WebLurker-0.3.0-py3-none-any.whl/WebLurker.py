import datetime
import re
import time
import urllib.robotparser
from urllib.parse import urljoin, urlparse, urldefrag
from threading import Thread, Lock

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

    def __init__(self, root_url, max_depth=0, delay=0, n_threads=1,user_agent=__firefox_agent, follow_robotstxt=True,
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
        self.__root_urls = dict()
        if type(root_url) is str:
            self.__root_urls[0] = [root_url]
        else:
            self.__root_urls[0] = list(root_url)
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
        self.__n_threads = n_threads
        self.__browserpath = ""
        if n_threads > 20:
            print("WARNING!!!", "Trying to spawn too many threads!")

    def crawl(self, sitemap=False, num_retries=2):
        if sitemap:
            for url in self.__root_urls[0]:
                sitemaps = self.get_sitemaps(url)
                #Check for sitemaps
                for sitemap in sitemaps:
                    self.__root_urls[0].extend(self.parse_sitemap(sitemap))

        url_queue_lock = Lock()
        robotstxt_lock = Lock()
        self.__seen = []
        if self.__follow_robotstxt:
            parsers = {}
        else:
            parsers = False

        threads = list()

        def watchdog():
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)
                    t = thread.clone()
                    threads.append(t)
                    t.start()

        def extraction_callback_wrapper(data, depth):
            if self.__callback_function:
                result = self.__callback_function(data, depth)
                if result is not None:
                    self.__extracted_data.append(result)

        #TODO ADD CACHE
        print("[WebLurker]Crawling with ", self.__n_threads, "threads...")
        for i in range(self.__n_threads):
            d = Downloader(self.__root_urls, url_queue_lock, self.__max_depth, identifier="\t[WL Thread "+str(i)+"]", seen_urls=self.__seen,
                           extraction_callback=extraction_callback_wrapper, delayer=self.__delayer, robotstxtparsers=parsers,
                           on_pre_load=self.__pre_load_routine, on_post_load=self.__post_load_routine, proxy=self.__proxy,
                           browser=self.__browser, browser_path=self.__browserpath, session=self.__session, url_pattern=self.__url_pattern,
                           stay_on_domain=self.__stay_on_domain, thread_spawner=watchdog, robotstxtlock=robotstxt_lock, n_retries=num_retries,
                           cache=self.__cache)
            threads.append(d)
            d.start()
        try:
            for downloader in threads:
                if downloader.is_alive():
                    downloader.join()
            print("[WebLurker]Crawling ended (Visited", len(self.__seen), "links)")
        except KeyboardInterrupt:
            print("[WebLurker]Terminating...")
            for downloader in threads:
                downloader.stop()
            print("[WebLurker]Terminated")
            raise KeyboardInterrupt()


        #Spawning threads


    def get_sitemaps(self, root_url):
        """
        Gets sitemaps from robots.txt of a webpage
        """
        robots_url = Downloader.normalize_link(root_url, '/robots.txt') #TODO FIX
        robotstxt = self.__download(robots_url)
        a = re.findall(self.__sitemap_regex, robotstxt)
        return list(a)

    def parse_sitemap(self, sitemap_url):
        """
        Searchs sitemap for links. If more sitemaps are found, they get parse.
        """
        sitemap_content = self.__download(sitemap_url) #TODO FIX
        links = list(re.findall(self.__sitemap_link_regex, sitemap_content))
        for link in links:
            if link.endswith('.xml'):
                # if for some reason a sitemap contains more sitemaps we gotta parse them, right?
                links.extend(self.parse_sitemap(link))
                links.remove(link)

        return links

    def __download(self, url):
        responsetext = self.__session.get(url).text
        return responsetext
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

    @staticmethod
    def normalize_link(root_url, link):
        """
        Normalizes link by adding domain and removing hash
        """
        link, _ = urldefrag(link)
        link = urljoin(root_url, link)
        return link

    def get_links(self, html):
        """
        Returns all links from a html content
        """
        if type(html) is bytes:
            return []
        return self.__link_regex.findall(html)

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
        self.__browserpath = path
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


class Downloader(Thread):
    FIREFOX = "firefox"
    PHANTOMJS = "phantomjs"
    CHROME = "chrome"
    OPERA = "opera"
    SAFARI = "safari"
    __all_links = re.compile(r'(.*?)')
    __link_regex = re.compile(r'<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)

    def __init__(self, urls, lock, max_depth,n_retries=2 ,identifier="[WebLurker]", seen_urls=None, cache=None,
                 extraction_callback=None, delayer=None, robotstxtparsers=False,
                 on_pre_load=None, on_post_load=None, proxy=None, browser=None, browser_path=None, session=None,
                 url_pattern=__all_links,
                 stay_on_domain=True, thread_spawner=None, robotstxtlock=None):
        Thread.__init__(self)
        self.__urls = urls
        self.__id = identifier
        self.__on_pre_load = on_pre_load
        self.__on_post_load = on_post_load
        self.__cache = cache
        self.__url_queue_lock = lock
        self.__max_depth = max_depth
        self.__delayer = delayer
        self.__should_i_be_alive = True
        self.__robotstxtlock = robotstxtlock
        self.__robotstxtparsers = robotstxtparsers
        self.__n_retries = n_retries
        if robotstxtparsers is False:
            self.__polite = False
        else:
            self.__polite = True
        if not delayer:
            self.__delayer = Delayer(0)
        if seen_urls is None:
            self.__seen_urls = {}
        else:
            self.__seen_urls = seen_urls

        self.__proxy = proxy

        if browser:
            if type(browser) is str:
                self.use_browser(browser, path=browser_path)
            else:
                self.__browser = browser
        else:
            self.__browser = browser
        if not session:
            self.__session = requests.Session()
        else:
            self.__session = session

        self.__extraction_callback = extraction_callback
        self.__url_pattern = url_pattern
        self.__stay_on_domain = stay_on_domain
        self.__thread_spawner = thread_spawner

    def run(self):

        while self.__should_i_be_alive:
            try:
                self.__url_queue_lock.acquire()
                url = self.__get_url_from_queue()
                self.__url_queue_lock.release()
            except:
                url = None
                self.__url_queue_lock.release()
            if not url:
                break
            depth, url = url

            if self.__cache and url in self.__cache:
                downloaded_data = self.__cache[url]
            else:
                downloaded_data = self.download(url, num_retries=self.__n_retries)
                if self.__cache:
                    self.__cache[url] = downloaded_data

            if self.__extraction_callback:
                self.__extraction_callback(downloaded_data, depth)

            for link in self.get_links(downloaded_data):

                link = self.normalize_link(url, link)

                if self.__url_pattern.findall(link) and link not in self.__seen_urls:
                    self.__seen_urls.append(link)
                    if self.__stay_on_domain:
                        if self.are_in_same_domain(url, link):
                            if link.startswith("http"):
                                try:
                                    self.__url_queue_lock.acquire()
                                    self.__add_to_url_queue(depth + 1, link)
                                    self.__url_queue_lock.release()
                                except:
                                    self.__url_queue_lock.release()
                    else:
                        if link.startswith("http"):
                            try:
                                self.__url_queue_lock.acquire()
                                self.__add_to_url_queue(depth + 1, link)
                                self.__url_queue_lock.release()
                            except:
                                self.__url_queue_lock.release()
                    if self.__thread_spawner and self.__should_i_be_alive:
                        self.__thread_spawner()

    def getRobotsTxt(self, url):
        domain = urlparse(url).netloc
        if domain in self.__robotstxtparsers.keys():
            return self.__robotstxtparsers[domain]
        else:
            print(self.__id, "Downloading robots.txt from domain:", domain)
            robotstxtparser = urllib.robotparser.RobotFileParser(urljoin(domain, "robots.txt"))
            robotstxtparser.read()
            self.__robotstxtparsers[domain] = robotstxtparser
            return robotstxtparser

    def can_fetch(self, url):
        result = False
        try:
            self.__robotstxtlock.acquire()
            parser = self.getRobotsTxt(url)
            result = parser.can_fetch(self.__session.headers["User-agent"], url)
            self.__robotstxtlock.release()
        except:
            self.__robotstxtlock.release()
        return result



    @staticmethod
    def are_in_same_domain(url1, url2):
        """
        Checks if two url are in the same domain.
        """
        return urlparse(url1).netloc == urlparse(url2).netloc

    def get_links(self, html):
        """
        Returns all links from a html content
        """
        if type(html) is bytes:
            return []
        return self.__link_regex.findall(html)

    def clone(self):
        return Downloader(self.__urls, self.__url_queue_lock, self.__max_depth, identifier=self.__id,
                          seen_urls=self.__seen_urls,
                          cache=self.__cache, extraction_callback=self.__extraction_callback,
                          on_pre_load=self.__on_pre_load, on_post_load=self.__on_post_load, proxy=self.__proxy,
                          browser=self.__browser, session=self.__session, url_pattern=self.__url_pattern,
                          stay_on_domain=self.__stay_on_domain, thread_spawner=self.__thread_spawner,
                          delayer=self.__delayer, robotstxtparsers=self.__robotstxtparsers,
                          robotstxtlock=self.__robotstxtlock, n_retries=self.__n_retries)

    @staticmethod
    def normalize_link(root_url, link):
        """
        Normalizes link by adding domain and removing hash
        """
        link, _ = urldefrag(link)
        link = urljoin(root_url, link)
        return link

    def __get_url_from_queue(self):
        deepths = list(self.__urls.keys())
        deepths.sort()
        if deepths:
            for d in deepths:
                if d > self.__max_depth:
                    break
                if not self.__urls[d]:
                    self.__urls.pop(d, None)
                else:
                    return d, self.__urls[d].pop()
        else:
            return None

    def __add_to_url_queue(self, depth, url):
        if depth in self.__urls.keys() and url not in self.__urls.values():
            self.__urls[depth].append(url)
        else:
            self.__urls[depth] = list()
            self.__add_to_url_queue(depth, url)

    def download(self, url, num_retries=2):
        """
        Downloads html content from an url.
        If a browser is set, it waits until the browser has finished downloading the page.
        If not, it uses a simple request.
        """
        print(self.__id, "Downloading:", url)
        html = ""
        if self.__browser:
            try:
                if self.__on_pre_load:
                    self.__on_pre_load(self.__browser)

                self.__browser.get(url)

                if self.__on_post_load:
                    self.__on_post_load(self.__browser)
                html = self.__browser.page_source
            except:
                try:
                    self.__browser.close()
                except:
                    pass
                self.__browser = None
                html = self.download(url, num_retries=num_retries)
        else:
            if (self.__polite and self.can_fetch(url)) or not self.__polite:
                try:
                    response = self.__session.get(url)
                    html = response.content
                    if 500 <= response.status_code < 600 and num_retries:
                        print(self.__id, "Downloading error, retrying:", url)
                        html = self.download(url, num_retries=num_retries - 1)
                    if 'text/html' in response.headers['content-type']:
                        html = response.text
                except:
                    html = self.download(url, num_retries=num_retries - 1)
            else:
                print(self.__id, "Robots.txt from:", url, "prevented download. You may try disabling followrobotstxt")
        return html

    def use_browser(self, browser, path=None):
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
        else:
            self.__browser = None

    def stop(self):
        self.__should_i_be_alive = False


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
