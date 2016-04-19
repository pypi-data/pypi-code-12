from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class PSWait(object):
    def __init__(self, driver):
        self.driver = driver

    def _wait_until_visible(self, locator, timeout, message, is_visible):
        if message is None:
            message = "Could not find {} in {} seconds".format(str(locator), timeout)

        wait = WebDriverWait(self.driver, timeout)
        if is_visible:
            wait.until(EC.visibility_of_element_located(locator), message=message)
        else:
            wait.until(EC.invisibility_of_element_located(locator), message=message)

    def _wait_until_visible2(self, locator, timeout, is_visible):
        """

        A 'Wait until visible' implementation that suppresses exceptions

        Parameters
        ----------
        locator
        timeout
        is_visible

        Returns
        -------

        """
        wait = WebDriverWait(self.driver, timeout)

        try:
            if is_visible:
                wait.until(EC.visibility_of_element_located(locator))
            else:
                wait.until(EC.invisibility_of_element_located(locator))

            # At this point, either the element was found or an exception was raised
            return True
        except (NoSuchElementException, TimeoutException) as e:
            # Printing to stout as no access to logger instance
            print("Suppressing {} exception, item with locator {} not found in {} seconds".format(type(e).__name__,
                                                                                                  str(locator),
                                                                                                  timeout))
            return False

    def until_visible(self, locator, timeout=3, message=None):
        self._wait_until_visible(locator, timeout, message, True)

    def until_not_visible(self, locator, timeout=3, message=None):
        self._wait_until_visible(locator, timeout, message, False)

    def until_visible2(self, locator, timeout=3):
        """

        Parameters
        ----------
        timeout
        locator

        Returns
        -------
        bool

        """
        return self._wait_until_visible2(locator, timeout, True)

    def until_not_visible2(self, locator, timeout=3):
        """

        Parameters
        ----------
        locator
        timeout

        Returns
        -------
        bool

        """
        return self._wait_until_visible2(locator, timeout, False)
