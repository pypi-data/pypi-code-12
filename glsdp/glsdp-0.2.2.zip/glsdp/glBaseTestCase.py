#!/usr/bin/python
# vim:fileencoding=utf-8
# Copyright (c) GlobalLogic.

__doc__ = "Module with the base class for tests"
__module__ = "glsdp"
__version__ = "0.2.1"
__author__ = "Damian Giebas"
__all__ = ["GLBaseTestCase"]

import unittest
from selenium import webdriver
from glHelper import GLHelper

class GLBaseTestCase(unittest.TestCase):
    """Base class for work on rec-global.com page
    Attributes:
        driverType - type of driver. For more look GLHelper.
        driverPath - path to selenium webdriver. If default set None.
        baseUrl - default Url to load after setup browser
    """

    driverType = GLHelper.CHROME
    driverPath = None
    baseUrl = "http://www.rec-global.com"

    def setUp(self):
        """Setup driver"""

        self.glBeforeSetUp()
        try:
            driverHandler = getattr(webdriver, self.driverType)
            if self.driverPath is None:
                self.driver = driverHandler()
            else:
                self.driver = driverHandler(self.driverPath)
        except AttributeError:
            raise AttributeError("{0} is unknown ".format(self.driverType))

        self.driver.maximize_window()
        self.driver.get(self.baseUrl)
        self.glAfterSetUp()

    def glBeforeSetUp(self):
        """Simple method for custom action before driver setup"""
        pass

    def glAfterSetUp(self):
        """Simple method for custom action after driver setup"""
        pass

    def glBeforeTearDown(self):
        """Simple method for cutom actions before tear down"""
        pass

    def glAfterTearDown(self):
        """Simple method for cutom actions after tear down"""
        pass

    def tearDown(self):
        """Close driver"""
        self.glBeforeTearDown()
        self.driver.close()
        self.driver = None
        self.glAfterTearDown()
