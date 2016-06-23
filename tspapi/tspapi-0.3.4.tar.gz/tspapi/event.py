# Copyright 2016 BMC Software, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
from pprint import pprint
from tspapi import Source
from tspapi import Sender
import requests
import json


def event_create_good_response(status_code):
    """
    Determines what status codes represent a good response from an API call.
    :param status_code: HTTP status code
    :return: Boolean
    """
    return status_code == requests.codes.created or status_code == requests.codes.accepted


class BaseEvent(object):
    def __init__(self, *args, **kwargs):
        self._created_at = kwargs['created_at'] if 'created_at' in kwargs else None
        self._event_id = kwargs['event_id'] if 'event_id' in kwargs else None
        self._event_class = kwargs['event_class'] if 'event_class' in kwargs else None
        self._fingerprint_fields = kwargs['fingerprint_fields'] if 'fingerprint_fields' in kwargs else None
        self._id = kwargs['id'] if 'id' in kwargs else None
        self._message = kwargs['message'] if 'message' in kwargs else None
        self._properties = kwargs['properties'] if 'properties' in kwargs else None
        self._source = kwargs['source'] if 'source' in kwargs else None
        self._sender = kwargs['sender'] if 'sender' in kwargs else None
        self._severity = kwargs['severity'] if 'severity' in kwargs else None
        self._status = kwargs['status'] if 'status' in kwargs else None
        self._tags = kwargs['tags'] if 'tags' in kwargs else None
        self._tenant_id = kwargs['tenant_id'] if 'tenant_id' in kwargs else None
        self._title = kwargs['title'] if 'title' in kwargs else None

        self._received_at = kwargs['received_at'] if 'received_at' in kwargs else None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{0}(created_at={1}" \
               ", event_id='{2}'" \
               ", event_class='{3}'" \
               ", fingerprint_fields='{4}'" \
               ", id='{5}'" \
               ", message='{6}'" \
               ", properties={7}" \
               ", source='{8}'" \
               ", sender='{9}'" \
               ", severity='{10}'" \
               ", status='{11}'" \
               ", tags='{12}'" \
               ", tenant_id={13}" \
               ", title='{14}')".format(
                self.__class__.__name__,
                self._created_at,
                self._event_id,
                self._event_class,
                self._fingerprint_fields,
                self._id,
                self._message,
                self._properties,
                self._source.__repr__() if self._source is not None else None,
                self._sender,
                self._severity,
                self._status,
                self._tags,
                self._tenant_id,
                self._title)

    @property
    def created_at(self):
        return self._created_at

    @property
    def event_class(self):
        return self._event_class

    @property
    def event_id(self):
        return self._event_id

    @property
    def fingerprint_fields(self):
        return self._fingerprint_fields

    @property
    def id(self):
        return self._id

    @property
    def message(self):
        return self._message

    @property
    def properties(self):
        return self._properties

    @property
    def received_at(self):
        return self._received_at

    @property
    def title(self):
        return self._title

    @property
    def sender(self):
        return self._sender

    @property
    def severity(self):
        return self._severity

    @property
    def source(self):
        return self._source

    @property
    def status(self):
        return self._status

    @property
    def tags(self):
        return self._tags

    @property
    def tenant_id(self):
        return self._tenant_id


class RawEvent(BaseEvent):
    def __init__(self, *args, **kwargs):
        super(RawEvent, self).__init__(*args, **kwargs)


class Event(BaseEvent):
    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self._id = kwargs['id'] if 'id' in kwargs else None
        self._times_seen = kwargs['times_seen'] if 'times_seen' in kwargs else None

    @property
    def id(self):
        return self._id

    @property
    def times_seen(self):
        return self._times_seen


def serialize_instance(obj):
    d = {}
    if obj.created_at is not None:
        d['createdAt'] = obj.created_at
    if obj.title is not None:
        d['title'] = obj.title
    if obj.source is not None:
        d['source'] = obj.source.serialize()
    return d


def event_create_handle_results(api_result, context=None):
    # Only process if we get HTTP result of 200
    result = None
    if (api_result.status_code == requests.codes.created or api_result.status_code == requests.codes.accepted)\
            and len(api_result.text) > 0:
        result = json.loads(api_result.text)
    return result


def event_get_handle_results(api_result, context=None):
    logging.debug("event_get_handle_results")
    events = None
    # Only process if we get HTTP result of 200
    if api_result.status_code == requests.codes.ok:
        print(api_result.text)
        results = json.loads(api_result.text)
        events = []

        # Regression in API changed 'results' to 'items'
        # check to handle both
        if 'items' in results:
            results_key = 'items'
        else:
            results_key = 'results'

        for event in results[results_key]:
            if 'sender' in event:
                source = Source.dict_to_source(event['source'])
            else:
                source = None

            if 'sender' in event:
                sender = Source.dict_to_source(event['sender'])
            else:
                sender = None

            if 'event_class' in event:
                event_class = event['event_class']
            else:
                event_class = None

            status = None
            if 'status' in event:
                status = event['status']
            properties = None
            if 'properties' in event:
                properties = event['properties']
            severity = None
            if 'severity' in event:
                severity = event['severity']
            events.append(Event(event_class=event_class,
                                fingerprint_fields=event['fingerprintFields'],
                                first_seen_at=event['firstSeenAt'],
                                id=event['id'],
                                last_seen_at=event['lastSeenAt'],
                                properties=properties,
                                sender=sender,
                                severity=severity,
                                source=source,
                                status=status,
                                tenant_id=['tenantId'],
                                times_seen=event['timesSeen'],
                                title=event['title']))

    return events
