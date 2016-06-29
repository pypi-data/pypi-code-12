# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from marionette_driver.marionette import Marionette

TIMEOUT = 20


def pytest_addoption(parser):
    parser.addoption(
        '--bin',
        default='/Applications/Firefox.app/Contents/MacOS/firefox-bin',
        help='path for Firefox binary')
    parser.addoption(
        '--base-url',
        metavar='url',
        help='base url for the application under test.'
    )


@pytest.fixture(scope='session')
def base_url(request):
    """Return a base URL"""
    return request.config.getoption(
        'base_url') or 'https://www.yahoo.com'


@pytest.fixture
def marionette(request, timeout):
    """Return a marionette instance"""
    m = Marionette(bin=request.config.option.bin)
    m.start_session()
    m.set_prefs({'signon.rememberSignons': False})
    request.addfinalizer(m.delete_session)
    m.set_search_timeout(timeout)
    return m


@pytest.fixture
def timeout():
    """Return default timeout"""
    return TIMEOUT
