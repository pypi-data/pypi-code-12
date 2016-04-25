# coding: utf-8
"""
    tests.test_core_wrappers_timeout
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend.core.wrappers.singleton test case

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import pytest
import platform

PF = platform.system()

from pyextend.core.wrappers.timeout import timeout


def test_timeout():
    @timeout(2)
    def slowfunc(sleep_time):
        a = 1
        import time
        time.sleep(sleep_time)
        return a

    assert slowfunc(0) == 1
    assert slowfunc(1) == 1

    if PF == 'Windows':
        assert slowfunc(3) == 1
    else:
        assert slowfunc(3) is None
        assert slowfunc(10) is None

if __name__ == '__main__':
    pytest.main(__file__)
