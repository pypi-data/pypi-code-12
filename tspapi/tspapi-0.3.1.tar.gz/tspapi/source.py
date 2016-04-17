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


class Source(object):
    def __init__(self, ref=None, _type=None, name=None, properties=None):
        self._ref = ref
        self._type = _type
        self._name = name
        self._properties = properties

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = []
        s.append('{0}('.format(self.__class__.__name__))
        previous = False
        if self._ref is not None:
            s.append("ref='{0}'".format(self._ref))
            previous = True
        if self._type is not None:
            if previous:
                s.append(",")
            s.append("_type='{0}'".format(self._type))
            previous = True
        if self._name is not None:
            if previous:
                s.append(",")
            s.append("name='{0}'".format(self._name))
            previous = True
        if self._properties is not None:
            if previous:
                s.append(",")
            s.append("properties={0}".format(self._properties))
        s.append(")".format(self._ref))

        return "".join(s)

    @staticmethod
    def dict_to_source(source):
        ref = None
        _type = None
        name = None
        properties = None
        if 'ref' in source:
            ref = source['ref']
        if 'type' in source:
            _type = source['type']
        if 'name' in source:
            name = source['name']
        if 'properties' in source:
            properties = source['properties']
        return Source(ref=ref, _type=_type, name=name, properties=properties)

    @property
    def ref(self):
        return self._ref

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def properties(self):
        return self._properties

    def serialize_instance(self):
        d = {}
        if self.ref is not None:
            d['ref'] = self.ref
        return d

    def serialize(self):
        d = {}
        if self._ref is not None:
            d['ref'] = self._ref
        if self._type is not None:
            d['type'] = self._type
        if self._name is not None:
            d['name'] = self._name
        if self._properties is not None:
            d['properties'] = self._properties
        return d


class Sender(Source):
    def __init__(self, ref=None, _type=None, name=None, properties=None):
        Source.__init__(self, ref=ref, _type=_type, name=name, properties=properties)


def serialize_instance(obj):
    return obj.serialize()
