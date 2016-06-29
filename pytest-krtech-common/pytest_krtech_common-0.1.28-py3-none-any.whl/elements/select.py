# coding = utf-8

from selenium.webdriver.support.ui import Select as Select_

from krtech.elements.base_element import BaseElement


class Select(BaseElement):

    @property
    def select(self):
        return Select_(self.element)
