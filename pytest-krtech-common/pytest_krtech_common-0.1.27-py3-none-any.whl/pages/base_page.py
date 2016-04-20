# coding=utf-8
import logging
import time

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait


class BasePage(object):
    def __init__(self, config):
        self.__config = config
        self.__name = None
        self.__by = None
        self.__locator = None
        self.__element = None
        self.__driver = None
        self.__element_wait = None
        self.__element_init_timeout = None

    @property
    def config(self):
        return self.__config

    @property
    def locator(self):
        return self.__locator

    @locator.setter
    def locator(self, value):
        self.__locator = value

    @property
    def by(self):
        return self.__by

    @by.setter
    def by(self, value):
        self.__by = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def driver(self):
        return self.config.driver

    @driver.setter
    def driver(self, value):
        self.__driver = value

    @property
    def element_wait(self):
        return self.config.element_wait

    @element_wait.setter
    def element_wait(self, value):
        self.__element_wait = value

    @property
    def element_init_timeout(self):
        return self.config.element_init_timeout

    @element_init_timeout.setter
    def element_init_timeout(self, value):
        self.__element_init_timeout = value

    def __getitem__(self):
        return self

    def __str__(self):
        return self.name

    @property
    def element(self):
        driver = self.config.driver
        timeout = int(self.config.element_wait)
        time.sleep(float(self.config.element_init_timeout))
        try:
            WebDriverWait(driver, timeout).until(lambda s: driver.find_element(self.by, self.locator))
            self.__element = self.config.driver.find_element(self.by, self.locator)
        except (TimeoutException, StaleElementReferenceException):
            logger = logging.getLogger("base_element_logger")
            logger.setLevel(logging.INFO)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            logger.warning(u"Page '" + self.name + "' located by " + self.by + "='" + self.locator
                           + "' cannot be not found at " + driver.current_url)
        return self.__element
