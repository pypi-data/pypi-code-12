# coding=utf-8
import logging
import time

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait


class BaseElement(object):
    def __init__(self, name, by, locator):
        self.__name = name
        self.__by = by
        self.__locator = locator
        self.__element = None
        self.__config = None
        self.__text = None

    @property
    def element(self):
        return self.__element

    @element.setter
    def element(self, value):
        self.__element = value

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
    def config(self):
        return self.__config

    @config.setter
    def config(self, value):
        self.__config = value

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        self.__text = value

    def __getitem__(self):
        return self

    def __str__(self):
        return self.name

    def __get__(self, obj, owner=None):
        self.config = obj.config
        self.element = obj.element

        driver = self.config.driver
        timeout = int(self.config.element_wait)
        time.sleep(float(obj.config.element_init_timeout))

        try:
            WebDriverWait(driver, timeout).until(lambda s: self.element.find_element(self.__by, self.__locator))
            self.__element = self.element.find_element(self.__by, self.__locator)
            self.text = self.__element.text
            return self
        except (TimeoutException, StaleElementReferenceException):
            self.__element = None
            logger = logging.getLogger("base_element_logger")
            logger.warning(u"\nElement '" + self.name + "' located by " + self.by + "='" + self.locator +
                           "' was not found on page " + driver.current_url)
            return self

    def click(self):
        self.element.click()

    def get_attribute(self, name):
        return self.element.get_attribute(name)

    def is_displayed(self):
        return self.element.is_displayed()

    def is_enabled(self):
        return self.element.is_enabled()
