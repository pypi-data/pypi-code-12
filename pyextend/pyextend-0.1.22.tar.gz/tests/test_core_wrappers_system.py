# coding: utf-8
"""
    tests.test_core_wrappers_system
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend.core.wrappers.system test case

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import pytest

import pyextend.core.wrappers.system as sys

_platform_name = 'Unknown'


def test_platform():
    @sys.platform(sys.WINDOWS)
    def _windows():
        global _platform_name
        _platform_name = sys.WINDOWS
        print('This code just print on Windows platform.')

    @sys.platform(sys.LINUX)
    def _linux():
        global _platform_name
        _platform_name = sys.LINUX
        print('This code just print on Linux platform.')

    @sys.platform(sys.UNIX_LIKE)
    def _unix_like():
        global _platform_name
        _platform_name = sys.UNIX_LIKE
        print('This code just print on Unix like platform.')

    _unix_like()
    _windows()
    _linux()

    import platform
    assert platform.system() in _platform_name

if __name__ == '__main__':
    pytest.main(__file__)
