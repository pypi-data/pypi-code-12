import sys
import traceback
import re
from unittest import TestCase

from pscore.core.Logger import Logger
from pscore.core.factories import WebDriverFactory
from pscore.core.finalizers import WebDriverFinalizer
from pscore.core.support.test_context import TestContext

"""
This module includes any required TestCase subclasses.  These are then subclassed by the consuming test classes
to inherit the setup and teardown hooks responsible for initiating driver instanstiation, finalization and any resulting
actions.
"""


class WebDriverTestCase(TestCase):
    """
    This is the default (and currently only!) option for hooking.

    Example:
        class TestFlightsSearch(WebDriverTestCase):
    """
    failureExceptions = AssertionError
    failureInfo = None
    test_context = TestContext()

    """
    AF Note:
    I think we need a way for a consumer to specify their own log package.
    We also need (somehow) to have a common implied contract so we can leave it up to duck typing.
    Should our TestLog class be a subclass of logging.Logger?
    """

    def sanitized_test_name(self):
        """
        This method sanitizes the testmethod name when using params in nose2 to match the log file name
        See https://gojira.skyscanner.net/browse/TAS-1189
        Returns
        -------

        """

        removable_group = "([^A-Za-z0-9':_\"])+"
        return re.sub(removable_group, '', self._testMethodName.split("\n")[0]).replace('\'', '_').replace("\n", "_")

    def setUp(self):
        """
        The setup hook.  This will be called before each individual test.
        If you wish to use custom capabilties, please do the following in your test case:

        class SimplePscoreTestCase(WebDriverTestCase):
        def setUp(self):
            self.custom_caps = caps
            super(SimplePscoreTestCase, self).setUp()
        """
        self.test_context.test_name = self.sanitized_test_name()
        try:
            caps = self.custom_caps
        except AttributeError:
            caps = None
        self.driver = WebDriverFactory.get(self.logger,self.test_context.test_name,
                                           test_context=self.test_context,
                                           custom_caps=caps)


    def tearDown(self):
        """
        The teardown hook.  This will be called after each individual test.
        """
        self.logger.info("Test Runner: Attempting to teardown.")
        self._execute_driver_teardown()

    def _execute_driver_teardown(self):
        try:
            WebDriverFinalizer.finalize(self.driver, self.has_failed(), self.logger, self.test_context)
        except Exception as e:
            pass

    def has_failed(self):
        """
        This method encapsulates (and illustrates how to) ascertain a test failure state.
        """
        return self.failureInfo is not None

    def run(self, result=None):
        """
        This is the over-ridden version of run(), to allow us to track if a test has failed.
        This allows us to then differentiate between passed and failed results in teardown.
        It should be agnostic to the execution environment, so equally applicable to local tests,
        grid tests, saucelabs tests, etc.
        """

        success = False
        orig_result = result
        self.logger = None

        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()

        self._resultForDoCleanups = result
        result.startTest(self)

        testMethod = getattr(self, self._testMethodName)

        try:
            try:
                self.sanitized_test_name()
                test_method = getattr(self, self._testMethodName)
            except Exception as e:
                return

            self.logger = Logger(self.sanitized_test_name())
            self.test_context.logger = self.logger

            # Set up the test
            self.logger.info("Test Runner: Running test setup: {0}".format(str(self)))

            try:
                self.setUp()
            except Exception as e:
                result.addFailure(self, sys.exc_info())
                raise e

            # Run the test

            try:
                self.logger.info("Test Runner: Running test: {0}".format(str(self)))
                test_method()

            except Exception as e:
                if hasattr(e, 'msg'):
                    reason = e.msg
                else:
                    reason = e

                result.addFailure(self, sys.exc_info())
                self._set_failure_info(exception_message=reason)
            else:
                success = True

            # Tear down the test

            try:
                self.logger.info('Test Runner: Tearing down test: {0}'.format(str(self)))
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                success = False
                result.addFailure(self, sys.exc_info())
                self._set_failure_info(str(e))
                self._execute_driver_teardown()

            cleanUpSuccess = self.doCleanups()
            success = success and cleanUpSuccess
            if success:
                result.addSuccess(self)

        except Exception as e:
            if self.logger is None:
                print("Failed to instantiate logger: {0}".format(str(e)))
            else:
                self.logger.error(traceback.format_exc())
        finally:
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

    def _set_failure_info(self, exception_message):
        self.test_context.error_message = exception_message
        self.failureInfo = sys.exc_info()
        self.logger.error(sys.exc_info())
        self.logger.error(traceback.format_exc())
