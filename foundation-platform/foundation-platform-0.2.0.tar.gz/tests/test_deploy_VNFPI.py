from foundation_platform.vnfpi import vnfpi
import os
import shlex
import subprocess
import time
import unittest2


class TestVNFPI(unittest2.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestVNFPI, self).__init__(*args, **kwargs)
        self.__os_auth_url = os.environ.get('OS_AUTH_URL', None)
        self.__os_tenant_id = os.environ.get('OS_TENANT_ID', None)
        self.__os_tenant_name = os.environ.get('OS_TENANT_NAME', None)
        self.__os_region_name = os.environ.get('OS_REGION_NAME', None)
        self.__os_username = os.environ.get('OS_USERNAME', None)
        self.__os_password = os.environ.get('OS_PASSWORD', None)
        self.__image_name = os.environ.get('nfv_fp_image_name', None)
        self.__image_file_format = os.environ.get('nfv_fp_image_file_format',
                                                  None)
        self.__network_name = os.environ.get('nfv_fp_network_name', None)
        self.__flavor = os.environ.get('nfv_fp_flavor', None)
        self.__vm_name = os.environ.get('nfv_fp_vm_name', None)
        self.__security_group = os.environ.get('nfv_fp_security_group', None)
        self.__test_username = os.environ.get('nfv_fp_test_username', None)
        self.__test_password = os.environ.get('nfv_fp_test_password', None)
        self.__image_server_url = os.environ.get('nfv_fp_image_server_url',
                                                 None)
        self.__image_path = os.environ.get('nfv_fp_image_path', None)
        self.__flask_version = os.environ.get('nfv_fp_flask_version', None)
        self.__cinder_version = os.environ.get('nfv_fp_cinder_version', None)
        self.__glance_version = os.environ.get('nfv_fp_glance_version', None)
        self.__heat_version = os.environ.get('nfv_fp_heat_version', None)
        self.__keystone_version = os.environ.get('nfv_fp_keystone_version', None)
        self.__mistral_version = os.environ.get('nfv_fp_mistral_version', None)
        self.__murano_version = os.environ.get('nfv_fp_murano_version', None)
        self.__neutron_version = os.environ.get('nfv_fp_neutron_version', None)
        self.__nova_version = os.environ.get('nfv_fp_nova_version', None)
        self.__swift_version = os.environ.get('nfv_fp_swift_version', None)
        self.__nfvfp_service_port = os.environ.get('nfv_fp_service_port', None)
        self.__nfvfp_service_image_path = os.environ.get('nfv_fp_service_image_path', None)
        self.__java_version = os.environ.get('nfv_fp_java_version', None)
        self.__jython_version = os.environ.get('nfv_fp_jython_version', None)
        self.__redis_version = os.environ.get('nfv_fp_redis_version', None)
        self.__SAM_jar_pathname = os.environ.get('nfv_fp_SAM_jar_pathname', None)
        self.__SAM_image_pathname = os.environ.get('nfv_fp_SAM_image_pathname', None)
        self.__HOT_path = os.environ.get('nfv_fp_HOT_path', None)
        self.__HOT_name = os.environ.get('nfv_fp_HOT_name', None)
        self.__HOT_env = os.environ.get('nfv_fp_HOT_env', None)

    # Check all the env vars that should be defined.
    def setUp(self):
        if self.__os_auth_url is None:
            raise ValueError("can't find OS_AUTH_URL in environment")
        if self.__os_tenant_id is None:
            raise ValueError("can't find OS_TENANT_ID in environment")
        if self.__os_tenant_name is None:
            raise ValueError("can't find OS_TENANT_NAME in environment")
        if self.__os_region_name is None:
            raise ValueError("can't fine OS_REGION_NAME in environment")
        if self.__os_username is None:
            raise ValueError("can't find OS_USERNAME in environment")
        if self.__os_password is None:
            raise ValueError("can't find OS_PASSWORD in environment")
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
        if self.__flask_version is None:
            raise ValueError("can't find nfv_fp_flask_version in environment")
        if self.__cinder_version is None:
            raise ValueError("can't find nfv_fp_cinder_version in environment")
        if self.__glance_version is None:
            raise ValueError("can't find nfv_fp_glance_version in environment")
        if self.__heat_version is None:
            raise ValueError("can't find nfv_fp_heat_version in environment")
        if self.__keystone_version is None:
            raise ValueError("can't find nfv_fp_keystone_version in environment")
        if self.__mistral_version is None:
            raise ValueError("can't find nfv_fp_mistral_version in environment")
        if self.__murano_version is None:
            raise ValueError("can't find nfv_fp_murano_version in environment")
        if self.__neutron_version is None:
            raise ValueError("can't find nfv_fp_neutron_version in environment")
        if self.__nova_version is None:
            raise ValueError("can't find nfv_fp_nova_version in environment")
        if self.__swift_version is None:
            raise ValueError("can't find nfv_fp_swift_version in environment")
        if self.__image_server_url is None:
            raise ValueError("can't find nfv_fp_image_server_url in environment")
        if self.__image_path is None:
            raise ValueError("can't find nfv_fp_image_path in environment")
        if self.__nfvfp_service_port is None:
            raise ValueError("can't find nfv_fp_service_port in environment")
        if self.__nfvfp_service_image_path is None:
            raise ValueError("can't find nfv_fp_service_image_path in environment")
        if self.__java_version is None:
            raise ValueError("can't find nfv_fp_java_version in environment")
        if self.__jython_version is None:
            raise ValueError("can't find nfv_fp_jython_version in environment")
        if self.__redis_version is None:
            raise ValueError("can't find nfv_fp_redis_version in environment")
        if self.__SAM_jar_pathname is None:
            raise ValueError("can't find nfv_fp_SAM_jar_pathname in environment")
        if self.__SAM_image_pathname is None:
            raise ValueError("can't find nfv_fp_SAM_image_pathname in environment")
        if self.__HOT_path is None:
            raise ValueError("can't find nfv_fp_HOT_path in environment")
        if self.__HOT_name is None:
            raise ValueError("can't find nfv_fp_HOT_name in environment")
        if self.__HOT_env is None:
            raise ValueError("can't find nfv_fp_HOT_env in environment")

    # Run a curl command against passed url
    @staticmethod
    def __run_curl_cmd(url):
        __cmd = ('''/usr/bin/curl --output /dev/null --silent --head --fail ''' +
                 url)

        __args = __cmd.split()
        __process = subprocess.Popen(__args, shell=False, stdout=subprocess.PIPE)
        __process.wait()

        return __process

    @staticmethod
    def __get_field(res, srch, field):
        # Search res for srch and return passed field
        for __line in res.splitlines():
            if srch in __line:
                # print line.split()[field]
                return __line.split()[field]

        return None

    def __get_status(self, res, srch):
        # Return status (third field in line)
        return self.__get_field(res, srch, 5)

    # Verify that the current base image file resides on the image server
    def test_check_VNF_Platform_image_existence(self):
        __url = (self.__image_server_url + self.__image_path + "/" +
                 self.__image_name + '.' + self.__image_file_format)

        __process = self.__run_curl_cmd(__url)

        # print __process.returncode
        self.assertEqual(0, __process.returncode, "VNF Platform image file: " +
                         __url + " does not exist!")

    # Verify that the base image file exists in tenant
    def test_VNF_Platform_image_in_tenant(self):
        __cmd_line = ("nova " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "image-show " +
                      self.__image_name)

        try:
            __rc = subprocess.check_output(shlex.split(__cmd_line), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e
        else:
            self.assertTrue((self.__image_name in __rc),
                            "VNF Platform image: " +
                            self.__image_name +
                            " not found in OpenStack glance")

    # Verify that the NFVFP Heat template deploys properly
    def test_VNF_Platform_Heat_deployment(self):
        # Try to create the stack via Heat CLI
        __stack_name = "NFVFP_TEST" + "." + str(os.getpid())

        __cmd_line = ("heat " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "stack-create " +
                      "-f " + self.__HOT_path + "/" + self.__HOT_name + " " +
                      "-e " + self.__HOT_path + "/" + self.__HOT_env + " " +
                      __stack_name)

        try:
            __rc = subprocess.check_output(shlex.split(__cmd_line), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e
        else:
            __status = self.__get_status(__rc, __stack_name)

            self.assertTrue(("CREATE_IN_PROGRESS" == __status),
                            "VNF Heat stack-create not started. HOT:" +
                            self.__HOT_path + "/" + self.__HOT_name + " " +
                            self.__HOT_path + "/" + self.__HOT_env + " ")

        # Check to see if stack creates without problems
        __cmd = ("heat " +
                 "--os-auth-url '" + self.__os_auth_url + "' " +
                 "--os-username '" + self.__os_username + "' " +
                 "--os-tenant-name '" + self.__os_tenant_name + "' " +
                 "--os-password '" + self.__os_password + "' " +
                 "stack-list ")

        __started = False
        __count = 0
        __limit = 60
        __status = ""
        while not __started:
            try:
                __rc = subprocess.check_output(shlex.split(__cmd), universal_newlines=True)
            except subprocess.CalledProcessError as __e:
                raise __e
            else:
                __status = self.__get_status(__rc, __stack_name)

                if __status == "CREATE_COMPLETE":
                    __started = True

                else:
                    time.sleep(5)

                    __count += 1

                    if __count > __limit:
                        self.fail("Stack: " + __stack_name +
                                  " never reached CREATE_COMPLETE")

        # Did stack create successfully?
        self.assertTrue(("CREATE_COMPLETE" == __status),
                        "VNF Heat stack-create failed. HOT:" +
                        self.__HOT_path + "/" + self.__HOT_name + " " +
                        self.__HOT_path + "/" + self.__HOT_env + " ")

        # Delete the test stack
        __cmd_line = ("heat " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "stack-delete " +
                      __stack_name)

        try:
            subprocess.check_output(shlex.split(__cmd_line), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e

    # Verify that components exist for building base image
    def test_check_VNF_Platform_components_existence(self):
        __url = (self.__image_server_url + self.__SAM_jar_pathname)

        __cmd = ('''/usr/bin/curl --output /dev/null --silent --head --fail ''' +
                 __url)
        __args = __cmd.split()
        __process = subprocess.Popen(__args, shell=False, stdout=subprocess.PIPE)
        __process.wait()
        # print __process.returncode
        self.assertEqual(0, __process.returncode, "VNF Platform component file: " +
                         __url + " does not exist!")

    def __test_installation(self, vm, name, version, source):
        try:
            # Build command
            __cmd = source + " | " + "/usr/bin/grep " + name

            __out = vm.run_command(self.__test_username, self.__test_password, __cmd)
        except Exception:
            raise

        # Is software installed?
        self.assertTrue((name in __out),
                        name +
                        " not found to be installed on " +
                        self.__image_name +
                        " in OpenStack glance")

        # Is it the proper version?
        self.assertTrue((version in __out),
                        name +
                        " version installed on " +
                        self.__image_name +
                        " in OpenStack glance not " +
                        version)

    # Test to see if a connection can be made to nfvfp service running on VM
    def __test_nfvfp_service_connect(self, vm):
        __url = "http://" + vm.get_IP_address() + ":" + self.__nfvfp_service_port + \
                self.__nfvfp_service_image_path

        __process = self.__run_curl_cmd(__url)

        # print __process.returncode
        self.assertEqual(0, __process.returncode, "VNF Platform service: " +
                         __url + " is not running!")

    # Make sure nfvfp service is actually running on VM
    def __test_nfvfp_service_running(self, vm):
        try:
            __out = vm.run_command(self.__test_username, self.__test_password,
                                   '/etc/init.d/nfvfp status')
        except Exception:
            raise

        # Output expected to be "NFVFP service is not running" if process is not found
        self.assertTrue(('not' not in __out),
                        " nfvfp service not found to be running on VM from " +
                        self.__image_name +
                        " in OpenStack glance")

    # Check to make sure a file is present
    def __test_file_present(self, vm, path):
        try:
            __cmd = 'ls ' + path
            __out = vm.run_command(self.__test_username, self.__test_password, __cmd)
        except Exception:
            raise

        # Strip any trailing whitespace
        __out = __out.rstrip()

        # Output expected to be an echo of path parameter
        # print "Path:[" + path + "]" + "Out:[" + __out + "]"
        self.assertEqual(path, __out,
                         os.path.basename(path) + " not found in " + os.path.dirname(path) +
                         " on VM from " + self.__image_name)

    # Verify required applications are installed and/or running on image/VM
    def test_nfvfp_applications(self):
        # Create a test VM from current golden image against which to test
        __vm = vnfpi.VNFTestVM(network_name=self.__network_name, flavor=self.__flavor,
                               vm_name=self.__vm_name, image_name=self.__image_name,
                               image_file_format=self.__image_file_format,
                               security_group=self.__security_group)

        # Create a list of required packages and version to test
        # Package name, version, command to determine if package installed
        __package_list = {0: ['Flask', self.__flask_version, '/bin/pip list'],
                          1: ['python-cinderclient', self.__cinder_version, '/bin/pip list'],
                          2: ['python-glanceclient', self.__glance_version, '/bin/pip list'],
                          3: ['python-heatclient', self.__heat_version, '/bin/pip list'],
                          4: ['python-keystoneclient', self.__keystone_version, '/bin/pip list'],
                          5: ['python-mistralclient', self.__mistral_version, '/bin/pip list'],
                          6: ['python-muranoclient', self.__murano_version, '/bin/pip list'],
                          7: ['python-neutronclient', self.__neutron_version, '/bin/pip list'],
                          8: ['python-novaclient', self.__nova_version, '/bin/pip list'],
                          9: ['python-swiftclient', self.__swift_version, '/bin/pip list'],
                          10: ['redis', self.__redis_version, '/bin/pip list'],
                          11: ['java', self.__java_version, ('/usr/bin/rpm -qa | grep java | '
                                                             'grep openjdk | grep -v headless')],
                          12: ['Jython', self.__jython_version,
                               '/opt/jython/bin/jython --version 2>&1'],
                          13: ['redis', self.__redis_version, '/opt/jython/bin/pip list']
                          }

        for __id in __package_list:
            self.__test_installation(__vm, __package_list[__id][0], __package_list[__id][1],
                                     __package_list[__id][2])

        # Test to see if SAM file is present on image
        self.__test_file_present(__vm, self.__SAM_image_pathname)

        # Test if NFVFP service is running on the VM
        self.__test_nfvfp_service_running(__vm)

        # Test if we can connect to the NFVFP service from external source
        self.__test_nfvfp_service_connect(__vm)

        # Explicitly call delete to forcibly remove VM in case of error
        __vm.delete()


def main():
    __suite = unittest2.TestLoader().loadTestsFromTestCase(TestVNFPI)
    __suite()


if __name__ == '__main__':
    main()
