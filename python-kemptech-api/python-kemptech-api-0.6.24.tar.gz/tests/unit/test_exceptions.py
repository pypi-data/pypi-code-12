from nose.tools import assert_equal, assert_raises

# handle py3 and py2 cases:
try:
    import unittest.mock as mock
except ImportError:
    import mock

patch = mock.patch
sentinel = mock.sentinel

import python_kemptech_api.exceptions as exceptions
from python_kemptech_api.utils import IS_PY3

class Test_get_api_exception_message:

    def setup(self):
        self.p_get_error_msg = patch.object(exceptions, 'get_error_msg')
        self.get_error_msg = self.p_get_error_msg.start()

    def teardown(self):
        self.p_get_error_msg.stop()

    def test_msg_str_is_xml_msg(self):
        self.get_error_msg.return_value = sentinel.err
        res = exceptions.get_api_exception_message('a message', 401, True)
        assert_equal(res, sentinel.err)

    def test_msg_str_not_xml_msg(self):
        res = exceptions.get_api_exception_message('a message', 401, False)
        assert_equal(res, 'a message')

    def test_msg_None_status_code_ok(self):
        for is_xml_msg in (True, False):
            res = exceptions.get_api_exception_message(None, 401, is_xml_msg)
            assert_equal(res, '401 Client Error: Authorization required.')

    def test_msg_None_status_code_fail(self):
        for is_xml_msg in (True, False):
            res = exceptions.get_api_exception_message(None, 450, is_xml_msg)
            assert_equal(res, 'An unknown error has occurred (450).')


class Test_get_parameter_message:

    def test_dict_input(self):
        lm = 'my-loadmaster'
        parameters = {'param': 'a', 'value': 'b'}
        msg = exceptions.get_parameter_message(lm, parameters)
        assert_equal(msg,'my-loadmaster failed to set a: b')

    def test_non_dict_input(self):
        lm = 'my-loadmaster'
        parameters = 23  # Not a dictionary
        msg = exceptions.get_parameter_message(lm, parameters)
        if IS_PY3:
            assert_equal(msg,"my-loadmaster failed to set 23 ('int' object is not subscriptable)")
        else:
            assert_equal(msg,"my-loadmaster failed to set 23 ('int' object has no attribute '__getitem__')")


class Test_MissingInfo:

    def test_call(self):
        with assert_raises(exceptions.MissingInfo) as err:
            raise exceptions.MissingInfo('avalue')
        expect = "My service is missing the parameter_name parameter 'avalue'"
        assert_equal(str(err.exception), expect)


class Test_status_code:

    def test_status_code_is_set(self):
        expected = 45
        try:
            raise exceptions.UnauthorizedAccessError("1.1.1.1", code=expected)
        except exceptions.UnauthorizedAccessError as e:
            actual = e.status_code
            assert_equal(expected, actual)
