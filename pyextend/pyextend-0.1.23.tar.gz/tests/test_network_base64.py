# coding: utf-8
"""
    tests.test_network_base64
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend.network.test_network_base64  test case

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import pytest


def test_base64():
    from pyextend.network.base64 import safe_base64_decode

    assert b'abcd' == safe_base64_decode(b'YWJjZA=='), safe_base64_decode('YWJjZA==')
    assert b'abcd' == safe_base64_decode(b'YWJjZA'), safe_base64_decode('YWJjZA')
    assert b'abcde' == safe_base64_decode(b'YWJjZGU'), safe_base64_decode(b'YWJjZGU')

if __name__ == '__main__':
    pytest.main(__file__)
