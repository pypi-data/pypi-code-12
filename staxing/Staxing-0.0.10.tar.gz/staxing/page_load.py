"""
Wait for page load in Selenium.

credit to Tommy Beadle for the solution and
http://www.obeythetestinggoat.com/
how-to-get-selenium-to-wait-for-page-load-after-a-click.html
"""

from contextlib import contextmanager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of


class SeleniumWait(object):
    """Wait for webpage load by watching for staleness."""

    def __init__(self, driver, wait):
        """Constructor."""
        self.browser = driver
        self.wait = wait

    @contextmanager
    def wait_for_page_load(self):
        """Delay progress until the new page is available."""
        old_page = self.browser.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.browser, self.wait).until(
            staleness_of(old_page)
        )
