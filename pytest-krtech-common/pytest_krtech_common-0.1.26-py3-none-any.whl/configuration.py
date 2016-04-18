# coding=utf-8

from urllib.parse import urljoin
from allure.constants import AttachmentType
from selenium import webdriver
import allure
from selenium.webdriver import FirefoxProfile


class TestConfig:
    def __init__(self):
        self.__driver = None
        self.__base_url = "http://127.0.0.1"
        self.__element_wait = 5
        self.__page_load_timeout = 20
        self.__element_init_timeout = 0.1
        self.__mysqlhost = "127.0.0.1"
        self.__mysqluser = "root"
        self.__mysqlpassword = "toor"
        self.__mysqldb = "dbname"

    @property
    def driver(self):
        return self.__driver

    @driver.setter
    def driver(self, value):
        self.__driver = value

    @property
    def base_url(self):
        return self.__base_url

    @base_url.setter
    def base_url(self, value):
        self.__base_url = value

    @property
    def element_wait(self):
        return self.__element_wait

    @element_wait.setter
    def element_wait(self, value):
        self.__element_wait = int(value)

    @property
    def page_load_timeout(self):
        return self.__page_load_timeout

    @page_load_timeout.setter
    def page_load_timeout(self, value):
        self.__page_load_timeout = float(value)

    @property
    def element_init_timeout(self):
        return self.__element_init_timeout

    @element_init_timeout.setter
    def element_init_timeout(self, value):
        self.__element_init_timeout = float(value)

    @property
    def mysqlhost(self):
        return self.__mysqlhost

    @mysqlhost.setter
    def mysqlhost(self, value):
        self.__mysqlhost = value

    @property
    def mysqluser(self):
        return self.__mysqluser

    @mysqluser.setter
    def mysqluser(self, value):
        self.__mysqluser = value

    @property
    def mysqlpassword(self):
        return self.__mysqlpassword

    @mysqlpassword.setter
    def mysqlpassword(self, value):
        self.__mysqlpassword = value

    @property
    def mysqldb(self):
        return self.__mysqldb

    @mysqldb.setter
    def mysqldb(self, value):
        self.__mysqldb = value


class WebdriverWrapper(webdriver.Remote):
    def __init__(self, base, *args, **kwargs):
        self._base_url = base
        super(WebdriverWrapper, self).__init__(*args, **kwargs)

    def get(self, url='/'):
        url = urljoin(self._base_url, url)
        return super(WebdriverWrapper, self).get(url)


class ConftestOptions:
    def __init__(self, testconf):
        self.testconf = testconf

    def pytest_runtest_makereport(self, item, call, __multicall__):
        report = __multicall__.execute()

        if report.when in ('call', 'teardown') and report.failed:
            attrs = getattr(item, 'funcargs')
            if 'config' in attrs:
                driver = attrs['config'].driver
                allure.attach('screenshot', driver.get_screenshot_as_png(), type=AttachmentType.PNG)

        return report

    def pytest_addoption(self, parser):
        parser.addoption("--base_url", action="store", default=self.testconf.base_url)
        parser.addoption("--browser", action="store", default="firefox")
        parser.addoption("--element_wait", action="store", default=self.testconf.element_wait)
        parser.addoption("--page_load_timeout", action="store", default=self.testconf.page_load_timeout)
        parser.addoption("--element_init_timeout", action="store", default=self.testconf.element_init_timeout)
        return parser

    def config(self, request):
        fp = FirefoxProfile()
        fp.set_preference("browser.startup.homepage_override.mstone", "ignore")
        fp.set_preference("startup.homepage_welcome_url.additional",  "about:blank")

        driver_ = WebdriverWrapper(
            base=request.config.option.base_url,
            desired_capabilities={'browserName': request.config.option.browser},
            browser_profile=fp
        )

        driver_.maximize_window()
        driver_.set_page_load_timeout(request.config.option.page_load_timeout)

        self.testconf.driver = driver_
        self.testconf.base_url = request.config.option.base_url

        return self.testconf
