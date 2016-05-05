from nose.tools import (
    assert_equal, assert_raises, assert_true,
    assert_is_none, assert_not_in)

# handle py3 and py2 cases:
try:
    import unittest.mock as mock
except ImportError:
    import mock

patch = mock.patch
sentinel = mock.sentinel

import python_kemptech_api.client as client
from python_kemptech_api.client import LoadMaster, VirtualService
import python_kemptech_api.exceptions as exceptions


def  test_endpoint():
    lm = client.LoadMaster('ip', 'user', 'pw', 'port')
    expected = "https://user:pw@ip:port/access"
    assert_equal(expected, lm.endpoint)


def test_send_response_ok():
    with patch.object(client, 'is_successful') as is_successful:
        is_successful.return_value = True
        with patch.object(client, 'parse_to_dict') as parse_to_dict:
            client.send_response('any_response')
            assert_true(parse_to_dict.called)


def test_send_response_fail():
    with patch.object(client, 'is_successful') as is_successful:
        is_successful.return_value = False
        with patch.object(client, 'get_error_msg') as get_error_msg:
            get_error_msg.return_value = None
            with assert_raises(client.KempTechApiException):
                client.send_response('any_response')

def test_repr():
    lm = client.LoadMaster('192.168.0.1', 'user', 'pw', 432)
    assert_equal(str(lm), '192.168.0.1:432')


class Test_get_parameter:

    def setup(self):
        self.p_get = patch.object(client.LoadMaster, '_get')
        self.p_get.start()
        self.p_get_data_field = patch.object(client, 'get_data_field')
        self.get_data_field = self.p_get_data_field.start()

        self.lm = client.LoadMaster('ip', 'user', 'pw')

    def teardown(self):
        self.p_get.stop()
        self.p_get_data_field.stop()

    def test_dict(self):
        self.get_data_field.return_value = {'a': 'dict', 'b': 'day'}
        res = self.lm.get_parameter('a-param')
        assert_equal("a='dict'b='day'", res)


    def test_str(self):
        self.get_data_field.return_value = 'a string'
        res = self.lm.get_parameter('a-param')
        assert_equal('a string', res)


class Test_set_parameter:

    def setup(self):
        self.p_get = patch.object(client.LoadMaster, '_get')
        self.p_get.start()
        self.p_is_successful = patch.object(client, 'is_successful')
        self.is_successful = self.p_is_successful.start()

        self.lm = client.LoadMaster('ip', 'user', 'pw')

    def teardown(self):
        self.p_get.stop()
        self.p_is_successful.stop()

    def test_ok(self):
        self.is_successful.return_value = True
        res = self.lm.set_parameter('a', 'b')
        assert_is_none(res)

    def test_fail(self):
        self.is_successful.return_value = False
        with assert_raises(exceptions.LoadMasterParameterError):
            self.lm.set_parameter('a', 'b')


class Test_virtual_service_crud:

    def setup(self):
        self.lm = LoadMaster("1.1.1.1", "bal", "2fourall")

    def test_create_virtual_service_factory(self):
        vs = self.lm.create_virtual_service("1.1.1.2", 90, "tcp")
        assert_equal(isinstance(vs, VirtualService), True)


class Test_get_virtual_services:

    def setup(self):
        self.lm = LoadMaster("1.1.1.1", "bal", "2fourall")

    def test_data_exists(self):
        with patch.object(LoadMaster, 'build_virtual_service') as build_virtual_service:
            with patch.object(client, 'get_data') as get_data:
                with patch.object(LoadMaster, '_get'):
                    build_virtual_service.side_effect = sorted
                    get_data. return_value = {'VS': ['ba', 'ed']}
                    res =  self.lm.get_virtual_services()
        expected = [['a','b'], ['d','e']]
        assert_equal(res, expected)

    def test_no_data_exists(self):
        with patch.object(LoadMaster, 'build_virtual_service') as build_virtual_service:
            with patch.object(client, 'get_data') as get_data:
                with patch.object(LoadMaster, '_get'):
                    build_virtual_service.side_effect = sorted
                    get_data. return_value = {}
                    res =  self.lm.get_virtual_services()
        expected = []
        assert_equal(res, expected)

class Test_get_virtual_service:

    def setup(self):
        self.lm = LoadMaster("1.1.1.1", "bal", "2fourall")

    def test_with_index(self):
        with patch.object(LoadMaster, 'build_virtual_service') as build_virtual_service:
            with patch.object(client, 'get_data'):
                with patch.object(LoadMaster, '_get'):
                    build_virtual_service.return_value = sentinel.vs
                    res =  self.lm.get_virtual_service(index=12)
        assert_equal(res, sentinel.vs)

    def test_without_index(self):
        with patch.object(LoadMaster, 'build_virtual_service') as build_virtual_service:
            with patch.object(client, 'get_data'):
                with patch.object(LoadMaster, '_get'):
                    build_virtual_service.return_value = sentinel.vs
                    res =  self.lm.get_virtual_service(
                        address='1.1.1.1',
                        port=80,
                        protocol='tcp'
                        )
        assert_equal(res, sentinel.vs)


class Test_show_interface:

    def setup(self):
        self.lm = LoadMaster("1.1.1.1", "bal", "2fourall")

    def test_show_interface_when_id_is_nan(self):
        with assert_raises(exceptions.ValidationError):
            self.lm.show_interface("1")

    def test_show_interface(self):
        with patch.object(LoadMaster, "_get"):
            with patch.object(client, "get_data") as get_data:
                get_data.return_value = {"Interface": {"IPAddress": "10.154.190.110/16"}}
                interface = self.lm.show_interface(0)
                assert_equal(interface["IPAddress"], "10.154.190.110")
                assert_equal(interface["cidr"], "16")

    def test_show_interface_no_ip(self):
        with patch.object(LoadMaster, "_get") as _get:
            with patch.object(client, "get_data") as get_data:
                get_data.return_value = {"Interface": {"IPAddress": None}}
                interface = self.lm.show_interface(0)
                assert_equal(interface["IPAddress"], None)
                assert_not_in("cidr", interface)
