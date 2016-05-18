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
                    def sorted_wrap(kwargs, arbitrary):
                        return sorted(kwargs)
                    build_virtual_service.side_effect = sorted_wrap
                    get_data. return_value = {'VS': ['ba', 'ed']}
                    res = self.lm.get_virtual_services()
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


class TestLmApiWrapperCalls:

    def setup(self):
        self.p__get = patch.object(LoadMaster, '_get')
        self._get = self.p__get.start()
        self.p__post = patch.object(LoadMaster, '_post')
        self._post = self.p__post.start()
        self.p_send_response = patch.object(client, 'send_response')
        self.send_response = self.p_send_response.start()
        self.p_is_successful = patch.object(client, 'is_successful')
        self.is_successful = self.p_is_successful.start()

        self.lm = LoadMaster("1.1.1.1", "bal", "1fourall")

    def teardown(self):
        self.p__get.stop()
        self.p__post.stop()
        self.p_send_response.stop()
        self.p_is_successful.stop()

    def test_stats(self):
        self.lm.stats()
        self.lm._get.assert_called_with('/stats')

    def test_update_firmware(self):
        file = "file"
        self.lm.version = "V7.1.40"
        self.lm.update_firmware(file)
        self.lm._post.assert_called_with('/installpatch', file)
        assert_is_none(self.lm.version)

    def test_restore_firmware(self):
        self.lm.version = "V7.1.40"
        self.lm.restore_firmware()
        self.lm._get.assert_called_with('/restorepatch')
        assert_is_none(self.lm.version)

    def test_shutdown(self):
        self.lm.shutdown()
        self.lm._get.assert_called_with('/shutdown')

    def test_reboot(self):
        self.lm.reboot()
        self.lm._get.assert_called_with('/reboot')

    def test_get_sdn_controller(self):
        self.lm.get_sdn_controller()
        self.lm._get.assert_called_with('/getsdncontroller')

    def test_get_license_info(self):
        self.lm.get_license_info()
        self.lm._get.assert_called_with('360/licenseinfo')
        self.lm._get.side_effect = exceptions.KempTechApiException
        with assert_raises(exceptions.KempTechApiException):
            self.lm.get_license_info()

    def test_list_addons(self):
        self.lm.list_addons()
        self.lm._get.assert_called_with('/listaddon')

    def test_upload_template(self):
        file = 'file'
        self.lm.upload_template(file)
        self.lm._post.assert_called_with('/uploadtemplate', file)

    def test_list_templates(self):
        self.lm.list_templates()
        self.lm._get.assert_called_with('/listtemplates')

    def test_delete_template(self):
        name = 'template_name'
        self.lm.delete_template(name)
        params = {'name': name}
        self.lm._get.assert_called_with('/deltemplate', parameters=params)

    def test_apply_template(self):
        ip = '1.1.1.1'
        port = 80
        prot = 'tcp'
        name = 'template_name'
        self.lm.apply_template(ip, port, prot, name)
        params = {
            'vs': ip,
            'port': port,
            'prot': prot,
            'name': name,
        }
        self.lm._get.assert_called_with('/addvs', parameters=params)

    def test_get_sdn_info(self):
        self.lm.get_sdn_info()
        self.lm._get.assert_called_with('/sdninfo')

    def test_restore_backup(self):
        file = 'file'
        backup_type = 2
        self.lm.restore_backup(backup_type, file)
        params = {'type': backup_type}
        self.lm._post.assert_called_with('/restore', file=file, parameters=params)

    def test_alsi_license(self):
        kempid = 's@s.com'
        password = 'p4ss'
        self.lm.alsi_license(kempid, password)
        params = {
            'kemp_id': kempid,
            'password': password,
        }
        self.lm._get.assert_called_with('/alsilicense', parameters=params)

    def test_set_initial_password(self):
        password = 'p4ss'
        self.lm.set_initial_password(password)
        params = {
            'passwd': password,
        }
        self.lm._get.assert_called_with('/set_initial_password', parameters=params)

    def test_kill_asl_instance(self):
        self.lm.kill_asl_instance()
        self.lm._get.assert_called_with('/killaslinstance')

    def test_add_local_user(self):
        user = 'shane'
        password = 'p4ss'
        radius = False
        self.lm.add_local_user(user, password, radius)
        params = {
            'user': user,
            'radius': 'n',
            'password': password,
        }
        self.lm._get.assert_called_with('/useraddlocal', params)

    def test_delete_local_user(self):
        user = 'shane'
        self.lm.delete_local_user(user)
        params = {'user': user}
        self.lm._get.assert_called_with('/userdellocal', params)

    def test_set_user_perms_as_list(self):
        user = 'shane'
        perms = ['root', 'vs']
        self.lm.set_user_perms(user, perms)
        params = {
            'user': user,
            'perms': 'root,vs',
        }
        self.lm._get.assert_called_with('/usersetperms', params)

    def test_set_user_perms_as_string(self):
        user = 'shane'
        perms = 'root'
        self.lm.set_user_perms(user, perms)
        params = {
            'user': user,
            'perms': 'root',
        }
        self.lm._get.assert_called_with('/usersetperms', params)

    def test_new_user_cert(self):
        user = 'shane'
        perms = ['root', 'vs']
        self.lm.new_user_cert(user)
        params = {'user': user}
        self.lm._get.assert_called_with('/usernewcert', params)
