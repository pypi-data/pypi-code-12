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
import requests
import json
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Metric(object):
    def __init__(self,
                 name=None,
                 display_name=None,
                 display_name_short=None,
                 description='',
                 default_aggregate='avg',
                 default_resolution=1000,
                 unit='number',
                 _type=None,
                 is_disabled=False):

        if name is None:
            raise ValueError("name value not specified")

        self._name = name
        self._display_name = display_name if display_name is not None else self._name
        self._display_name_short = display_name_short if display_name_short is not None else self._name
        self._description = description
        self._default_aggregate = default_aggregate
        self._default_resolution = default_resolution
        self._is_disabled = is_disabled
        self._unit = unit
        self._type = _type

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{0}(name='{1}'" \
               ", display_name='{2}'" \
               ", display_name_short='{3}'" \
               ", description='{4}'" \
               ", default_aggregate='{5}'" \
               ", default_resolution={6}" \
               ", unit='{7}'" \
               ", _type='{8}'" \
               ", is_disabled='{9}'" \
               ")".format(
                self.__class__.__name__,
                self._name,
                self._display_name,
                self._display_name_short,
                self._description,
                self._default_aggregate,
                self._default_resolution,
                self._unit,
                self._type,
                self._is_disabled)

    @property
    def name(self):
        return self._name

    @property
    def display_name(self):
        return self._display_name

    @property
    def display_name_short(self):
        return self._display_name_short

    @property
    def description(self):
        return self._description

    @property
    def default_aggregate(self):
        return self._default_aggregate

    @property
    def default_resolution(self):
        return self._default_resolution

    @property
    def is_disabled(self):
        return self._is_disabled

    @property
    def unit(self):
        return self._unit

    @property
    def type(self):
        return self._type


def serialize_instance(obj):
    d = {}
    d['name'] = obj.name
    d['displayName'] = obj.display_name
    d['displayNameShort'] = obj.display_name_short
    d['description'] = obj.description
    d['defaultAggregate'] = obj.default_aggregate
    d['defaultResolutionMS'] = obj.default_resolution
    d['unit'] = obj.unit
    if obj.type is not None:
        d['type'] = obj.type
    d['isDisabled'] = obj.is_disabled
    return d


def metric_get_handle_results(api_result, context=None):
    logging.debug("metric_get_handle_results")
    metric = None
    if api_result.status_code == requests.codes.ok:
        results = json.loads(api_result.text)
        m = results['result']
        metric = Metric(name=m['name'],
                        display_name=m['displayName'],
                        display_name_short=m['displayNameShort'],
                        description=m['description'],
                        default_aggregate=m['defaultAggregate'],
                        default_resolution=m['defaultResolutionMS'],
                        unit=m['unit'],
                        _type=m['type'] if 'type' in m else None,
                        is_disabled=m['isDisabled'])
    return metric


def metric_batch_get_handle_results(api_result, context=None):
    logging.debug("metric_batch_get_handle_results")
    metrics = None
    # Only process if we get HTTP result of 200
    if api_result.status_code == requests.codes.ok:
        results = json.loads(api_result.text)
        metrics = []
        log.debug(api_result.text)
        for metric in results['result']:
            metrics.append(Metric(name=metric['name'],
                                  display_name=metric['displayName'],
                                  display_name_short=metric['displayNameShort'],
                                  description=metric['description'],
                                  default_aggregate=metric['defaultAggregate'],
                                  default_resolution=metric['defaultResolutionMS'],
                                  unit=metric['unit'],
                                  _type=metric['type'] if 'type' in metric else None,
                                  is_disabled=metric['isDisabled']))

    return metrics
