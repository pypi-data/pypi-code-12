# coding=utf-8
import random

from krtech.elements.base_element import BaseElement


class List(object):
    def __init__(self, name, by, locator):
        self.__name = name
        self.__by = by
        self.__locator = locator
        self.__index = None
        self.__element = None
        self.__elements = None
        self.__config = None

    @property
    def element(self):
        return self.__element

    @element.setter
    def element(self, value):
        self.__element = value

    @property
    def elements(self):
        return self.__elements

    @elements.setter
    def elements(self, value):
        self.__elements = value

    @property
    def locator(self):
        return self.__locator

    @locator.setter
    def locator(self, value):
        self.__locator = value

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, value):
        self.__index = value

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

    def get_element_contains_text(self, text):
        for e in self.elements:
            if text.lower() in e.text.lower():
                self.element = e
                return self

    def get_element_by_text(self, text):
        for e in self.elements:
            if text.strip() == e.text.strip():
                self.element = e
                return self

    def get_element_by_attribute(self, attr, value):
        for e in self.elements:
            if e.get_attribute(attr) == value:
                self.element = e
                return self

    def get_element_by_index(self, index):
        if index < len(self.elements):
            self.element = self.elements[index]
            return self

    def __getitem__(self):
        return self

    def __str__(self):
        return self.name

    def __get__(self, obj, owner=None):
        self.config = obj.config
        driver = self.config.driver

        i = 1
        l = []
        for e in driver.find_elements(self.__by, self.__locator):
            ee = BaseElement(self.name, self.by, self.locator + "[" + str(i) + "]")
            setattr(ee, "element", e)
            setattr(ee, "config", self.config)
            setattr(ee, "text", e.text)
            l.append(ee)
            i += 1
        self.elements = l
        return self
