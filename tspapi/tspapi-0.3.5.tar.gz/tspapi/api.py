#
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

import os
import json
import logging
from tspapi.api_call import ApiCall
import tspapi.measurement
from tspapi.measurement import Measurement
import tspapi.metric
import tspapi.event
from tspapi.source import Source
from tspapi.source import Sender

logger = logging.getLogger(__name__)


class API(ApiCall):

    def __init__(self, api_host=None, email=None, api_token=None):
        (api_host, email, api_token) = self._get_environment(api_host, email, api_token)
        ApiCall.__init__(self, api_host=api_host, email=email, api_token=api_token)

    def _get_environment(self, api_host, email, api_token):
        """
        Gets the configuration stored in environment variables
        """
        if email is None and 'TSP_EMAIL' in os.environ:
            email = os.environ['TSP_EMAIL']
        if api_token is None and 'TSP_API_TOKEN' in os.environ:
            api_token = os.environ['TSP_API_TOKEN']
        if api_host is None and 'TSP_API_HOST' in os.environ:
            api_host = os.environ['TSP_API_HOST']
        else:
            api_host = 'api.truesight.bmc.com'

        return api_host, email, api_token

    def measurement_create(self,
                           metric=None,
                           value=None,
                           source=None,
                           timestamp=None,
                           properties=None):
        """
        Creates a new measurement in TrueSight Pulse instance.

        :param metric: Identifies the metric to use to add a measurement
        :param value: Value of the measurement
        :param source: Origin of the measurement
        :param timestamp: Time of the occurrence of the measurement
        :param properties: Properties of the measurement
        :return: None
        """

        if metric is None:
            raise ValueError('metrics not specified')

        if value is None:
            raise ValueError('value not specified')
        self._method = 'POST'
        payload = {}
        payload['metric'] = metric
        payload['measure'] = float(value)
        if source is not None:
            payload['source'] = source
        if timestamp is not None:
            payload['timestamp'] = Measurement.parse_timestamp(timestamp)
        if properties is not None:
            payload['metadata'] = properties
        self._data = json.dumps(payload, sort_keys=True)
        self._headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        self._path = "v1/measurements"
        self._api_call()

    def measurement_create_batch(self, measurements):
        """
        Creates measurements from an array of Measurements instances.

        measurements = []
        measurements.append(Measurement())
        measurements.append(Measurement())
        api.measurement_create_batch(measurements)

        :param measurements: List of measurements
        :return: None
        """
        self._method = 'POST'
        self._data = json.dumps(measurements, default=tspapi.measurement.serialize_instance)
        self._headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        self._path = "v1/measurements"
        self._api_call()

    def measurement_get(self,
                        source=None,
                        metric='CPU',
                        start=None,
                        end=None,
                        aggregate='avg',
                        sample=1):
        self._method = 'GET'
        self._data = None
        self._url_parameters = {"source": source,
                                "start": start,
                                "aggregate": aggregate,
                                "sample": sample
                                }

        if start is None:
            raise ValueError("start is not value")
        if end is not None:
            self._url_parameters['end'] = end
        self._path = 'v1/measurements/{0}'.format(metric)
        result = self._api_call(handle_results=tspapi.measurement.measurement_get_handle_results, context=metric)
        return result

    def metric_create(self,
                      name=None,
                      display_name=None,
                      display_name_short=None,
                      description=None,
                      default_aggregate='avg',
                      default_resolution=1000,
                      unit='number',
                      is_disabled=False,
                      _type=None):
        """
        Creates a new metric definition
        :param name:
        :param display_name:
        :param display_name_short:
        :param description:
        :param default_aggregate:
        :param default_resolution:
        :param unit:
        :param is_disabled:
        :param _type:
        :return:
        """

        if name is None:
            raise ValueError("name not specified")

        if display_name is None:
            display_name = name

        if display_name_short is None:
            display_name_short = name

        if description is None:
            description = name

        metric = {
            "name": name,
            "displayName": display_name,
            "displayNameShort": display_name_short,
            "description": description,
            "defaultAggregate": default_aggregate,
            "defaultResolutionMS": default_resolution,
            "unit": unit,
            "isDisabled": is_disabled,
            "type": _type
        }

        self._method = 'POST'
        self._data = json.dumps(metric)
        self._headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        self._path = "v1/metrics"
        result = self._api_call(handle_results=tspapi.metric.metric_get_handle_results)
        return result

    def metric_create_batch(self, metrics):
        """
        Creates multiple metric definitions
        :param metrics:
        :return:
        """
        self._method = 'POST'
        self._data = json.dumps(metrics, default=tspapi.metric.serialize_instance)
        self._headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        self._path = "v1/batch/metrics"
        result = self._api_call(handle_results=tspapi.metric.metric_batch_get_handle_results)
        return result

    def metric_delete(self, name=None, remove_alarms=False):
        """
        Deletes a metric definition from an account
        :param name: Name of the metric to delete
        :param remove_alarms: Set to true to remove the associated alarms
        :return: None
        """
        if name is None:
            raise ValueError("name not specified")
        self._method = 'DELETE'
        self._headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        data = {
            "removeAlarms": remove_alarms
        }
        self._data = json.dumps(data)
        self._path = "v1/metrics/{0}".format(name)
        self._api_call()

    def metric_get(self, enabled=False, custom=False):
        """
        Fetch the metric definitions from an account
        :param enabled: Filter the list to only return enabled metrics
        :param custom: Filter the list to only return custom metrics
        :return: List of metric definition instances
        """
        self._method = 'GET'
        self._data = None
        self._path = "v1/metrics"
        self._url_parameters = {"enabled": enabled, "custom": custom}
        result = self._api_call(handle_results=tspapi.metric.metric_batch_get_handle_results)
        return result

    def metric_update(self,
                      name=None,
                      display_name=None,
                      display_name_short=None,
                      description=None,
                      default_aggregate=None,
                      default_resolution=None,
                      unit=None,
                      is_disabled=None,
                      _type=None):

        payload = {}
        if display_name is not None:
            payload['displayName'] = display_name

        if display_name_short is not None:
            payload['displayNameShort'] = display_name_short

        if description is not None:
            payload['description'] = description

        if default_aggregate is not None:
            payload['defaultAggregate'] = default_aggregate

        if default_resolution is not None:
            payload['defaultResolutionMS'] = default_resolution

        if unit is not None:
            payload['unit'] = unit

        if is_disabled is not None:
            payload['isDisabled'] = is_disabled

        if _type is not None:
            payload['type'] = _type

        self._path = "v1/metrics"
        self._method = 'PUT'
        self._data = json.dumps(payload)
        self._path = "v1/metrics/{0}".format(name)
        result = self._api_call(handle_results=tspapi.metric.metric_get_handle_results)
        return result

    def event_create(self,
                     created_at=None,
                     event_class=None,
                     fingerprint_fields=None,
                     message=None,
                     properties=None,
                     sender=None,
                     severity='INFO',
                     source=None,
                     status='OPEN',
                     tags=None,
                     title=None,
                     ):
        """
        Creates an event in an account
        :param created_at:
        :param event_class:
        :param fingerprint_fields:
        :param message:
        :param properties:
        :param sender:
        :param severity:
        :param source:
        :param status:
        :param tags:
        :param title:
        :return:
        """

        if title is None:
            raise ValueError('title not specified')

        if source is None:
            raise ValueError('source not specified')

        if fingerprint_fields is None:
            raise ValueError('fingerprint fields not specified')

        payload = {}

        if created_at is not None:
            payload['createdAt'] = Measurement.parse_timestamp(created_at)

        if event_class is not None:
            payload['eventClass'] = event_class

        if fingerprint_fields is not None:
            payload['fingerprintFields'] = fingerprint_fields

        if message is not None:
            payload['message'] = message

        if properties is not None:
            payload['properties'] = properties

        if sender is not None:
            if not isinstance(sender, Sender):
                raise ValueError('sender is not a Sender instance')
            else:
                payload['sender'] = {}
                payload['sender']['ref'] = sender.ref
                payload['sender']['type'] = sender.type
                payload['sender']['name'] = sender.name

        if severity is not None:
            payload['severity'] = severity

        if source is not None:
            if not isinstance(source, Source):
                raise ValueError('source is not a Source instance')
            else:
                payload['source'] = {}
                payload['source']['ref'] = source.ref
                payload['source']['type'] = source.type
                payload['source']['name'] = source.name

        if status is not None:
            payload['status'] = status

        if tags is not None:
            payload['tags'] = tags

        if title is not None:
            payload['title'] = title

        self._method = 'POST'
        self._data = json.dumps(payload)
        self._headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        self._path = 'v1/events'
        self._api_call(handle_results=tspapi.event.event_create_handle_results,
                       good_response=tspapi.event.event_create_good_response)

    def event_get(self):
        pass

    def event_list(self):
        """
        Lists the events in your account
        :return:
        """
        self._method = 'GET'
        self._data = None
        self._headers = {"Accept": "application/json"}
        self._path = "v1/events"
        result = self._api_call(handle_results=tspapi.event.event_get_handle_results)
        return result

    def hostgroup_create(self, name, sources=[]):
        """
        Creates a host group or filter
        :param name: Name of the host group/filter
        :param sources: An array of sources to included in the host group/filter
        :return:
        """
        payload = {}
        payload['name'] = name
        payload['hostnames'] = sources

        self._method = 'POST'
        self._data = json.dumps(payload)
        self._headers = {'Content-Type': 'application/json', "Accept": "application/json"}
        self._path = "v1/hostgroups"
        self._api_call()
