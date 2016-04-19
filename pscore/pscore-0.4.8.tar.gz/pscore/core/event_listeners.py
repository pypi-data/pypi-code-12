from selenium.webdriver.support.abstract_event_listener import AbstractEventListener


class DefaultWebDriverEventListener(AbstractEventListener):
    logger = None

    def __init__(self, logger):
        self.logger = logger

    def on_exception(self, exception, driver):
        self.logger.info("Exception raised: " + str(exception))

    def before_click(self, element, driver):
        self.logger.info("Clicking element")

    def before_find(self, by, value, driver):
        self.logger.info("Locating element by " + str(by) + " " + str(value))