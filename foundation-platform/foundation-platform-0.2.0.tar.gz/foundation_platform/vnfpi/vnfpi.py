from __future__ import print_function
import os
import paramiko
import shlex
import subprocess
import time


# Class used for continuous integration testing that instantiates a VM
# against which tests can be run
class VNFTestVM(object):
    def __init__(self, network_name, flavor, vm_name, image_name,
                 security_group, image_file_format=None):
        self.__IP_address = None
        self.__network_name = network_name
        self.__network_uuid = None
        self.__flavor = flavor
        self.__vm_name = vm_name + "." + str(os.getpid())
        self.__image_name = image_name
        self.__image_file_format = image_file_format
        self.__os_auth_url = os.environ.get('OS_AUTH_URL', None)
        self.__os_tenant_id = os.environ.get('OS_TENANT_ID', None)
        self.__os_tenant_name = os.environ.get('OS_TENANT_NAME', None)
        self.__os_region_name = os.environ.get('OS_REGION_NAME', None)
        self.__os_username = os.environ.get('OS_USERNAME', None)
        self.__os_password = os.environ.get('OS_PASSWORD', None)
        self.__security_group = security_group
        self.__vm_id = None
        self.__vol_id = None

        self.__base_command = ("/usr/bin/nova " +
                               "--os-auth-url '" + self.__os_auth_url + "' " +
                               "--os-username '" + self.__os_username + "' " +
                               "--os-tenant-name '" + self.__os_tenant_name + "' " +
                               "--os-password '" + self.__os_password + "' ")

        # First obtain the network uuid for the given network name
        try:
            self.__get_network_uuid()
        except Exception:
            raise

        self.__boot_command = (self.__base_command + "boot " +
                               "--nic net-id=" + self.__network_uuid + " " +
                               "--image '" + self.__image_name + "' " +
                               "--flavor '" + self.__flavor + "' " +
                               "--security-groups '" + self.__security_group + "' " +
                               self.__vm_name)
        self.__check_command = (self.__base_command + "show ")

        # Go and boot the NFV test VM using class parameters and save the IP address we get
        try:
            self.__boot_vm()
        except Exception:
            raise

    @staticmethod
    def __find_response_value(resp_string, pattern):
        # Find a pattern in a string.  The string is expected to be the return from one of the
        # OpenStack python commands but basically anything formatted like this will work:
        # | something <whitespace> | value <whitespace> | morestuff <whitespace> |<newline>
        # We'll look for the something and return the value with all the whitespace stripped.
        __pattern = "| " + pattern
        if not(__pattern in resp_string):
            raise ValueError("Can't find requested pattern " + pattern + " in " + resp_string)
        __start = resp_string.find(__pattern)
        __end = resp_string.find("\n", __start)
        return resp_string[__start:__end].split("|")[2].strip()

    # Get the network uuid from the network name
    def __get_network_uuid(self):
        # Get network uuid
        __cmd_line = (self.__base_command + "tenant-network-list ")

        try:
            __rc = subprocess.check_output(shlex.split(__cmd_line), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e
        else:
            # We can't use __find_response_value here because the value is before the key.
            # In this case, once we find the line we want, we need to go backwards to the end
            # of the previous line and then just step foward by 1 to get the start of this line
            __start = __rc.find(self.__network_name)
            __end = __rc.find("\n", __start)
            __start = __rc.rfind("\n", 0, __start) + 1
            self.__network_uuid = __rc[__start:__end].split("|")[1].strip()
            # If for some reason we didn't find our network
            if not self.__network_uuid:
                raise ValueError("Network: " + self.__network_name + " not found in tenant")

    # Boot the NFV VM
    def __boot_vm(self):
        print("__boot_vm: Booting NFV VM: " + self.__vm_name)

        try:
            __response = subprocess.check_output(shlex.split(self.__boot_command),
                                                 universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e

        # OK, this whole method should be rewritten to use the python client API but...
        self.__vm_id = self.__find_response_value(__response, "id")

        # OK, we did all of that so we could just poll to see if the VM status has moved to
        # Active.  Active here means that the status is ACTIVE and vm_state is active, but of
        # which we'll have to find using the method above.
        __check_command = (self.__check_command + self.__vm_id)
        __running = False
        __count = 0
        __limit = 10
        print("__boot_vm: Waiting for VM to start running")
        while not __running:
            try:
                __response = subprocess.check_output(shlex.split(__check_command),
                                                     universal_newlines=True)
            except subprocess.CalledProcessError as __e:
                raise __e
            __status = self.__find_response_value(__response, "status")
            __state = self.__find_response_value(__response, "OS-EXT-STS:vm_state")
            if __status == "ACTIVE" and __state == "active":
                __running = True
                self.__IP_address = self.__find_response_value(__response, self.__network_name)
                print("NFV VM: " + self.__vm_name + " IP address: " + self.__IP_address)
            else:
                time.sleep(15)
                __count += 1
                if __count > __limit:
                    raise ValueError("Didn't detect VM start")

    # Stop the NFV VM
    def stop(self):
        print("stop: Stopping NFV VM: " + self.__vm_name)

        __stop_command = (self.__base_command + "stop " +
                          self.__vm_name)

        try:
            subprocess.check_output(shlex.split(__stop_command), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e

        # OK, we did all of that so we could just poll to see if the VM status has moved to
        # Shutoff.  Shutoff here means that the status is SHUTOFF and vm_state is Shutdown, but of
        # which we'll have to find using the method above.
        __check_command = (self.__check_command + self.__vm_id)
        __running = True
        __count = 0
        __limit = 10
        print("stop: Waiting for VM " + self.__vm_name + " to stop running")
        while __running:
            try:
                __response = subprocess.check_output(shlex.split(__check_command),
                                                     universal_newlines=True)
            except subprocess.CalledProcessError as __e:
                raise __e

            __status = self.__find_response_value(__response, "status")
            __state = self.__find_response_value(__response, "OS-EXT-STS:vm_state")
            if __status == "SHUTOFF" and __state == "stopped":
                __running = False
            else:
                time.sleep(15)
                __count += 1
                if __count > __limit:
                    raise ValueError("Didn't detect VM stop")

    # Run passed command on NFV VM
    def run_command(self, user, password, command):
        # Make SSH connection
        print("run_command: Running Command: [" + command + "] on " + self.__vm_name)

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        __success = False
        __limit = 10
        __count = 0
        while not __success:
            try:
                client.connect(self.__IP_address, username=user, password=password)
                __success = True
            except paramiko.AuthenticationException:
                raise ValueError("Could not log in to VM with user = " + user)
            except Exception:
                __count += 1
                if __count > __limit:
                    raise ValueError("Could not establish secure connection")

        # Run the command
        __stdin, __stdout, __stderr = client.exec_command(command)

        __output = ""
        for __line in __stdout:
            # print __line.strip('\n')
            __output += __line

        client.close()

        return __output

    def delete(self):
        # Delete the VM
        print("delete: Deleting NFV VM: " + self.__vm_name)
        __cmd_line = ("/usr/bin/nova " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "delete " +
                      self.__vm_name)
        try:
            subprocess.check_output(shlex.split(__cmd_line))
        except subprocess.CalledProcessError as __e:
            raise __e

    def __del__(self):
        if self.__vol_id:
            try:
                self.detach_volume()
            except:
                raise

            try:
                self.delete_volume()
            except:
                raise

        try:
            self.delete()
        except Exception:
            raise

    def get_IP_address(self):
        return self.__IP_address

    def get_VM_name(self):
        return self.__vm_name

    @staticmethod
    def __get_field(res, srch, field):
        # Search res for srch and return passed field
        for __line in res.splitlines():
            if srch in __line:
                # print line.split()[field]
                return __line.split()[field]

        return None

    def __get_status(self, res, srch):
        # Return status (second field in line)
        return self.__get_field(res, srch, 3)

    def __get_uuid(self, res, srch):
        # Return first field (uuid)
        return self.__get_field(res, srch, 1)

    # Get the id of the volume using its name
    def __get_volume_id(self):
        # Get volume uuid
        __cmd_line = ("/usr/bin/cinder " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "list")

        try:
            __rc = subprocess.check_output(shlex.split(__cmd_line), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e

        # Parse volume id out of string
        self.__vol_id = self.__get_uuid(__rc, self.__vol_name)

        # If for some reason we didn't find our VM
        if not self.__vol_id:
            raise ValueError("Volume: " + self.__vol_name + " not found in tenant")

    def __create_volume(self, size):
        # Create a volume name by appending static string to existing VM name
        self.__vol_name = self.__vm_name + "_DISK_2"

        print("__create_volume: Creating volume " + self.__vol_name + " of size: " + size + "GB")
        # Create the volume in OpenStack
        __cmd_line = ("/usr/bin/cinder " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "create " + size + " " +
                      "--name " + self.__vol_name + " " +
                      "--volume-type default-rbd ")

        try:
            subprocess.check_output(shlex.split(__cmd_line), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e

        # Wait for volume to become available before proceeding
        __cmd_line = ("/usr/bin/cinder " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "list")

        __avail = False
        __count = 0
        __limit = 10
        print("__create_volume: Waiting for volume to become available")
        while not __avail:
            try:
                __response = subprocess.check_output(shlex.split(__cmd_line),
                                                     universal_newlines=True)
            except subprocess.CalledProcessError as __e:
                raise __e

            # Parse response for status
            __status = self.__get_status(__response, self.__vol_name)

            # If status is available, we're done
            if __status == "available":
                __avail = True

            else:
                time.sleep(5)

                __count += 1

                if __count > __limit:
                    raise ValueError("Volume: " + self.__vol_name + " never became available")

        # Grab the uuid of the newly created volume so we have it
        try:
            self.__get_volume_id()
        except:
            raise

    # Attach new volume to new VM
    def __attach_volume(self):
        print("__attach_volume: Attaching volume " + self.__vol_name + " to " + self.__vm_name)

        # Create and issue the attach command
        __cmd_line = (self.__base_command +
                      "volume-attach " +
                      self.__vm_id + " " +
                      self.__vol_id + " " +
                      "auto")

        try:
            subprocess.check_output(shlex.split(__cmd_line), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e

        # Wait for volume's status to go in-use
        __cmd_line = ("/usr/bin/cinder " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "list")

        __in_use = False
        __count = 0
        __limit = 10
        print("__attach_volume: Waiting for volume to become attached")
        while not __in_use:
            try:
                __response = subprocess.check_output(shlex.split(__cmd_line),
                                                     universal_newlines=True)
            except subprocess.CalledProcessError as __e:
                raise __e

            # Parse response for status
            __status = self.__get_status(__response, self.__vol_name)

            if __status == "in-use":
                __in_use = True

            else:
                time.sleep(5)

                __count += 1

                if __count > __limit:
                    raise ValueError("Volume: " + self.__vol_name + " never became available")

    def attach_volume(self, size):
        # Create a new volume to be attached to this VM
        try:
            self.__create_volume(size)
        except:
            raise

        # Attach the newly created volume to this VM
        try:
            self.__attach_volume()
        except:
            raise

    # Detach volume from VM
    def detach_volume(self):
        print("detach_volume: Detaching volume " + self.__vol_name + " from " + self.__vm_name)

        # Create and issue the detach command
        __cmd_line = (self.__base_command +
                      "volume-detach " +
                      self.__vm_id + " " +
                      self.__vol_id + " ")

        try:
            subprocess.check_output(shlex.split(__cmd_line), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e

        # Wait for volume's status to go available meaning it has been detached
        __cmd_line = ("/usr/bin/cinder " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "list")

        __available = False
        __count = 0
        __limit = 10
        print("__detach_volume: Waiting for volume to become available (detached)")
        while not __available:
            try:
                __response = subprocess.check_output(shlex.split(__cmd_line),
                                                     universal_newlines=True)
            except subprocess.CalledProcessError as __e:
                raise __e

            # Parse response for status
            __status = self.__get_status(__response, self.__vol_name)

            if __status == "available":
                __available = True

            else:
                time.sleep(5)

                __count += 1

                if __count > __limit:
                    raise ValueError("Volume: " + self.__vol_name + " never became available")

    # Delete the volume
    def delete_volume(self):
        print("delete_volume: Deleting volume " + self.__vol_name)

        # Create and issue the delete command
        __cmd_line = ("/usr/bin/cinder " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "delete " +
                      self.__vol_id)

        try:
            subprocess.check_output(shlex.split(__cmd_line), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e

        self.__vol_id = None

    # Upload a volume to an image
    def upload_to_image(self, name):
        print("upload_to_image: Uploading volume " + self.__vol_name + " to " + name)

        # Create and issue the upload command
        __cmd_line = ("/usr/bin/cinder " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "upload-to-image " +
                      self.__vol_name + " " +
                      name + " " +
                      "--disk-format qcow2 " +
                      "--force True")

        try:
            subprocess.check_output(shlex.split(__cmd_line), universal_newlines=True)
        except subprocess.CalledProcessError as __e:
            raise __e

        # Give upload time to start
        time.sleep(10)

        # Wait for volume's status to go back from uploading to in-use
        __cmd_line = ("/usr/bin/cinder " +
                      "--os-auth-url '" + self.__os_auth_url + "' " +
                      "--os-username '" + self.__os_username + "' " +
                      "--os-tenant-name '" + self.__os_tenant_name + "' " +
                      "--os-password '" + self.__os_password + "' " +
                      "list")

        __done = False
        __count = 0
        __limit = 180       # 30 minute limit  Might have to make configurable
        print("upload_to_image: Waiting for image to finish uploading")
        while not __done:
            try:
                __response = subprocess.check_output(shlex.split(__cmd_line),
                                                     universal_newlines=True)
            except subprocess.CalledProcessError as __e:
                raise __e

            # Parse response for status
            __status = self.__get_status(__response, self.__vol_name)

            if (__status == "in-use") or (__status == "available"):
                __done = True

            else:
                time.sleep(10)

                __count += 1

                if __count > __limit:
                    raise ValueError("Volume: " + self.__vol_name + " never became available")
