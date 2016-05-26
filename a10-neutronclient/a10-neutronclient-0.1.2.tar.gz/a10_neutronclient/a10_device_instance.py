# Copyright 2015,  A10 Networks
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from a10_neutronclient import client_extension
from a10_neutronclient.resources import a10_device_instance


class DeviceInstanceExtension(client_extension.ClientExtension):

    resource = a10_device_instance.RESOURCE
    resource_plural = a10_device_instance.RESOURCES

    resource_attribute_map = a10_device_instance.RESOURCE_ATTRIBUTE_MAP

    object_path = '/%s' % resource_plural
    resource_path = '/%s/%%s' % resource_plural
    versions = ['2.0']


class DeviceInstanceList(client_extension.List, DeviceInstanceExtension):
    """List current A10 vThunder instances"""

    shell_command = 'a10-device-instance-list'

    list_columns = ['id', 'name', 'host', 'api_version', 'nova_instance_id', 'description']


class DeviceInstanceShow(client_extension.Show, DeviceInstanceExtension):
    """Show A10 vThunder instance"""

    shell_command = 'a10-device-instance-show'
