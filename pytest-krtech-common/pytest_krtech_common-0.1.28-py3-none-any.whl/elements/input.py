# coding=utf-8
from selenium.webdriver.common.by import By

from krtech.elements.base_element import BaseElement


class Input(BaseElement):

    @property
    def label(self):
        return self.element.find_element(By.XPATH, ".//label")

    @property
    def error(self):
        return self.element.find_element(By.XPATH, ".//*[contains(@*,'error')][not(self::label)]")

    @property
    def input(self):
        return self.element.find_element(By.XPATH, ".//input")

    @property
    def value(self):
        return self.input.get_attribute('value')
