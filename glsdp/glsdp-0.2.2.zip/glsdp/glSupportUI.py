#!/usr/bin/python
# vim:fileencoding=utf-8
# Copyright (c) GlobalLogic.

__doc__ = "Module with the support ui actions class for tests"
__module__ = "glsdp"
__version__ = "0.2.1"
__author__ = "Damian Giebas"
__all__ = ["GLSupportUI"]

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from glWait import GLWait

class GLSupportUI(object):
    """Helper class with methods for actions on REC Global page"""

    def __findElement(self, driver, by, locator):
        """Return element located using 'by' value with 'locator'"""

        return driver.find_element(by, locator)


    def __findElementByXPath(self, driver, xpath):
        """Get page element using XPath"""

        return self.__findElement(driver, By.XPATH, xpath)

    def __getMenuElement(self, driver, linkText):
        """Get element from top menu panel"""

        menuPanel = self.__findElementByXPath(driver,
            "//ul[@id='navigation-menu']")
        return menuPanel.find_element_by_link_text(linkText)

    def __getSubMenuElement(self, driver, linkText):
        """Get element from popup menu"""

        menuElement = GLWait.untilElementIsNotVisible(driver, 3, By.XPATH,
            "//ul[@class='dropdown-menu' and @style='display: block;']")
        return menuElement.find_element_by_link_text(linkText)

    def clickOnInputTypeButtonWithText(self, webElement, buttonText):
        """Method to click on submit button with text"""

        webElement.find_element_by_xpath(
            ".//input[@value='{}']".format(buttonText)).click()

    def clickOnSubMenuLink(self, driver, menuLinkText, subMenuLinkText):
        """Method to click on submenu in menu"""

        self.hoverOnTopMenuLink(driver, menuLinkText)
        self.__getSubMenuElement(driver, subMenuLinkText).click()

    def clickOnTopMenuLink(self, driver, linkText):
        """Click on top menu element"""

        self.__getMenuElement(driver, linkText).click()

    def findElementAndPutText(self, driver, by, locator, text):
        """Using selenium locator strategies"""
        element = self.__findElement(driver, by, locator)
        element.send_keys(text)

    def findPageHeader(self, driver, headerText):
        """Get page header title element"""

        return self.__findElementByXPath(driver,
            "//h1[text()='{}']".format(headerText))

    def focusOnElement(self, element):
        """Focus element"""

        element.send_keys(Keys.NULL)

    def getFormUsingAttrs(self, driver, formAttributes):
        """Function to return form handler
        Arguments:
            formAttributes - iterable object with dicts, with two elements.
            First element have keyword "attribute", second have keyword "value".
        """

        formXPathAttributes = []
        for attribute in formAttributes:
            formXPathAttributes.append(
                "@{attribute}='{value}'".format(**attribute))

        formXPath = "//form"
        if formXPathAttributes:
            formXPath += "[{}]"
            formXPath = formXPath.format(' and '.join(formXPathAttributes))

        return self.__findElementByXPath(driver, formXPath)

    def hoverOnTopMenuLink(self, driver, linkText):
        """Hover element on top menu"""

        element = self.__getMenuElement(driver, linkText)
        handler = ActionChains(driver).move_to_element(element)
        handler.perform()
