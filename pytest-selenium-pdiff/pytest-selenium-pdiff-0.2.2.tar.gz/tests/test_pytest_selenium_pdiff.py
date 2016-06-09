#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pytest
import time

from selenium.webdriver.remote.webdriver import WebDriver

from pytest_selenium_pdiff import utils, settings, assertions, exceptions


def test_ensure_path_exists(tmpdir):
    path = os.path.join(str(tmpdir), 'subdir')

    assert os.path.exists(path) is False

    utils.ensure_path_exists(path)

    assert os.path.exists(path) is True


def test_assert_screenshot_matches(selenium: WebDriver, tmpdir):
    selenium.implicitly_wait(5)
    selenium.set_window_size(1200, 800)
    selenium.maximize_window()

    selenium.get('./tests/fixtures/page1.html')

    settings['SCREENSHOTS_PATH'] = str(tmpdir.join('screenshots/'))
    settings['PDIFF_PATH'] = str(tmpdir.join('pdiff/'))

    with pytest.raises(exceptions.MissingScreenshot):
        assertions.assert_screenshot_matches(selenium, 'testing')

    settings['ALLOW_SCREENSHOT_CAPTURE'] = True

    assertions.assert_screenshot_matches(selenium, 'testing')
    assert os.path.exists(os.path.join(settings['SCREENSHOTS_PATH'], 'testing.png')) is True

    with pytest.raises(exceptions.ScreenshotMismatch):
        selenium.get('./tests/fixtures/page1-changed.html')
        selenium.find_element_by_tag_name('body').text.index("It has a second paragraph.")
        assertions.assert_screenshot_matches(selenium, 'testing')

    captured_path = os.path.join(settings['PDIFF_PATH'], 'testing.captured.png')
    pdiff_path = os.path.join(settings['PDIFF_PATH'], 'testing.diff.png')

    assert os.path.exists(captured_path)
    assert os.path.exists(pdiff_path)
