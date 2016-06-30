import copy

from batchcompute.utils import (partial, add_metaclass, CamelCasedClass)
from batchcompute.utils.jsonizable import Jsonizable
from batchcompute.utils.constants import (STRING, NUMBER, TIME)

class GroupDescription(Jsonizable):
    '''
    Description class of the group resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'DesiredVMCount': NUMBER,
        'InstanceType': STRING,
        'ResourceType': STRING,
    }
    required = [
        'DesiredVMCount'
    ]

    def __init__(self, dct={}):
        super(GroupDescription, self).__init__(dct)
        if 'ResourceType' not in self._d:
            self.setproperty('ResourceType', 'OnDemand')
        if 'InstanceType' not in self._d:
            self.setproperty('InstanceType', '')

    def setproperty(self, key, value):
        super_set = super(GroupDescription, self).setproperty
        if key == 'InstanceType' and not value.strip():
            pass
        else:
            super_set(key, value)
GroupDescription = add_metaclass(GroupDescription, CamelCasedClass)

class SystemDisk(Jsonizable):
    '''Description class of the disk resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Type': STRING,
        'Size': NUMBER,
    }
    required = ['Size']
    
    def __init__(self, dct={}):
        super(SystemDisk, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(SystemDisk, self).setproperty
        if key == 'Type' and not value.strip():
            pass
        else:
            super_set(key, value)
SystemDisk = add_metaclass(SystemDisk, CamelCasedClass)

class DataDisk(Jsonizable):
    '''Description class of the disk resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Type': STRING,
        'Size': NUMBER,
        'MountPoint': STRING,
    }
    required = ['Size']
    
    def __init__(self, dct={}):
        super(DataDisk, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(DataDisk, self).setproperty
        if key == 'MountPoint' and not value.strip():
            pass
        elif key == 'Type' and not value.strip():
            pass
        else:
            super_set(key, value)
DataDisk = add_metaclass(DataDisk, CamelCasedClass)

class Disks(Jsonizable):
    '''Description class of the disks resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'SystemDisk': (dict, SystemDisk),
        'DataDisk': (dict, DataDisk)
    }
    required = ['SystemDisk', 'DataDisk']

    def __init__(self, dct={}):
        super(Disks, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Disks, self).setproperty
        if key == 'SystemDisk' and isinstance(value, dict):
            new_value = SystemDisk(value)
        elif key == 'DataDisk' and isinstance(value, dict):
            new_value = DataDisk(value)
        else:
            new_value = value
        super_set(key, new_value)
Disks = add_metaclass(Disks, CamelCasedClass)

class Configs(Jsonizable):
    '''Description class of the configs resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Disks': (dict, Disks),
    }
    required = ['Disks']

    def __init__(self, dct={}):
        super(Configs, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Configs, self).setproperty
        if key == 'Disks' and isinstance(value, dict):
            new_value = Disks(value)
        else:
            new_value = value
        super_set(key, new_value)

    def add_system_disk(self, size, type_='cloud'):
        assert isinstance(size, NUMBER) and isinstance(type_, STRING), \
            'size must be number and type_ must be string'
        disk = {
            'Type': type_,
            'Size': size,
        } 

        if "Disks" in self._d:
            self._d['Disks']['SystemDisk'] = disk
        else:
            self._d['Disks'] = {
                'SystemDisk': disk
            }

    def add_data_disk(self, size, type_='cloud', mount_point=''):
        assert isinstance(size, NUMBER) and isinstance(type_, STRING) and \
            isinstance(mount_point, STRING), 'size must be number and type_ must be string'
        disk = {
            'Type': type_,
            'Size': size,
            'MountPoint': mount_point,
        } 

        if "Disks" in self._d:
            self._d['Disks']['DataDisk'] = disk
        else:
            self._d['Disks'] = {
                "DataDisk": disk
            }
Configs = add_metaclass(Configs, CamelCasedClass)
        

class ClusterDescription(Jsonizable):
    '''
    Description class of the cluster resource type in batchcompute service.
    '''
    resource_name = 'clusters'
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Description': STRING,
        'ImageId': STRING,
        'InstanceType': STRING,
        'UserData': dict,
        'Configs': (Configs, dict),
        'Groups': dict,
    }
    required = [
        'Name', 
        'ImageId', 
        'Groups'
    ]

    def __init__(self, dct={}):
        super(ClusterDescription, self).__init__(dct)
        if 'Groups' not in self._d:
            self.setproperty('Groups', {})
        if 'UserData' not in self._d:
            self.setproperty('UserData', {})

    def setproperty(self, key, value):
        super_set = super(ClusterDescription, self).setproperty
        if key == 'Groups' and isinstance(value, dict):
            new_value = {}
            for group_name in value:
                new_value[group_name] = self._validate_group(value[group_name])
        elif key == 'Configs' and isinstance(value, dict):
            new_value = Configs(value)
        else:
            new_value = value
        super_set(key, new_value)

    def _validate_group(self, group):
        return copy.deepcopy(group) if isinstance(group, GroupDescription) else GroupDescription(group)

    def add_group(self, group_name, group):
        if not group_name and not isinstance(group_name, STRING):
            raise TypeError('''Task name must be str and can't be empty ''')
        self._d['Groups'][group_name] = self._validate_group(group)

    def delete_group(self, group_name):
        if group_name in self._d['Groups']:
            del self._d['Groups'][group_name]
        else:
            pass

    def get_group(self, group_name):
        if group_name in self._d['Groups']:
            return self._d['Groups'][group_name]
        else:
            raise KeyError(''''%s' is not a valid group name''' % group_name)
ClusterDescription = add_metaclass(ClusterDescription, CamelCasedClass)
