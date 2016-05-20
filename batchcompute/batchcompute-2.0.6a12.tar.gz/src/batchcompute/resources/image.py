import copy

from batchcompute.utils import (partial, add_metaclass, CamelCasedClass)
from batchcompute.utils.jsonizable import Jsonizable
from batchcompute.utils.constants import (STRING, NUMBER, TIME)

class DeviceDescription(Jsonizable):
    '''
    Description class of device resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'ECSSnapshotId': STRING,
    }
    required = [
        'ECSSnapshotId'
    ]

    def __init__(self, dct={}):
        super(DeviceDescription, self).__init__(dct)
DeviceDescription = add_metaclass(DeviceDescription, CamelCasedClass)

class ImageDescription(Jsonizable):
    '''
    Description class of image resource type in batchcompute service.
    '''
    resource_name = 'images'
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Description': STRING,
        'OS': STRING,
        'ECSImageId': STRING,
        'DiskDeviceMapping': dict,
    }
    required = [
        'Name', 
        'OS',
        'ECSImageId'
    ]

    def __init__(self, dct={}):
        super(ImageDescription, self).__init__(dct)
        if 'DiskDeviceMapping' not in self._d:
            self.setproperty('DiskDeviceMapping', dict())
        if 'Description' not in self._d:
            self.setproperty('Description', 'Batchcompute Python SDK')

    def setproperty(self, key, value):
        super_set = super(ImageDescription, self).setproperty
        if key == 'DiskDeviceMapping':
            new_value = {}
            for disk_name in value:
                new_value[disk_name] = self._validate_disk(value[disk_name])
        else:
            new_value = value
        super_set(key, new_value)

    def _validate_disk(self, device):
        return copy.deepcopy(device) if isinstance(device, DeviceDescription) else DeviceDescription(device)

    def add_disk(self, disk_name, disk):
        if not disk_name and not isinstance(disk_name, STRING):
            raise TypeError('''Task name must be str and can't be empty ''')
        self._d['DiskDeviceMapping'][disk_name] = self._validate_disk(disk)

    def delete_disk(self, disk_name):
        if disk_name in self._d['DiskDeviceMapping']:
            del self._d['DiskDeviceMapping'][disk_name]
        else:
            pass

    def get_disk(self, disk_name):
        if disk_name in self._d['DiskDeviceMapping']:
            return self._d['DiskDeviceMapping'][disk_name]
        else:
            raise KeyError(''''%s' is not a valid disk name''' % disk_name)
ImageDescription = add_metaclass(ImageDescription, CamelCasedClass)
