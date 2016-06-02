#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pytest

from pytest_selenium_pdiff import utils, settings, assertions, exceptions


def test_ensure_path_exists(tmpdir):
    path = os.path.join(str(tmpdir), 'subdir')

    assert os.path.exists(path) is False

    utils.ensure_path_exists(path)

    assert os.path.exists(path) is True


def test_assert_screenshot_matches(selenium, tmpdir):
    selenium.set_window_size(1200, 800)
    selenium.maximize_window()

    selenium.get('http://www.google.com')

    settings['SCREENSHOTS_PATH'] = str(tmpdir.join('screenshots/'))
    settings['PDIFF_PATH'] = str(tmpdir.join('pdiff/'))

    with pytest.raises(exceptions.MissingScreenshot):
        assertions.assert_screenshot_matches(selenium, 'testing')

    settings['ALLOW_SCREENSHOT_CAPTURE'] = True

    assertions.assert_screenshot_matches(selenium, 'testing')
    assert os.path.exists(os.path.join(settings['SCREENSHOTS_PATH'], 'testing.png')) is True

    with pytest.raises(exceptions.ScreenshotMismatch):
        selenium.get('http://www.google.com/robots.txt')
        assertions.assert_screenshot_matches(selenium, 'testing')

        assert os.path.exists(os.path.join(settings['PDIFF_PATH'], 'testing.diff.png')) is True
