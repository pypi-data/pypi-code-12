# coding: utf-8
"""
    tests.test_network_base64
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend.network.test_network_base64  test case

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import pytest


def test_b64decode_safe():
    from pyextend.network.encoding import b64decode_safe

    assert b'abcd' == b64decode_safe(b'YWJjZA=='), b64decode_safe('YWJjZA==')
    assert b'abcd' == b64decode_safe(b'YWJjZA'), b64decode_safe('YWJjZA')
    assert b'abcde' == b64decode_safe(b'YWJjZGU'), b64decode_safe(b'YWJjZGU')

if __name__ == '__main__':
    pytest.main(__file__)
