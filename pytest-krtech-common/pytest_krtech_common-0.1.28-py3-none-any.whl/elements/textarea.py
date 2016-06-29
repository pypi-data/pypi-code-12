# coding=utf-8
from selenium.webdriver.common.by import By

from krtech.elements.base_element import BaseElement


class Textarea(BaseElement):

    @property
    def label(self):
        return self.element.find_element(By.XPATH, ".//label")

    @property
    def error(self):
        return self.element.find_element(By.XPATH, ".//*[contains(@*,'error')][not(self::label)]")

    @property
    def textarea(self):
        return self.element.find_element(By.XPATH, ".//textarea")

    @property
    def value(self):
        return self.textarea.get_attribute('value')
