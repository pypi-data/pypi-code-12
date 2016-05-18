""" standard """
import dateutil.parser
import time
import uuid
from BatchJobObject import BatchJobObject

""" custom """
from GroupObject import GroupObject
from TaskObject import TaskObject
from VictimObject import VictimObject

from Config.ResourceType import ResourceType
from Config.FilterOperator import FilterOperator
from ErrorCodes import ErrorCodes


class Resource(object):
    """ """

    def __init__(self, tc_obj):
        """ """
        # instance of the ThreatConnect object
        self.tc = tc_obj
        self.tcl = self.tc.tcl

        # filtered resource object list
        self._objects = []
        self._objects_dict = {}

        # master resource object list
        self._master_objects = []

        # filtered resource indexes
        self._object_res_id_idx = {}
        self._object_res_name_idx = {}

        # master resource indexes
        self._master_res_id_idx = {}
        self._master_object_id_idx = {}

        # Post Filter Indexes
        self._attribute_idx = {}
        self._confidence_idx = {}
        self._date_added_idx = {}
        self._file_type_idx = {}
        self._last_modified_idx = {}
        self._name_idx = {}
        self._rating_idx = {}
        self._threat_assess_confidence_idx = {}
        self._threat_assess_rating_idx = {}
        self._tag_idx = {}
        self._type_idx = {}

        # defaults
        self._api_response = []
        self._commit_queue = {}
        self._current_filter = None
        self._error = False
        self._error_messages = []
        self._filter_class = None
        self._filter_objects = []
        self._http_method = None
        self._id_mapping = {}
        self._max_results = None
        self._method = None
        self._object_class = None
        self._request_object = None
        self._resource_object = None
        self._resource_type = None
        self._result_count = 0
        self._status_code = []
        self._uris = []

    def add(self, resource_name, owner=None):
        """ add resource to resource container """
        # generate unique temporary id
        resource_id = uuid.uuid4().int

        if self._resource_type == ResourceType.VICTIMS:
            resource_object = VictimObject()
        elif self._resource_type == ResourceType.BATCH_JOBS:
            resource_object = BatchJobObject()
        elif self._resource_type == ResourceType.TASKS:
            resource_object = TaskObject()
        else:
            resource_object = GroupObject(self._resource_type)

        resource_object.set_id(resource_id, False)  # set resource id
        if owner is not None:
            resource_object.set_owner_name(owner)  # set resource name
        if resource_name is not None:
            resource_object.set_name(resource_name, False)  # set resource name
        resource_object.set_phase(1)  # set resource api action

        # return resource object
        return self._method_wrapper(resource_object)

    def update(self, resource_id, owner=None):
        # resource object
        if self._resource_type == ResourceType.VICTIMS:
            resource_obj = VictimObject()
        elif self._resource_type == ResourceType.BATCH_JOBS:
            resource_obj = BatchJobObject()
        else:
            resource_obj = GroupObject(self._resource_type)

        resource_obj.set_id(int(resource_id))
        if owner is not None:
            resource_obj.set_owner_name(owner)
        resource_obj.set_phase(2)  # set resource api phase (1 = add)

        # return object for modification
        return self._method_wrapper(resource_obj)

    def delete(self, resource_id, owner=None):
        # resource object
        if self._resource_type == ResourceType.VICTIMS:
            resource_obj = VictimObject()
        else:
            resource_obj = GroupObject(self._resource_type)

        resource_obj.set_id(resource_id)
        resource_obj.set_owner_name(owner)
        resource_obj.set_phase(3)  # set resource api phase (3 = delete)

        # call delete to queue call
        wrapper = self._method_wrapper(resource_obj)
        wrapper.delete()

    def add_obj(self, data_obj):
        """add object to resource instance"""
        has_id = False

        # update id index
        if hasattr(data_obj, 'id'):
            resource_id = data_obj.id
            if resource_id is not None:
                # signify that id will be used a index key
                has_id = True
                if resource_id not in self._object_res_id_idx:
                    self._object_res_id_idx.setdefault(resource_id, data_obj)
                    self._objects.append(data_obj)
                    self._objects_dict.setdefault(id(data_obj), data_obj)

        # use name if id is not available
        if hasattr(data_obj, 'name'):
            resource_name = data_obj.name
            if resource_name is not None:
                if resource_name not in self._object_res_name_idx:
                    self._object_res_name_idx.setdefault(resource_name, []).append(data_obj)

                    # only do this if the object has no id
                    if not has_id:
                        self._objects.append(data_obj)

    def add_filter(self, resource_type=None):
        """ """
        if resource_type is not None:
            filter_obj = self._filter_class(self.tc, resource_type)
        else:
            filter_obj = self._filter_class(self.tc)

        # append filter object
        self._filter_objects.append(filter_obj)

        return filter_obj

    def get_resource_by_identity(self, data):
        if data in self._master_object_id_idx:
            return self._master_object_id_idx[data]

    def add_master_resource_obj(self, data_obj, index):
        """ """
        resource_object_id = id(data_obj)
        # has_id = False
        duplicate = True

        # update master resource object id index
        self._master_object_id_idx.setdefault(id(data_obj), data_obj)

        # handle file hashed by making all index a dict
        if isinstance(index, dict):
            init = True
            for indx in index.values():
                if indx is None:
                    continue

                if indx.upper() not in self._master_res_id_idx:
                    if init:  # only add file indicator one time
                        self._master_objects.append(data_obj)
                        init = False
                    self._master_res_id_idx.setdefault(indx.upper(), data_obj)
                    duplicate = False
                else:
                    resource_object_id = id(self._master_res_id_idx[indx])
        else:
            if index not in self._master_res_id_idx:
                self._master_objects.append(data_obj)
                self._master_res_id_idx.setdefault(index, data_obj)
                duplicate = False
            else:
                resource_object_id = id(self._master_res_id_idx[index])

        #
        # post filters indexes
        #
        if not duplicate:
            #
            # confidence index
            #
            if hasattr(data_obj, 'confidence'):
                if data_obj.confidence is not None:
                    self._confidence_idx.setdefault(
                        data_obj.confidence, []).append(data_obj)

            #
            # date added index
            #
            if hasattr(data_obj, 'date_added'):
                if data_obj.date_added is not None:
                    date_added = data_obj.date_added
                    date_added = dateutil.parser.parse(date_added)
                    date_added_seconds = int(time.mktime(date_added.timetuple()))
                    self._date_added_idx.setdefault(date_added_seconds, []).append(data_obj)

            #
            # file type index
            #
            if hasattr(data_obj, 'file_type'):
                if data_obj.file_type is not None:
                    self._file_type_idx.setdefault(data_obj.file_type, []).append(data_obj)

            #
            # last modified index
            #
            if hasattr(data_obj, 'last_modified'):
                if data_obj.last_modified is not None:
                    last_modified = data_obj.last_modified
                    last_modified = dateutil.parser.parse(last_modified)
                    last_modified_seconds = int(time.mktime(last_modified.timetuple()))
                    self._last_modified_idx.setdefault(last_modified_seconds, []).append(data_obj)

            #
            # name index
            #
            if hasattr(data_obj, 'name'):
                if data_obj.name is not None:
                    self._name_idx.setdefault(
                        data_obj.name, []).append(data_obj)

            #
            # rating index
            #
            if hasattr(data_obj, 'rating'):
                if data_obj.rating is not None:
                    self._rating_idx.setdefault(
                        data_obj.rating, []).append(data_obj)

            #
            # threat assess confidence index
            #
            if hasattr(data_obj, 'threat_assess_confidence'):
                if data_obj.threat_assess_confidence is not None:
                    self._threat_assess_confidence_idx.setdefault(
                        data_obj.threat_assess_confidence, []).append(data_obj)

            #
            # threat assess rating index
            #
            if hasattr(data_obj, 'threat_assess_rating'):
                if data_obj.threat_assess_rating is not None:
                    self._threat_assess_rating_idx.setdefault(
                        data_obj.threat_assess_rating, []).append(data_obj)

            #
            # type index
            #
            if hasattr(data_obj, 'type'):
                if data_obj.type is not None:
                    self._type_idx.setdefault(data_obj.type, []).append(data_obj)

            #
            # attributes (nested object)
            #
            if hasattr(data_obj, 'attributes'):
                if len(data_obj.attributes) > 0:
                    for attribute_obj in data_obj.attributes:
                        self._attribute_idx.setdefault(
                            attribute_obj.type, []).append(data_obj)

            #
            # tags (nested object)
            #
            if hasattr(data_obj, 'tags'):
                if len(data_obj.tags) > 0:
                    for tag_obj in data_obj.tags:
                        self._tag_idx.setdefault(
                            tag_obj.name, []).append(data_obj)

        return resource_object_id

    #
    # Post Filter Methods
    #

    def filter_attribute(self, data, operator, description):
        """Post Filter"""
        if operator == FilterOperator.EQ:
            if data in self._attribute_idx:
                for data_obj in self._attribute_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        else:
            for key, data_obj_list in self._attribute_idx.items():
                if operator.value(key, data):
                    for data_obj in data_obj_list:
                        data_obj.add_matched_filter(description)
                        yield data_obj

    def filter_confidence(self, data, operator, description):
        """Post Filter"""
        if operator == FilterOperator.EQ:
            if data in self._confidence_idx:
                for data_obj in self._confidence_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        else:
            for key, data_obj_list in self._confidence_idx.items():
                if operator.value(int(key), int(data)):
                    for data_obj in data_obj_list:
                        data_obj.add_matched_filter(description)
                        yield data_obj

    def filter_date_added(self, data, operator, description):
        """Post Filter"""
        if operator == FilterOperator.EQ:
            if data in self._date_added_idx:
                for data_obj in self._date_added_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        else:
            for key, data_obj_list in self._date_added_idx.items():
                if operator.value(key, data):
                    for data_obj in data_obj_list:
                        data_obj.add_matched_filter(description)
                        yield data_obj

    def filter_file_type(self, data, operator, description):
        """Post Filter"""
        if operator == FilterOperator.EQ:
            if data in self._file_type_idx:
                for data_obj in self._file_type_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        else:
            for key, data_obj_list in self._file_type_idx.items():
                if operator.value(key, data):
                    for data_obj in data_obj_list:
                        data_obj.add_matched_filter(description)
                        yield data_obj

    def filter_last_modified(self, data, operator, description):
        """Post Filter"""
        if operator == FilterOperator.EQ:
            if data in self._last_modified_idx:
                for data_obj in self._last_modified_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        else:
            for key, data_obj_list in self._last_modified_idx.items():
                if operator.value(key, data):
                    for data_obj in data_obj_list:
                        data_obj.add_matched_filter(description)
                        yield data_obj

    def filter_name(self, data, operator, description):
        """Post Filter"""
        if operator == FilterOperator.EQ:
            if data in self._name_idx:
                for data_obj in self._name_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        """ NO OTHER STRING COMPARISON SUPPORTED AT THIS TIME """
        # else:
        #     for key, data_obj_list in self._rating_idx.items():
        #         if operator.value(float(key), float(data)):
        #             for data_obj in data_obj_list:
        #                 data_obj.add_matched_filter(description)
        #                 yield data_obj

    def filter_rating(self, data, operator, description):
        """Post Filter"""
        if operator == FilterOperator.EQ:
            if data in self._rating_idx:
                for data_obj in self._rating_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        else:
            for key, data_obj_list in self._rating_idx.items():
                if operator.value(float(key), float(data)):
                    for data_obj in data_obj_list:
                        data_obj.add_matched_filter(description)
                        yield data_obj

    def filter_threat_assess_confidence(self, data, operator, description):
        """Post Filter"""
        if operator == FilterOperator.EQ:
            if data in self._threat_assess_confidence_idx:
                for data_obj in self._threat_assess_confidence_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        else:
            for key, data_obj_list in self._threat_assess_confidence_idx.items():
                if operator.value(float(key), float(data)):
                    for data_obj in data_obj_list:
                        data_obj.add_matched_filter(description)
                        yield data_obj

    def filter_threat_assess_rating(self, data, operator, description):
        """Post Filter"""
        if operator == FilterOperator.EQ:
            if data in self._threat_assess_rating_idx:
                for data_obj in self._threat_assess_rating_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        else:
            for key, data_obj_list in self._threat_assess_rating_idx.items():
                if operator.value(float(key), float(data)):
                    for data_obj in data_obj_list:
                        data_obj.add_matched_filter(description)
                        yield data_obj

    def filter_tag(self, data, operator, description):
        """Post Filter"""
        self.tcl.debug('len tag index: {0}'.format(len(self._tag_idx)))
        if operator == FilterOperator.EQ:
            if data in self._tag_idx:
                for data_obj in self._tag_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        else:
            for key, data_obj_list in self._tag_idx.items():
                if operator.value(key, data):
                    for data_obj in data_obj_list:
                        data_obj.add_matched_filter(description)
                        yield data_obj

    def filter_type(self, data, operator, description):
        """Post Filter"""
        if operator == FilterOperator.EQ:
            if data in self._type_idx:
                for data_obj in self._type_idx[data]:
                    data_obj.add_matched_filter(description)
                    yield data_obj
        else:
            for key, data_obj_list in self._type_idx.items():
                if operator.value(key, data):
                    for data_obj in data_obj_list:
                        data_obj.add_matched_filter(description)
                        yield data_obj

    def get_resource_by_id(self, data):
        """ """
        if data in self._master_res_id_idx:
            return self._method_wrapper(self._master_res_id_idx[data])
        elif data.upper() in self._master_res_id_idx:
            return self._method_wrapper(self._master_res_id_idx[data.upper()])
        else:
            self.tcl.warning(ErrorCodes.e10012.value.format(data))
            return None

    def get_resource_by_name(self, data):
        """ """
        if data in self._master_res_id_idx:
            return self._method_wrapper(self._master_res_id_idx[data])
        else:
            self.tcl.warning(ErrorCodes.e10013.value.format(data))
            return None

    def retrieve(self):
        """ """
        self.tc.api_filter_handler(self, self._filter_objects)
        del self._filter_objects[:]  # clear filters
        return self  # if class is called directly

    def add_commit_queue(self, resource_id, request_obj):
        """ add request object to process during commit """
        self._commit_queue.setdefault(resource_id, []).append(request_obj)

    def commit_queue(self, resource_id):
        if resource_id in self._commit_queue:
            for ro in self._commit_queue[resource_id]:
                yield ro

    def clear_commit_queue(self):
        """ clear request object """
        del self._commit_queue
        self._commit_queue = []

    def clear_commit_queue_id(self, resource_id):
        """ clear request object by id"""
        if resource_id in self._commit_queue:
            del self._commit_queue[resource_id]

    def add_id_mapping(self, temp_id, api_id):
        """ store temporary id to api id mapping """
        self._id_mapping.setdefault(temp_id, api_id)

    def clear_id_mapping(self):
        """ clear temporary id to api id mapping """
        del self._id_mapping
        self._id_mapping = {}

    def _method_wrapper(self, obj):
        """ """
        pass

    def __iter__(self):
        """ """
        for obj in self._objects:
            yield self._method_wrapper(obj)

    def __len__(self):
        """ """
        return len(self._objects)
