from nose.tools import (
    assert_raises,
    assert_is_none,
    )

try:
    import unittest.mock as mock
except ImportError:
    import  mock

mock_open = mock.mock_open
patch = mock.patch
MagicMock = mock.MagicMock
sentinel = mock.sentinel

from python_kemptech_api.utils import (
    validate_port,
    validate_ip,
    validate_protocol,
    )
from python_kemptech_api.exceptions import (
    ValidationError
    )


class Test_validate_port:

    def test_ok(self):
        assert_is_none(validate_port('22'))

    def test_non_integer(self):
        with assert_raises(ValidationError):
            validate_port('sds')

    def test_out_of_range(self):
        with assert_raises(ValidationError):
            validate_port(1000000)


class Test_validate_ip:

    def test_ok(self):
        assert_is_none(validate_ip('2.2.2.2'))
        assert_is_none(validate_ip('2001:cdba::3257:9652'))

    def test_invalid_str(self):
        with assert_raises(ValidationError):
            validate_ip('sds')

    def test_none(self):
        with assert_raises(ValidationError):
            validate_ip(None)


class Test_validate_protocol:

    def test_TCP(self):
        assert_is_none(validate_protocol('TCP'))

    def test_udp(self):
        assert_is_none(validate_protocol('udp'))

    def test_invalid(self):
        with assert_raises(ValidationError):
            validate_protocol('sds')
