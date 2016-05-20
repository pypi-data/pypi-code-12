'''Implementation of jsonizable Job, Task, Instance, Image and four types
responses of BatchComputeClient service.
'''
import copy

from batchcompute.utils import CamelCasedClass, remap, add_metaclass
from batchcompute.utils.jsonizable import Jsonizable, BatchEncoder
from batchcompute.utils.constants import STRING, NUMBER, TIME, PY2, PY3
from batchcompute.utils.functions import import_json
from batchcompute.utils.log import get_logger
from batchcompute.resources import Configs 

json = import_json()
logger = get_logger('batchcompute.client.response')

########################
#RESOURCES STATUS CLASS#
########################
class Group(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'DesiredVMCount': NUMBER,
        'ActualVMCount': NUMBER,
        'InstanceType': STRING,
        'ResourceType': STRING,
    }

    def __init__(self, dct):
        super(Group, self).__init__(dct)
Group = add_metaclass(Group, CamelCasedClass)

class Metrics(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'RunningCount': NUMBER,
        'StartingCount': NUMBER,
        'StoppingCount': NUMBER,
        'StoppedCount': NUMBER,
    }

    def __init__(self, dct):
        super(Metrics, self).__init__(dct)
Metrics = add_metaclass(Metrics, CamelCasedClass)

class Cluster(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Id': STRING,
        'OwnerId': NUMBER,
        'Description': STRING,
        'CreationTime': TIME,
        'State': STRING,
        'InstanceType': STRING,
        'ImageId': STRING,
        'UserData': dict,
        'Configs': (Configs, dict),
        'Groups': dict,
        'OperationLogs': list,
        'Metrics': (Metrics, dict),
    }

    def __init__(self, dct):
        super(Cluster, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Cluster, self).setproperty
        if key == 'Groups':
            new_value = {}
            for group_name in value:
                new_value[group_name] = self._validate_group(value[group_name])
        elif key == 'Configs' and isinstance(value, dict):
            new_value = Configs(value)
        elif key == 'Metrics' and isinstance(value, dict):
            new_value = Metrics(value)
        else:
            new_value = value
        super_set(key, new_value)

    def _validate_group(self, group):
        return copy.deepcopy(group) if isinstance(group, Group) else Group(group)

    def get_group(self, group_name):
        if group_name in self._d['Groups']:
            return self._d['Groups'][group_name]
        else:
            raise KeyError(''''%s' is not a valid group name''' % group_name)

    if PY2:
        def __cmp__(self, other):
            if isinstance(other, self.descriptor_map['Id']):
                other_cluster_id = other
            else:
                other_cluster_id = other['Id']
            return cmp(self['Id'], other_cluster_id)

    if PY3:
        def __lt__(self, other):
            if isinstance(other, self.descriptor_map['Id']):
                other_cluster_id = other
            else:
                other_cluster_id = other['Id']
            return self['Id'] < other_cluster_id

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['Id']):
            other_cluster_id = other
        else:
            other_cluster_id = other['Id']
        return self['Id'] == other_cluster_id
Cluster = add_metaclass(Cluster, CamelCasedClass)

class ClusterInstance(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'Id': STRING,
        'Hint': STRING,
        'State': STRING,
        'IpAddress': STRING,
        'CreationTime': TIME,
    }

    def __init__(self, dct):
        super(ClusterInstance, self).__init__(dct)
ClusterInstance = add_metaclass(ClusterInstance, CamelCasedClass)

class TaskMetrics(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'WaitingCount': NUMBER,
        'RunningCount': NUMBER,
        'FinishedCount': NUMBER,
        'FailedCount': NUMBER,
        'StoppedCount': NUMBER,
    }

    def __init__(self, dct):
        super(TaskMetrics, self).__init__(dct)
TaskMetrics = add_metaclass(TaskMetrics, CamelCasedClass)

class InstanceMetrics(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'WaitingCount': NUMBER,
        'RunningCount': NUMBER,
        'FinishedCount': NUMBER,
        'FailedCount': NUMBER,
        'StoppedCount': NUMBER,
    }

    def __init__(self, dct):
        super(InstanceMetrics, self).__init__(dct)
InstanceMetrics = add_metaclass(InstanceMetrics, CamelCasedClass)

