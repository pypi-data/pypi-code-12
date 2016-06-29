# coding=utf-8
from krtech.elements.base_element import BaseElement


class Link(BaseElement):

    @property
    def href(self):
        return self.element.get_attribute('href')
