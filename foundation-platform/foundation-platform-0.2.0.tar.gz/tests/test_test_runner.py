from foundation_platform.vnfpi import vnfpi
import os
import shlex
import subprocess
import unittest2 as unittest


class TestRunner(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestRunner, self).__init__(*args, **kwargs)
        self.__os_auth_url = os.environ.get('OS_AUTH_URL', None)
        self.__os_tenant_id = os.environ.get('OS_TENANT_ID', None)
        self.__os_tenant_name = os.environ.get('OS_TENANT_NAME', None)
        self.__os_region_name = os.environ.get('OS_REGION_NAME', None)
        self.__os_username = os.environ.get('OS_USERNAME', None)
        self.__os_password = os.environ.get('OS_PASSWORD', None)
        self.__image_name = os.environ.get('nfv_fp_image_name', None)
        self.__image_file_format = os.environ.get('nfv_fp_image_file_format', None)
        self.__network_name = os.environ.get('nfv_fp_network_name', None)
        self.__flavor = os.environ.get('nfv_fp_flavor', None)
        self.__vm_name = "test_runner_vm"
        self.__security_group = os.environ.get('nfv_fp_security_group', None)
        self.__test_username = os.environ.get('nfv_fp_test_username', None)
        self.__test_password = os.environ.get('nfv_fp_test_password', None)
        self.__zato_version = os.environ.get('nfv_fp_zato_version', None)
        self.__glance_version = os.environ.get('nfv_fp_glance_version', None)

    # See if we can find the client in our path using the which command.
    def __check_for_client(self, client):
        try:
            __rc = subprocess.check_output(['which', client], universal_newlines=True)
        except subprocess.CalledProcessError:
            __rc = "not found"
        return __rc

    # See if the client can at least return its version - we'll call that
    # executable.
    def __check_client_execution(self, client):
        if self.__check_for_client(client) != "not found":
            try:
                __rc = subprocess.check_output([client, '--version'], universal_newlines=True)
            except subprocess.CalledProcessError:
                __rc = "failed"
        else:
            __rc = "failed"
        return __rc

    # Setup the OpenStack env vars that should be defined.
    def setUp(self):
        if self.__os_auth_url is None:
            raise ValueError("can't find OS_AUTH_URL in environment")
        if self.__os_tenant_id is None:
            raise ValueError("can't find OS_TENANT_ID in environment")
        if self.__os_tenant_name is None:
            raise ValueError("can't find OS_TENANT_NAME in environment")
        if self.__os_username is None:
            raise ValueError("can't find OS_USERNAME in environment")
        if self.__os_password is None:
            raise ValueError("can't find OS_PASSWORD in environment")
        if self.__os_region_name is None:
            raise ValueError("can't fine OS_REGION_NAME in environment")
        if self.__image_name is None:
            raise ValueError("can't find nfv_fp_image_name in environment")
        if self.__image_file_format is None:
            raise ValueError("can't find nfv_fp_image_file_format in environment")
        if self.__network_name is None:
            raise ValueError("can't find nfv_fp_network_name in environment")
        if self.__flavor is None:
            raise ValueError("can't find nfv_fp_flavor in environment")
        if self.__vm_name is None:
            raise ValueError("can't find nfv_fp_vm_name in environment")
        if self.__security_group is None:
            raise ValueError("can't find nfv_fp_security_group in environment")
        if self.__test_username is None:
            raise ValueError("can't find nfv_fp_test_username in environment")
        if self.__test_password is None:
            raise ValueError("can't find nfv_fp_test_password in environment")
        if self.__zato_version is None:
            raise ValueError("can't find nfv_fp_zato_version in environment")
        if self.__glance_version is None:
            raise ValueError("can't find nfv_fp_glance_version in environment")

    # Verify that the runner can run
    def test_run_simple_test(self):
        self.assertTrue(True, "Couldn't run simple test")

    # Verify that the heat client exists in the runner
    def test_heat_client_present(self):
        self.assertNotEqual(self.__check_for_client('heat'),
                            "not found", "heat client not found")

    # Verify that the glance client exists in the runner
    def test_glance_client_present(self):
        self.assertNotEqual(self.__check_for_client('glance'), "not found",
                            "glance client not found")

    # Verify that we can run the heat client
    def test_heat_client_execution(self):
        self.assertNotEqual(self.__check_client_execution('heat'), "failed",
                            "heat client didn't execute")

    # Verify that we can run the glance client
    def test_glance_client_execution(self):
        self.assertNotEqual(self.__check_client_execution('glance'), "failed",
                            "glance client didn't execute")

    # Verify that we have API-level connectivity from the runner to the
    # an openstack cloud
    def test_api_connectivity(self):
        __cmd_line = ("nova " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "list")
        __rc = None
        try:
            __rc = subprocess.check_output(shlex.split(__cmd_line))
        except subprocess.CalledProcessError as e:
            print(str(e))
        self.assertNotEqual(__rc, "", "API connectivity failed using " +
                            __cmd_line)

    # Verify that we can SSH from the runner to the openstack cloud VM
    def test_ssh_connectivity(self):
        __vm = vnfpi.VNFTestVM(network_name=self.__network_name, flavor=self.__flavor,
                               vm_name=self.__vm_name, image_name=self.__image_name,
                               image_file_format=self.__image_file_format,
                               security_group=self.__security_group)
        __output = __vm.run_command(self.__test_username, self.__test_password,
                                    "ls /")
        __vm.delete()
        self.assertTrue(("etc" in __output), "couldn't ssh to test VM")


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRunner)
    suite()


if __name__ == '__main__':
    main()
