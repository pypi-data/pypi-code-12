#!/usr/bin/python
# vim:fileencoding=utf-8
# Copyright (c) GlobalLogic.

__doc__ = "Module with the class support timeouts for tests"
__module__ = "glsdp"
__version__ = "0.2.1"
__author__ = "Damian Giebas"
__all__ = ["GLWait"]

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

class GLWait(object):
    """Class with helpers for waiting"""

    @staticmethod
    def untilElementIsNotVisible(driver, timeout, by, locator):
        """Static method waiting while element is visible.
        Method return element which is visible."""

        return WebDriverWait(driver, timeout).until(
            expected_conditions.visibility_of_element_located((by, locator))
        )

    @staticmethod
    def untilElementIsVisible(driver, timeout, by, locator):
        """Static method waiting while element is visible"""

        WebDriverWait(driver, timeout).until_not(
            expected_conditions.visibility_of_element_located((by, locator))
        )

    @staticmethod
    def untilElementNotExist(driver, timeout, by, locator):
        """Static method waiting until element not exists"""

        return WebDriverWait(driver, timeout).until(
            expected_conditions.presence_of_element_located((by, locator))
        )

    @staticmethod
    def whilePageLoaderIsVisible(driver):
        """Static method waiting while pageloader is visible"""

        GLWait.untilElementIsVisible(driver, 10, By.XPATH,
            "//div[@id='pageloader']")
