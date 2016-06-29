# coding=utf-8

from krtech.elements.base_element import BaseElement


class Checkbox(BaseElement):

    def is_checked(self):
        return self.element.is_selected()
