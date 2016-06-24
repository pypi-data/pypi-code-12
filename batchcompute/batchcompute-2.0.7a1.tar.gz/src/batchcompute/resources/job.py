import copy

from .cluster import Configs
from batchcompute.utils import (partial, add_metaclass, CamelCasedClass)
from batchcompute.utils.jsonizable import Jsonizable
from batchcompute.utils.constants import (STRING, NUMBER, TIME)

class AutoCluster(Jsonizable):
    '''
    Description class of autocluster configuration in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'InstanceType': STRING,
        'ResourceType': STRING,
        'ImageId': STRING,
        'ECSImageId': STRING,
        'Configs': (dict, Configs),
        'UserData': dict,
    }
    required = [
    ]

    def __init__(self, dct={}):
        super(AutoCluster, self).__init__(dct)
        if 'InstanceType' not in self._d:
            self.setproperty('InstanceType', '')
        if 'ECSImageId' not in self._d:
            self.setproperty('ECSImageId', '')
        if 'UserData' not in self._d:
            self.setproperty('UserData', dict())

    def setproperty(self, key, value):
        super_set = super(AutoCluster, self).setproperty
        super_set(key, value)
AutoCluster = add_metaclass(AutoCluster, CamelCasedClass)

class InputMappingConfig(Jsonizable):
    '''
    Description class of input mapping configuration in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Locale': STRING,
        'Lock': bool,
    }
    required = [
    ]

    def __init__(self, dct={}):
        super(InputMappingConfig, self).__init__(dct)
        if 'Locale' not in self._d:
            self.setproperty('Locale', 'GBK')
        if 'Lock' not in self._d:
            self.setproperty('Lock', False)

    def setproperty(self, key, value):
        super_set = super(InputMappingConfig, self).setproperty
        super_set(key, value)
InputMappingConfig = add_metaclass(InputMappingConfig, CamelCasedClass)

class Command(Jsonizable):
    '''
    Description class of command in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'CommandLine': STRING,
        'PackagePath': STRING,
        'EnvVars': dict,
    }
    required = [
        'CommandLine',
        'PackagePath',
    ]

    def __init__(self, dct={}):
        super(Command, self).__init__(dct)
        if 'EnvVars' not in self._d:
            self.setproperty('EnvVars', dict())

    def setproperty(self, key, value):
        super_set = super(Command, self).setproperty
        if key == 'EnvVars' and isinstance(value, dict):
            for env in value:
                if not isinstance(value[env], STRING):
                    value[env] = str(value[env])
            new_value = value
        else:
            new_value = value
        super_set(key, new_value)
Command = add_metaclass(Command, CamelCasedClass)

class Parameters(Jsonizable):
    '''
    Description class of task parameters in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Command': (Command, dict),
        'InputMappingConfig': (InputMappingConfig, dict),
        'StdoutRedirectPath': STRING,
        'StderrRedirectPath': STRING,
    }
    required = [
        'Command',
        'InputMappingConfig',
        'StdoutRedirectPath',
        'StderrRedirectPath',
    ]

    def __init__(self, dct={}):
        super(Parameters, self).__init__(dct)
        if 'Command' not in self._d:
            self.setproperty('Command', Command())
        if 'InputMappingConfig' not in self._d:
            self.setproperty('InputMappingConfig', InputMappingConfig())

    def setproperty(self, key, value):
        super_set = super(Parameters, self).setproperty
        if key == 'Command' and isinstance(value, dict):
            new_value = Command(value)
        elif key == 'InputMappingConfig' and isinstance(value, dict):
            new_value = InputMappingConfig(value)
        else:
            new_value = value
        super_set(key, new_value)
Parameters = add_metaclass(Parameters, CamelCasedClass)