class Job(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Id': STRING,
        'Priority': NUMBER,
        'Owner': STRING,
        'State': STRING,
        'Message': STRING,
        'CreationTime': TIME, 
        'StartTime': TIME, 
        'EndTime': TIME, 
        'TaskMetrics': (TaskMetrics, dict),
        'InstanceMetrics': (InstanceMetrics, dict)
    }

    def __init__(self, dct):
        super(Job, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Job, self).setproperty
        if key == 'TaskMetrics' and isinstance(value, dict):
            new_value = TaskMetrics(value)
        elif key == 'InstanceMetrics' and isinstance(value, dict):
            new_value = InstanceMetrics(value)
        else:
            new_value = value
        super_set(key, new_value)

    if PY2:
        def __cmp__(self, other):
            '''
            Used as method to sort a collection of Job in Python 2.

            Build-in functions `cmp` and `__cmp__` were deprecated since Python
            3.
            '''
            if isinstance(other, self.descriptor_map['Id']):
                other_job_id = other
            else:
                other_job_id = other['Id']
            return cmp(self['Id'], other_job_id)

    if PY3:
        def __lt__(self, other):
            '''
            Used as method to sort a collection of Job in Python 3.
            '''
            if isinstance(other, self.descriptor_map['Id']):
                other_job_id = other
            else:
                other_job_id = other.Id
            return self.Id < other_job_id

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['Id']):
            other_job_id = other
        else:
            other_job_id = other['Id']
        return self['Id'] == other_job_id
Job = add_metaclass(Job, CamelCasedClass)

class Task(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'TaskName': STRING,
        'State': STRING,
        'StartTime': TIME,
        'EndTime': TIME,
        'InstanceMetrics': (InstanceMetrics, dict),
    }

    def __init__(self, dct):
        super(Task, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Task, self).setproperty
        if key == 'InstanceMetrics' and isinstance(value, dict):
            new_value = InstanceMetrics(value)
        else:
            new_value = value
        super_set(key, new_value)

    if PY2:
        def __cmp__(self, other):
            if isinstance(other, self.descriptor_map['TaskName']):
                other_task_name = other
            else:
                other_task_name = other.TaskName
            return cmp(self['TaskName'], other_task_name)

    if PY3:
        def __lt__(self, other):
            if isinstance(other, self.descriptor_map['TaskName']):
                other_task_name = other
            else:
                other_task_name = other.TaskName
            return self.TaskName < other_task_name 

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['TaskName']):
            other_task_name = other
        else:
            other_task_name = other.TaskName
        return self.TaskName == other_task_name 
Task = add_metaclass(Task, CamelCasedClass)

class Disk(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'ECSSnapshotId': STRING,
    }

    def __init__(self, dct):
        super(Disk, self).__init__(dct)
Disk = add_metaclass(Disk, CamelCasedClass)

class Image(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Id': STRING,
        'Description': STRING,
        'CreationTime': TIME,
        'OwnerId': NUMBER,
        'State': STRING,
        'OS': STRING,
        'ECSImageId': STRING,
        'DiskDeviceMapping': dict,
    }

    def __init__(self, dct):
        super(Image, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Image, self).setproperty
        if key == 'DiskDeviceMapping':
            new_value = {}
            for disk_name in value:
                new_value[disk_name] = self._validate_disk(value[disk_name])
        else:
            new_value = value
        super_set(key, new_value)

    def _validate_disk(self, disk):
        return copy.deepcopy(disk) if isinstance(disk, Disk) else Disk(disk)

    if PY2:
        def __cmp__(self, other):
            if isinstance(other, self.descriptor_map['Id']):
                other_image_id = other
            else:
                other_image_id = other['Id']
            return cmp(self['Id'], other_image_id)

    if PY3:
        def __lt__(self, other):
            if isinstance(other, self.descriptor_map['Id']):
                other_image_id = other
            else:
                other_image_id = other['Id']
            return self['Id'] < other_image_id
Image = add_metaclass(Image, CamelCasedClass)

class Result(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'ExitCode': NUMBER,
        'ErrorCode': STRING,
        'ErrorMessage': STRING,
        'Detail': STRING,
    }

    def __init__(self, dct):
        super(Result, self).__init__(dct)
Result = add_metaclass(Result, CamelCasedClass)

