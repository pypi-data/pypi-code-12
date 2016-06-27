from nose.tools import (
    assert_equal, assert_raises, assert_in,
    assert_is_instance
    )

# handle py3 and py2 cases:
try:
    import unittest.mock as mock
except ImportError:
    import mock

patch = mock.patch
sentinel = mock.sentinel

import python_kemptech_api.exceptions as exceptions
import python_kemptech_api.client as client
from python_kemptech_api.client import VirtualService, RealServer

ValidationError = exceptions.ValidationError


class Test_VirtualService:

    def setup(self):
        self.lm_info = {
            "endpoint": "https://bal:2fourall@1.1.1.1:443/access",
            "ip_address": "1.1.1.1",
        }
        self.vs = VirtualService(self.lm_info, "1.1.1.2")

    def test_init_with_no_endpoint(self):
        lm_info_with_no_endpoint = {"ip_address": "1.1.1.1"}
        VirtualService(self.lm_info, "1.1.1.2")
        with assert_raises(exceptions.VirtualServiceMissingLoadmasterInfo):
            VirtualService(lm_info_with_no_endpoint, "1.1.1.2")

    def test_init_with_no_ipaddress(self):
        lm_info_with_no_ip_address = {"endpoint": "https://bal:2fourall@1.1.1.1:443/access"}
        VirtualService(self.lm_info, "1.1.1.2")
        with assert_raises(exceptions.VirtualServiceMissingLoadmasterInfo):
            VirtualService(lm_info_with_no_ip_address, "1.1.1.2")

    def test_str(self):
        assert_equal(str(self.vs), "Virtual Service TCP 1.1.1.2:80 on "
                                   "LoadMaster 1.1.1.1")

    def test_get_base_parameters(self):
        base_params = self.vs._get_base_parameters()
        expected_params = {
            "vs": "1.1.1.2",
            "port": 80,
            "prot": "tcp",
        }
        assert_equal(base_params, expected_params)

        self.vs.index = 1
        base_params = self.vs._get_base_parameters()
        expected_params = {
            "vs": 1,
        }
        assert_equal(base_params, expected_params)

    def test_to_api_dict(self):
        actual = self.vs.to_api_dict()
        expected = {
            "vs": "1.1.1.2",
            "port": 80,
            "prot": "tcp",
        }
        assert_equal(actual, expected)

    def test_to_dict(self):
        self.vs._ignore = None
        actual = self.vs.to_dict()
        expected = {
            "endpoint": "https://bal:2fourall@1.1.1.1:443/access",
            "ip_address": "1.1.1.1",
            "vs": "1.1.1.2",
            "port": 80,
            "prot": "tcp",
            "subvs_entries": [],
            "real_servers": [],
            "prot": "tcp",
        }
        assert_equal(actual, expected)

class Test_get_real_servers:

    def setup(self):
        self.lm_info = {
            "endpoint": "https://bal:2fourall@1.1.1.1:443/access",
            "ip_address": "1.1.1.1",
        }
        self.vs = VirtualService(self.lm_info, "1.1.1.2")

    def test_data_exists(self):
        with patch.object(VirtualService, 'build_real_server') as build_real_server:
            with patch.object(client, 'get_data') as get_data:
                with patch.object(VirtualService, '_get'):
                    build_real_server.side_effect = sorted
                    get_data. return_value = {'Rs': ['ba', 'ed']}
                    res =  self.vs.get_real_servers()
        expected = [['a','b'], ['d','e']]
        assert_equal(res, expected)

    def test_no_data_exists(self):
        with patch.object(VirtualService, 'build_real_server') as build_real_server:
            with patch.object(client, 'get_data') as get_data:
                with patch.object(VirtualService, '_get'):
                    build_real_server.side_effect = sorted
                    get_data. return_value = {}
                    res =  self.vs.get_real_servers()
        expected = []
        assert_equal(res, expected)


class Test_get_real_server:

    def setup(self):
        self.lm_info = {
            "endpoint": "https://bal:2fourall@1.1.1.1:443/access",
            "ip_address": "1.1.1.1",
        }
        self.vs = VirtualService(self.lm_info, "1.1.1.2")

    def test_with_index_ok(self):
        with patch.object(VirtualService, 'build_real_server') as build_real_server:
            with patch.object(client, 'get_data'):
                with patch.object(VirtualService, '_get'):
                    self.vs.index = self
                    build_real_server.return_value = sentinel.rs
                    res =  self.vs.get_real_server('1.1.1.1', 80)
        assert_equal(res, sentinel.rs)

    def test_with_index_invalid_ip(self):
        with patch.object(VirtualService, 'build_real_server') as build_real_server:
            with patch.object(client, 'get_data'):
                with patch.object(VirtualService, '_get'):
                    self.vs.index = self
                    build_real_server.return_value = sentinel.rs
                    with assert_raises(ValidationError):
                        self.vs.get_real_server('junk', 80)

    def test_with_index_invalid_port(self):
        with patch.object(VirtualService, 'build_real_server') as build_real_server:
            with patch.object(client, 'get_data'):
                with patch.object(VirtualService, '_get'):
                    self.vs.index = self
                    build_real_server.return_value = sentinel.rs
                    with assert_raises(ValidationError):
                        self.vs.get_real_server('1.1.1.1', 'junk')

    def test_without_index_ok(self):
        with patch.object(VirtualService, 'build_real_server') as build_real_server:
            with patch.object(client, 'get_data'):
                with patch.object(VirtualService, '_get'):
                    self.vs.index = None
                    build_real_server.return_value = sentinel.rs
                    res =  self.vs.get_real_server('1.1.1.1', 80)
        assert_equal(res, sentinel.rs)

    def test_without_index_invalid_ip(self):
        with patch.object(VirtualService, 'build_real_server') as build_real_server:
            with patch.object(client, 'get_data'):
                with patch.object(VirtualService, '_get'):
                    self.vs.index = None
                    build_real_server.return_value = sentinel.rs
                    with assert_raises(ValidationError):
                        self.vs.get_real_server('junk', 80)

    def test_without_index_invalid_port(self):
        with patch.object(VirtualService, 'build_real_server') as build_real_server:
            with patch.object(client, 'get_data'):
                with patch.object(VirtualService, '_get'):
                    self.vs.index = None
                    build_real_server.return_value = sentinel.rs
                    with assert_raises(ValidationError):
                        self.vs.get_real_server('1.1.1.1., junk')


class Test_build_real_server:

    def setup(self):
        self.lm_info = {
            "endpoint": "https://bal:2fourall@1.1.1.1:443/access",
            "ip_address": "1.1.1.1",
        }
        self.vs = VirtualService(self.lm_info, "1.1.1.2")

    def test_no_Addr(self):
        server = {"Port": 80}
        with assert_raises(ValidationError) as err:
            self.vs.build_real_server(server)
        assert_in('Addr', str(err.exception))

    def test_no_Port(self):
        server = {"Addr": '1.1.1.1'}
        with assert_raises(ValidationError) as err:
            self.vs.build_real_server(server)
        assert_in('Port', str(err.exception))

    def test_ok(self):
        server = {"Addr": '1.1.1.1', "Port": 80}
        res = self.vs.build_real_server(server)
        assert_is_instance(res, RealServer)