class TaskDescription(Jsonizable):
    '''
    Description class for task.

    Task in batchcompute is an unit which deal with the same logic work.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Parameters': (Parameters, dict),
        'InputMapping': dict,
        'OutputMapping': dict,
        'LogMapping': dict,
        'WriteSupport': bool,
        'Timeout': NUMBER,
        'InstanceCount': NUMBER,
        'MaxRetryCount': NUMBER,
        'ClusterId': STRING,
        'AutoCluster': (AutoCluster, dict),
    }
    required = [
        'Parameters',
        'TimeOut',
        'InstanceCount',
        ['ClusterId', 'AutoCluster'],
    ]

    def __init__(self, dct={}):
        super(TaskDescription, self).__init__(dct)
        if 'Parameters' not in self._d:
            self.setproperty('Parameters', Parameters())
        if 'InstanceCount' not in self._d:
            self.setproperty('InstanceCount', 1)
        if 'InputMapping' not in self._d:
            self.setproperty('InputMapping', dict())
        if 'OutputMapping' not in self._d:
            self.setproperty('OutputMapping', dict())
        if 'LogMapping' not in self._d:
            self.setproperty('LogMapping', dict())
        if 'Timeout' not in self._d:
            self.setproperty('Timeout', 3600)
        if 'MaxRetryCount' not in self._d:
            self.setproperty('MaxRetryCount', 0)

    def setproperty(self, key, value):
        super_set = super(TaskDescription, self).setproperty
        if key == 'Parameters' and isinstance(value, dict):
            new_value = Parameters(value)
        elif key == 'AutoCluster' and isinstance(value, dict):
            new_value = AutoCluster(value) 
        else:
            new_value = value
        super_set(key, new_value)
TaskDescription = add_metaclass(TaskDescription, CamelCasedClass)

class DAG(Jsonizable):
    '''
    Description class for JobDesc.

    JobDesc in batchcompute descripts the tasks and dependencies between each
    other.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Tasks': dict,
        'Dependencies': dict,
    }
    required = ['Tasks']

    def __init__(self, dct={}):
        super(DAG, self).__init__(dct)
        if 'Tasks' not in self._d:
            self.setproperty('Tasks', dict())
        if 'Dependencies' not in self._d:
            self.setproperty('Dependencies', dict())

    def setproperty(self, key, value):
        super_set = super(DAG, self).setproperty
        if key == 'Tasks' and isinstance(value, dict):
            new_value = {}
            for task_name in value:
                new_value[task_name] = self._validate_task(value[task_name])
        else:
            new_value = value
        super_set(key, new_value)

    def _validate_task(self, task):
        return copy.deepcopy(task) if isinstance(task, TaskDescription) else TaskDescription(task)

    def add_task(self, task_name, task):
        if not task_name and not isinstance(task_name, STRING):
            raise TypeError('''Task name must be str and can't be empty ''')
        self._d['Tasks'][task_name] = self._validate_task(task)

    def delete_task(self, task_name):
        if task_name in self._d['Tasks']:
            del self._d['Tasks'][task_name]
        else:
            pass

    def get_task(self, task_name):
        if task_name in self._d['Tasks']:
            return self._d['Tasks'][task_name]
        else:
            raise KeyError(''''%s' is not a valid task name''' % task_name)
DAG = add_metaclass(DAG, CamelCasedClass)

class JobDescription(Jsonizable):
    '''
    Description class for BatchCompute job.

    Job in BatchCompute descripts the batch task.
    '''
    resource_name = 'jobs'
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Description': STRING,
        'Priority': NUMBER,
        'Notification': dict,
        'JobFailOnInstanceFail': bool,
        'Type': STRING,
        'DAG': (dict, DAG)
    }
    required = [
        'Name',
        'Priority',
        'Type',
        'JobFailOnInstanceFail',
        'DAG',
    ]

    def __init__(self, dct={}):
        super(JobDescription, self).__init__(dct)
        if 'Description' not in self._d:
            self.setproperty('Description', 'Batchcompute Python SDK')
        if 'JobFailOnInstanceFail' not in self._d:
            self.setproperty('JobFailOnInstanceFail', True)
        if 'Type' not in self._d:
            self.setproperty('Type', 'DAG')

    def setproperty(self, key, value):
        super_set = super(JobDescription, self).setproperty
        if key == 'DAG' and isinstance(value, dict):
            new_value = DAG(value)
        else:
            new_value = value
        super_set(key, new_value)
JobDescription = add_metaclass(JobDescription, CamelCasedClass)
