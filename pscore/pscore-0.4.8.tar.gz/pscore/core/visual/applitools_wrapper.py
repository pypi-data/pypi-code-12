# __author__ = 'craigsyme'
from pscore.config.test_configuration import TestConfiguration as Config
from applitools.eyes import Eyes
from applitools.eyes import MatchLevel
from applitools.errors import *
import datetime


class ApplitoolsWrapper(object):
    @staticmethod
    def visually_test_page(driver, test_name, application_name, match_level, test_context, time_out=None):
        """
        :param driver: EventFiringWebDriver instance
        :param test_name: string used to match against the applitools baseline test name
        :param application_name: The name of the area of the website or app name being tested (eg flights-day-view,
         car-hire, hotels).
        :param match_level: 'Exact' (don't use), 'Strict' smart pixel compare 'Layout2' for dynamic content
         The values are 10 more as applitools doesn't screen-shot the full viewport.
         Changing the values will result in a new baseline!
        :param test_context: the test context that is property of WebDriverTestCase needed to provide logging
        :param time_out: Applitools can wait until the page is in the state under test.  It does this by screen
         shoting the page and performing the compare N number of times till the timeout has elapsed.
         Strongly recommend that tests should take responsibility for ensuring the page is in the correct state
         before calling this method.
        :return: Tuple Boolean result and string if failed
        """
        result = (True, "")
        eyes = None
        start_time = datetime.datetime.now()
        try:
            eyes = ApplitoolsWrapper._setup_test(driver=driver, match_level=match_level, test_name=test_name,
                                                 application_name=application_name)
            eyes.check_window(test_name, specific_match_timeout=time_out)
            eyes.close()
        except TestFailedError as e:
            result = (False, e.message)
        except EyesError as e:
            result = (False, e.message)
        finally:
            if eyes is not None:
                eyes.abort_if_not_closed()
            elapsed_time = datetime.datetime.now() - start_time
            test_context.logger.debug("Finishing visual test: {0}, run time {1}".format(
                                      test_name, elapsed_time.total_seconds()))
        return result

    @staticmethod
    def visually_test_element(driver, element, test_name, tag, application_name,
                              match_level, test_context, time_out=None):
        """
        :param driver: EventFiringWebDriver instance
        :param element: Webelement of the part of the page that is to be tested (ensure it is displayed)
        :param test_name: string used to match against the applitools baseline test (must be unique).
        :param tag: the name of the region of the page being tested.  Test name will be a combo of this and test_name
        :param application_name: The name of the area of the website or app name being tested (eg flights-day-view,
         car-hire, hotels).
        :param application_name: The name of the area of the website or app name being tested (eg flights-day-view,
         car-hire, hotels).
        :param match_level: 'Exact' (don't use), 'Strict' smart pixel compare 'Layout2' for dynamic content
        :param test_context: the test context that is property of WebDriverTestCase needed to provide logging
        :param time_out: Applitools can wait until the page is in the state under test.  It does this by screen
         shoting the page and performing the compare N number of times till the timeout has elapsed.
         Strongly recommend that tests should take responsibility for ensuring the page is in the correct state
         before calling this method.
        :return: Tuple Boolean result and string if failed
        """
        result = (True, "")
        eyes = None
        start_time = datetime.datetime.now()
        try:
            eyes = ApplitoolsWrapper._setup_test(driver=driver, match_level=match_level, test_name=test_name,
                                                 application_name=application_name)
            eyes.check_region_by_element(element=element, tag=tag, specific_match_timeout=time_out)
            eyes.close()
        except TestFailedError as e:
            result = (False, e.message)
        except EyesError as e:
            result = (False, e.message)
        finally:
            if eyes is not None:
                eyes.abort_if_not_closed()
            elapsed_time = datetime.datetime.now() - start_time
            test_context.logger.debug("Finishing visual test: {0}, run time {1}".format(
                                      test_name, elapsed_time.total_seconds()))
        return result

    @staticmethod
    def visually_test_by_selector(driver, by, selector, test_name, tag, application_name,
                                  match_level, test_context, time_out=None):
        """
        :param driver: EventFiringWebDriver instance
        :param by: The webdriver.common.by (ID, XPATH etc)
        :param selector: The selector string applitools will call find_element upon (ensure it is displayed)
        :param test_name: string used to match against the applitools baseline test (must be unique).
        :param tag: the name of the region of the page being tested.  Test name will be a combo of this and test_name
        :param application_name: The name of the area of the website or app name being tested (eg flights-day-view,
         car-hire, hotels).
        :param match_level: 'Exact' (don't use), 'Strict' smart pixel compare 'Layout2' for dynamic content
        :param test_context: the test context that is property of WebDriverTestCase needed to provide logging
        :param time_out: Applitools can wait until the page is in the state under test.  It does this by screen
         shoting the page and performing the compare N number of times till the timeout has elapsed.
         Strongly recommend that tests should take responsibility for ensuring the page is in the correct state
         before calling this method.
        :return: Tuple Boolean result and string if failed
        """
        result = (True, "")
        eyes = None
        start_time = datetime.datetime.now()
        try:
            eyes = ApplitoolsWrapper._setup_test(driver=driver, match_level=match_level, test_name=test_name,
                                                 application_name=application_name)
            eyes.check_region_by_selector(by=by, value=selector, tag=tag, specific_match_timeout=time_out)
            eyes.close()
        except TestFailedError as e:
            result = (False, e.message)
        except EyesError as e:
            result = (False, e.message)
        finally:
            if eyes is not None:
                eyes.abort_if_not_closed()
            elapsed_time = datetime.datetime.now() - start_time
            test_context.logger.debug("Finishing visual test: {0}, run time {1}".format(
                                      test_name, elapsed_time.total_seconds()))
        return result

    @staticmethod
    def _setup_test(driver, match_level, test_name, application_name):
        if not Config.get_execution_environment() == 'sauce':
            raise TestFailedError("Applitools tests must be run on saucelabs as this is the only env that supports "
                                  "decent viewport sizes")
        eyes = Eyes()
        if eyes is None:
            raise TestFailedError("Fatal error: failed to construct eyes object in applitools_warpper._setup_test")
        eyes.api_key = Config.get_applitools_lic_key()
        browser_name = Config.get_browser().lower()
        eyes.match_level = ApplitoolsWrapper._check_match_level(match_level)

        if browser_name == 'chrome' or browser_name == 'firefox' or browser_name == 'ie':
            eyes.force_full_page_screenshot = True
            ApplitoolsWrapper._set_browser_size(driver=driver)

        test_name = test_name + "_" + browser_name
        eyes.open(driver=driver.wrapped_driver,
                  app_name=application_name,
                  test_name=test_name)
        return eyes

    @staticmethod
    def _set_browser_size(driver):
        error_msg = 'There must be a env.PSCORE_BROWSER_RESOLUTION for browser size which sets width '\
                                  'and height in the following format as an example: \'1280x1024\''
        browser_size = Config.get_browser_resolution()
        if browser_size is None:
            raise TestFailedError(error_msg)
        width_height_split = browser_size.split('x')
        if not len(width_height_split) == 2:
            raise TestFailedError(error_msg)
        driver.set_window_size(width_height_split[0], width_height_split[1])

    @staticmethod
    def _check_match_level(level):
        if level == MatchLevel.LAYOUT2 or \
           level == MatchLevel.LAYOUT or \
           level == MatchLevel.STRICT or \
           level == MatchLevel.CONTENT:
            return level
        else:
            raise TestFailedError("The requested match level must be one of the following: {}, {}, {}, {}".format(
                MatchLevel.LAYOUT2, level == MatchLevel.LAYOUT, level == MatchLevel.STRICT, level == MatchLevel.CONTENT
            ))
