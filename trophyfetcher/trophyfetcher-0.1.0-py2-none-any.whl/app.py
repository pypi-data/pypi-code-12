# coding: utf-8

"""
    trophyfetcher.app
    ~~~~~~~~~~~~~~~~~

    This module implements a TrophyFetcher class used to fetch information
    from PSN public trophies.

    :copyright: (c) 2016 by Roberto Soares
    :license: MIT
"""

import signal
import os
import selenium.webdriver.support.expected_conditions as EC

from . import logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support.ui import WebDriverWait


class TrophyFetcher(object):
    """
    This class uses Selenium WebDriver API with PhantomJS to navigate through
    the trophies website.
    """

    def __init__(self):
        """
        Initializes the browser using the PhantomJS driver. Also creates an object
        that will serve as the browser waiting tool when pooling DOM elements.
        """

        #: Instance of a headless browser using PhantomJS.
        #: Do not change the window size to a very low resolution (e.g. default
        #: resolution), otherwise, it will fail to find some elements.
        #: The parameter being passed on to the PhantomJS constructor will
        #: disable the creation of a ghostdriver.log.
        self.browser = webdriver.PhantomJS(service_log_path=os.path.devnull)
        self.browser.set_window_size(1920, 1080)

        #: Browser will wait 30 seconds while trying to find an element on the
        #: page. If it fails, it will raise a TimeoutException.
        self.browser_wait = WebDriverWait(self.browser, 30)

        self.should_log = True

    def user_info(self, username):
        """
        Use this method to get the user's information through the PSN public trophies website.

        :param username: Any PSN's username.
        :return: Will return all user's information available on the PSN public trophies website, such as:
                 avatar url, level, level progress, total number of trophies, bronze trophies, silver trophies,
                 golden trophies, platinum trophies and information on all games played by the user, such as:
                 image url, platform, name, bronze trophies, silver trophies, golden trophies, platinum trophies
                 and progress.
        """

        user_info = {}

        self.browser.get('https://www.playstation.com/en-us/my/public-trophies/')

        search_area = self._get_search_bar()
        search_area.clear()
        search_area.send_keys(username)

        search_button = self._get_search_button()
        search_button.click()

        user_info['avatar_url'] = self._get_avatar_url()
        user_info['level'] = self._get_level()
        user_info['level_progress'] = self._get_level_progress()
        user_info['trophies'] = self._get_all_trophies()
        user_info['bronze_trophies'] = self._get_bronze_trophies()
        user_info['silver_trophies'] = self._get_silver_trophies()
        user_info['gold_trophies'] = self._get_gold_trophies()
        user_info['platinum_trophies'] = self._get_platinum_trophies()

        self._open_entire_page()

        user_info['games_info'] = self._get_games_info()

        #: Sending a signal to terminate subprocesses created by PhantomJS.
        #: Apparently, this memory leak does not occur if you install PhantomJS
        #: without npm, because browser.quit() should terminate all processes
        #: related to PhantomJS.
        self.browser.service.process.send_signal(signal.SIGTERM)
        self.browser.quit()

        return user_info

    def logging_option(self, should_log):
        """
        Use this method to change the logging option. True will enable it,
        False will disable it.

        :param should_log: Boolean that will determine the logging option.
        """

        self.should_log = should_log

    def _get_search_bar(self):
        """
        Gets lower search bar used to type user's username.

        :return: Search bar where username is typed.
        """

        return self._get_element_from_page(EC.presence_of_element_located, By.ID, 'trophiesId', 'Search area.')

    def _get_search_button(self):
        """
        Gets clickable button used to submit search request.

        :return: Button used to trigger search.
        """

        link_elements = self._get_element_from_page(EC.presence_of_all_elements_located, By.CSS_SELECTOR,
                                                    'div.float-list > a',
                                                    'Search button.')

        for a in link_elements:
            if 'usersearch' in a.get_attribute('onclick'):
                return a

    def _get_avatar_url(self):
        """
        Gets url that links to the user's avatar.

        :return: User's avatar.
        """

        avatar_img = self._get_element_from_page(EC.presence_of_element_located, By.CSS_SELECTOR,
                                                 'div.avatar-block > img',
                                                 'Avatar image.')
        return avatar_img.get_attribute('src')

    def _get_level(self):
        """
        Gets user's level.

        :return: User's level.
        """

        level_div = self._get_element_from_page(EC.presence_of_element_located, By.CSS_SELECTOR, 'div.level-num',
                                                'Level div.')
        return level_div.get_attribute('innerHTML')

    def _get_level_progress(self):
        """
        Gets user's level progress.

        :return: User's level progress.
        """

        level_progress_div = self._get_element_from_page(EC.presence_of_element_located, By.CSS_SELECTOR,
                                                         'div.level-percentage > span',
                                                         'Level progress div.')
        return level_progress_div.get_attribute('innerHTML')

    def _get_all_trophies(self):
        """
        Gets the total amount of trophies a user has.

        :return: All user's trophies.
        """

        trophies_div = self._get_element_from_page(EC.presence_of_element_located, By.CSS_SELECTOR, 'div.trophy-num',
                                                   'Trophies div.')
        return trophies_div.get_attribute('innerHTML')

    def _get_bronze_trophies(self):
        """
        Gets the total amount of bronze trophies a user has.

        :return: All user's bronze trophies.
        """

        bronze_div = self._get_element_from_page(EC.presence_of_element_located, By.CSS_SELECTOR, 'div.bronze-trophy',
                                                 'Bronze trophies div.')
        return bronze_div.get_attribute('innerHTML')

    def _get_silver_trophies(self):
        """
        Gets the total amount of silver trophies a user has.

        :return: All user's silver trophies.
        """

        silver_div = self._get_element_from_page(EC.presence_of_element_located, By.CSS_SELECTOR, 'div.silver-trophy',
                                                 'Silver trophies div.')
        return silver_div.get_attribute('innerHTML')

    def _get_gold_trophies(self):
        """
        Gets the total amount of gold trophies a user has.

        :return: All user's gold trophies.
        """

        gold_div = self._get_element_from_page(EC.presence_of_element_located, By.CSS_SELECTOR, 'div.gold-trophy',
                                               'Gold trophies div.')
        return gold_div.get_attribute('innerHTML')

    def _get_platinum_trophies(self):
        """
        Gets the total amount of platinum trophies a user has.

        :return: All user's platinum trophies.
        """

        platinum_div = self._get_element_from_page(EC.presence_of_element_located, By.CSS_SELECTOR,
                                                   'div.platinum-trophy',
                                                   'Platinum trophies div.')
        return platinum_div.get_attribute('innerHTML')

    def _get_more_button(self):
        """
        Gets the button named 'more' that loads more content on the page.

        :return: The button that loads more content on the page.
        """

        more_button = self._get_element_from_page(EC.element_to_be_clickable, By.CSS_SELECTOR, 'a.more-link',
                                                  'More button.')
        return more_button

    def _get_games_info(self):
        """
        Gets all information related to the games played by the user.

        :return: An array of maps containing information related to each game, such as: image url, platform, name,
                 bronze trophies, silver trophies, golden trophies, platinum trophies and progress.
        """

        games_info = []

        games_tiles = self._get_element_from_page(EC.presence_of_all_elements_located, By.CSS_SELECTOR,
                                                  'div.compete-tile > a',
                                                  'Games tiles.')

        for game_tile in games_tiles:
            game_info = {}

            game_info['img_url'] = game_tile.find_element_by_css_selector(
                'div.trophy-image > img').get_attribute('src')
            game_info['platform'] = game_tile.find_element_by_css_selector(
                'div.compete-tile-details > div.fixed-container > span').get_attribute('innerHTML')
            game_info['name'] = game_tile.find_element_by_css_selector(
                'div.compete-tile-details > div.fixed-container > h2').get_attribute('innerHTML')
            game_info['bronze_trophies'] = game_tile.find_element_by_css_selector(
                'div.compete-tile-details > ul.trophies.clearfix > li.bronze').get_attribute('innerHTML')
            game_info['silver_trophies'] = game_tile.find_element_by_css_selector(
                'div.compete-tile-details > ul.trophies.clearfix > li.silver').get_attribute('innerHTML')
            game_info['gold_trophies'] = game_tile.find_element_by_css_selector(
                'div.compete-tile-details > ul.trophies.clearfix > li.gold').get_attribute('innerHTML')
            game_info['platinum_trophies'] = game_tile.find_element_by_css_selector(
                'div.compete-tile-details > ul.trophies.clearfix > li.platinum').get_attribute('innerHTML')
            game_info['progress'] = game_tile.find_element_by_css_selector(
                'div.compete-tile-details > div.progress.clearfix > span').get_attribute('innerHTML')

            games_info.append(game_info)

        return games_info

    def _open_entire_page(self):
        """
        Clicks the 'more' button at the end of the page until it hides.
        """

        more_button = self._get_more_button()

        while True:
            try:
                more_button.click()
            except ElementNotVisibleException:
                break

    def _get_element_from_page(self, ec, by, selector, description):
        """
        Gets elements from the page based on its parameters.

        :param ec: selenium.webdriver.support.expected_conditions.
        :param by: selenium.webdriver.common.by.
        :param selector: The name used to locate the element on the page.
                         This parameter depends on the `by` parameter.
                         If it's `By.ID`, then `selector` should be the id
                         of the element, and so on.
        :param description: The description of the element. This will be used
                            in the log files, in case the search fails.
        :return: Element from the page, if it exists.
        """

        try:
            return self.browser_wait.until(ec((by, selector)))
        except TimeoutException:
            if self.should_log:
                logger.log('TimeoutException while searching for: ' + description)
            raise TimeoutException('Check your connection or try again later.')
