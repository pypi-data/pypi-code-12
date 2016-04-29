""" standard """
import types
import re
from threatconnect import GroupFilterMethods

""" custom """
from threatconnect.BatchJobObject import BatchJobObjectAdvanced, BatchJobObject
from threatconnect import ApiProperties
from threatconnect.Config.ResourceType import ResourceType
from threatconnect.FilterObject import FilterObject
from threatconnect.Resource import Resource


def parse_batch_job(batch_job_dict, resource_obj=None, api_filter=None, request_uri=None):
    """ """
    # group object
    batch_job = BatchJobObject()

    #
    # standard values
    #
    batch_job.set_id(batch_job_dict['id'])

    #
    # optional values
    #
    if 'status' in batch_job_dict:
        batch_job.set_status(batch_job_dict['status'])
    if 'errorCount' in batch_job_dict:
        batch_job.set_error_count(batch_job_dict['errorCount'])
    if 'successCount' in batch_job_dict:
        batch_job.set_success_count(batch_job_dict['successCount'])
    if 'unprocessCount' in batch_job_dict:
        batch_job.set_unprocess_count(batch_job_dict['unprocessCount'])

    #
    # handle both resource containers and individual objects
    #
    # if resource_obj is not None:
    #     # store the resource object in the master resource object list
    #     roi = resource_obj.add_master_resource_obj(batch_job, batch_job_dict['id'])
    #
    #     # retrieve the resource object and update data
    #     # must be submitted after parameters are set for indexing to work
    #     batch_job = resource_obj.get_resource_by_identity(roi)

    #
    # filter (set after retrieving stored object)
    #
    if api_filter is not None:
        batch_job.add_matched_filter(api_filter)

    #
    # request_uri (set after retrieving stored object)
    #
    if request_uri is not None:
        batch_job.add_request_uri(request_uri)

    return batch_job


class BatchJobs(Resource):

    __slots__ = (
        '_haltOnError',
        '_attributeWriteError',
        '_action'
    )

    def __init__(self, tc_obj):
        super(BatchJobs, self).__init__(tc_obj)
        self._filter_class = BatchJobsFilterObject
        self._resource_type = ResourceType.BATCH_JOBS

    def _method_wrapper(self, resource_object):
        """ """
        return BatchJobObjectAdvanced(self.tc, self, resource_object)
        # return resource_object

    def add(self, resource_name=None, owner=None):
        return super(BatchJobs, self).add(resource_name=None, owner=None)


class BatchJobsFilterObject(FilterObject):
    """ """
    def __init__(self, tc_obj):
        """ """
        super(BatchJobsFilterObject, self).__init__(tc_obj)
        self._owners = []

        # define properties for resource type
        self._resource_type = ResourceType.BATCH_JOBS
        self._resource_properties = ApiProperties.api_properties[self._resource_type.name]['properties']

        #
        # add_obj filter methods
        #
        for method_name in self._resource_properties['filters']:
            if re.findall('add_pf_', method_name):
                self.add_post_filter_names(method_name)
            else:
                self.add_api_filter_name(method_name)
            method = getattr(GroupFilterMethods, method_name)
            setattr(self, method_name, types.MethodType(method, self))

    @ property
    def default_request_object(self):
        """ default request when only a owner filter is provided """
        raise RuntimeError('BatchJobs can only be retrieved by ID')