class Instance(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'InstanceId': NUMBER,
        'State': STRING,
        'StartTime': TIME,
        'EndTime': TIME,
        'RetryCount': NUMBER,
        'Progress': NUMBER,
        'StdoutRedirectPath': STRING,
        'StderrRedirectPath': STRING,
        'Result': (Result, dict)
    }

    def __init__(self, dct):
        super(Instance, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Instance, self).setproperty
        if key == 'Result' and isinstance(value, dict):
            new_value = Result(value)
        else:
            new_value = value
        super_set(key, new_value)

    if PY2:
        def __cmp__(self, other):
            if isinstance(other, self.descriptor_map['InstanceId']):
                other_instance_id = other
            else:
                other_instance_id = other['InstanceId']
            return cmp(self['InstanceId'], other_instance_id)

    if PY3:
        def __lt__(self, other):
            if isinstance(other, self.descriptor_map['InstanceId']):
                other_instance_id = other
            else:
                other_instance_id = other['InstanceId']
            return self['InstanceId'] < other_instance_id

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['InstanceId']):
            other_instance_id = other
        else:
            other_instance_id = other['InstanceId']
        return self['InstanceId'] == other_instance_id
Instance = add_metaclass(Instance, CamelCasedClass)

# Add CamelCasedClass metaclass to all resource status classes.


################
#RESPONSE CLASS#
################

class RawResponse(object):
    '''
    Base class for all client response subclasses.

    Mainly suppulys `StatusCode`, `RequestId` and `Date` property and methods
    to retrive them.

    '''
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'StatusCode': NUMBER,
        'RequestId': STRING,
        'Date': STRING,
    }

    def __init__(self, response, human_readable):
        self._d = {}

        self.setproperty('StatusCode', response.status)
        self.setproperty('RequestId', response.getheader('request-id', ''))
        self.setproperty('Date', response.getheader('date'))

        response_body = response.read()
        logger.debug("Raw data recieved from batchcompute service: %s", response_body)
        self.content = remap(response_body, human_readable)

    def getproperty(self, key):
        return self._d[key]

    def setproperty(self, key, value):
        if key in self.descriptor_map:
            if isinstance(value, self.descriptor_map[key]):
                self._d[key] = value
            else:
                raise TypeError('Property %s must be type of %s, actual value: %s'%(key,
                                str(self.descriptor_map[key]), str(value)))

    if PY2:
        def __str__(self):
            return json.dumps(self._d, indent=4) 
        __repr__ = __str__

    if PY3:
        def __bytes__(self):
            return json.dumps(self._d, indent=4) 
        __repr__ = __bytes__
RawResponse = add_metaclass(RawResponse, CamelCasedClass)


class CreateResponse(RawResponse):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'Id': STRING,
    }
    descriptor_map.update(RawResponse.descriptor_map)

    def __init__(self, response, human_readable):
        super(CreateResponse, self).__init__(response, human_readable)
        self.setproperty('Id', self.content['Id'])
CreateResponse = add_metaclass(CreateResponse, CamelCasedClass)

class ActionResponse(RawResponse):
    '''
    Response for operations on jobs(Stop, Start, delete).
    '''
    def __init__(self, response, human_readable):
        super(ActionResponse, self).__init__(response, human_readable)


class GetResponse(RawResponse):
    '''
    Response for get operations on jobs, tasks or images.
    '''
    def __init__(self, response, type_, human_readable):
        super(GetResponse, self).__init__(response, human_readable)
        # Instantiation the real resource status class with the http body(
        # usually a json formatted string) returned by BatchCompute service.
        self._container = type_(self.content)

    def __getattr__(self, attr):
        return getattr(self._container, attr)

    if PY2:
        def __str__(self):
            return self._container.__str__()
        __repr__ = __str__

    if PY3:
        def __bytes__(self):
            return self._container.__bytes__()
        __repr__ = __bytes__


class ListResponse(RawResponse):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'NextMarker': STRING + NUMBER,
        'Items': list
    }
    descriptor_map.update(RawResponse.descriptor_map)

    def __init__(self, response, type_, human_readable):
        super(ListResponse, self).__init__(response, human_readable)
        self._container = [item for item in map(type_, self.content['Items'])]
        self.setproperty('Items', self._container)
        self.setproperty('NextMarker', self.content['NextMarker'])

    def __getattr__(self, attr):
        return getattr(self._container, attr)

    def __iter__(self):
        return iter(self._container)

    def __getitem__(self, index_or_slice):
        return self._container[index_or_slice]

    def __len__(self):
        return len(self._container)

    if PY2:
        def __str__(self):
            return json.dumps(self._d, indent=4, cls=BatchEncoder)
        __repr__ = __str__

    if PY3:
        def __bytes__(self):
            return json.dumps(self._d, indent=4, cls=BatchEncoder)
        __repr__ = __bytes__
ListResponse = add_metaclass(ListResponse, CamelCasedClass)
