import datetime
import re
import time
import urllib.robotparser
from urllib.parse import urljoin, urlparse

import requests
from selenium import webdriver

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
    __link_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    __all_links = re.compile('(.*?)')

    def __init__(self, root_url, depth=0, delay=0, user_agent=None, follow_robotstxt=True, url_pattern=__all_links):
        self.session = requests.session()
        self.session.headers.update({'User-Agent': user_agent})
        self.browser = None
        self.depth = depth
        self.delayer = Delayer(delay)
        self.root_url = root_url
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = self.__firefox_agent
        self.callback_function = None
        try:
            self.robot_parser = urllib.robotparser.RobotFileParser()
        except:
            self.robot_parser = None
        self.seen = set()
        self.extracted_data = list()
        self.url_pattern = url_pattern
        if not follow_robotstxt:
            self.robot_parser.can_fetch = lambda: True
        else:
            self.robot_parser.set_url(root_url)
            self.robot_parser.read()

    def crawl(self):
        """
        Starts the crawling process, beginning with the root_url.
        """
        crawler_queue = [self.root_url]
        self.seen.add(self.root_url)
        depth = 0
        while crawler_queue:
            url = crawler_queue.pop()
            self.delayer.wait(url)
            content = self.download(url)
            if self.callback_function:
                result = self.callback_function(content, depth)
                if result is not None:
                    self.extracted_data.append(result)
            if depth < self.depth:
                for link in self.get_links(content):
                    link = urljoin(self.root_url, link)
                    if self.url_pattern.findall(link) and link not in self.seen:
                        crawler_queue.append(link)
                        self.seen.add(link)
                depth += 1

    def download(self, url, num_retries=2):
        """
        Downloads html content from an url.
        If a browser is set, it waits until the browser has finished downloading the page.
        If not, it uses a simple request.
        """
        url = urljoin(self.root_url, url)
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
        if depth is not None and depth in self.__depth:
            return self.callback(content)
        elif self.__depth is None:
            return self.callback(content)
        else:
            return None
