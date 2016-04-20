# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helper functions for dealing with Cloud Datastore's Protobuf API.

The non-private functions are part of the API.
"""

import datetime

from google.protobuf import struct_pb2
from google.type import latlng_pb2
import six

from gcloud._helpers import _datetime_to_pb_timestamp
from gcloud._helpers import _pb_timestamp_to_datetime
from gcloud.datastore._generated import entity_pb2 as _entity_pb2
from gcloud.datastore.entity import Entity
from gcloud.datastore.key import Key

__all__ = ('entity_from_protobuf', 'key_from_protobuf')


def _get_meaning(value_pb, is_list=False):
    """Get the meaning from a protobuf value.

    :type value_pb: :class:`gcloud.datastore._generated.entity_pb2.Value`
    :param value_pb: The protobuf value to be checked for an
                     associated meaning.

    :type is_list: bool
    :param is_list: Boolean indicating if the ``value_pb`` contains
                    a list value.

    :rtype: int
    :returns: The meaning for the ``value_pb`` if one is set, else
              :data:`None`.
    :raises: :class:`ValueError <exceptions.ValueError>` if a list value
             has disagreeing meanings (in sub-elements) or has some
             elements with meanings and some without.
    """
    meaning = None
    if is_list:
        # An empty list will have no values, hence no shared meaning
        # set among them.
        if len(value_pb.array_value.values) == 0:
            return None

        # We check among all the meanings, some of which may be None,
        # the rest which may be enum/int values.
        all_meanings = set(_get_meaning(sub_value_pb)
                           for sub_value_pb in value_pb.array_value.values)
        meaning = all_meanings.pop()
        # The value we popped off should have been unique. If not
        # then we can't handle a list with values that have more
        # than one meaning.
        if all_meanings:
            raise ValueError('Different meanings set on values '
                             'within an array_value')
    elif value_pb.meaning:  # Simple field (int32)
        meaning = value_pb.meaning

    return meaning


def _new_value_pb(entity_pb, name):
    """Add (by name) a new ``Value`` protobuf to an entity protobuf.

    :type entity_pb: :class:`gcloud.datastore._generated.entity_pb2.Entity`
    :param entity_pb: An entity protobuf to add a new property to.

    :type name: string
    :param name: The name of the new property.

    :rtype: :class:`gcloud.datastore._generated.entity_pb2.Value`
    :returns: The new ``Value`` protobuf that was added to the entity.
    """
    return entity_pb.properties.get_or_create(name)


def _property_tuples(entity_pb):
    """Iterator of name, ``Value`` tuples from entity properties.

    :type entity_pb: :class:`gcloud.datastore._generated.entity_pb2.Entity`
    :param entity_pb: An entity protobuf to add a new property to.

    :rtype: :class:`generator`
    :returns: An iterator that yields tuples of a name and ``Value``
              corresponding to properties on the entity.
    """
    return six.iteritems(entity_pb.properties)


def entity_from_protobuf(pb):
    """Factory method for creating an entity based on a protobuf.

    The protobuf should be one returned from the Cloud Datastore
    Protobuf API.

    :type pb: :class:`gcloud.datastore._generated.entity_pb2.Entity`
    :param pb: The Protobuf representing the entity.

    :rtype: :class:`gcloud.datastore.entity.Entity`
    :returns: The entity derived from the protobuf.
    """
    key = None
    if pb.HasField('key'):  # Message field (Key)
        key = key_from_protobuf(pb.key)

    entity_props = {}
    entity_meanings = {}
    exclude_from_indexes = []

    for prop_name, value_pb in _property_tuples(pb):
        value = _get_value_from_value_pb(value_pb)
        entity_props[prop_name] = value

        # Check if the property has an associated meaning.
        is_list = isinstance(value, list)
        meaning = _get_meaning(value_pb, is_list=is_list)
        if meaning is not None:
            entity_meanings[prop_name] = (meaning, value)

        # Check if ``value_pb`` was excluded from index. Lists need to be
        # special-cased and we require all ``exclude_from_indexes`` values
        # in a list agree.
        if is_list:
            exclude_values = set(value_pb.exclude_from_indexes
                                 for value_pb in value_pb.array_value.values)
            if len(exclude_values) != 1:
                raise ValueError('For an array_value, subvalues must either '
                                 'all be indexed or all excluded from '
                                 'indexes.')

            if exclude_values.pop():
                exclude_from_indexes.append(prop_name)
        else:
            if value_pb.exclude_from_indexes:
                exclude_from_indexes.append(prop_name)

    entity = Entity(key=key, exclude_from_indexes=exclude_from_indexes)
    entity.update(entity_props)
    entity._meanings.update(entity_meanings)
    return entity


def entity_to_protobuf(entity):
    """Converts an entity into a protobuf.

    :type entity: :class:`gcloud.datastore.entity.Entity`
    :param entity: The entity to be turned into a protobuf.

    :rtype: :class:`gcloud.datastore._generated.entity_pb2.Entity`
    :returns: The protobuf representing the entity.
    """
    entity_pb = _entity_pb2.Entity()
    if entity.key is not None:
        key_pb = entity.key.to_protobuf()
        entity_pb.key.CopyFrom(key_pb)

    for name, value in entity.items():
        value_is_list = isinstance(value, list)
        if value_is_list and len(value) == 0:
            continue

        value_pb = _new_value_pb(entity_pb, name)
        # Set the appropriate value.
        _set_protobuf_value(value_pb, value)

        # Add index information to protobuf.
        if name in entity.exclude_from_indexes:
            if not value_is_list:
                value_pb.exclude_from_indexes = True

            for sub_value in value_pb.array_value.values:
                sub_value.exclude_from_indexes = True

        # Add meaning information to protobuf.
        if name in entity._meanings:
            meaning, orig_value = entity._meanings[name]
            # Only add the meaning back to the protobuf if the value is
            # unchanged from when it was originally read from the API.
            if orig_value is value:
                # For lists, we set meaning on each sub-element.
                if value_is_list:
                    for sub_value_pb in value_pb.array_value.values:
                        sub_value_pb.meaning = meaning
                else:
                    value_pb.meaning = meaning

    return entity_pb


def key_from_protobuf(pb):
    """Factory method for creating a key based on a protobuf.

    The protobuf should be one returned from the Cloud Datastore
    Protobuf API.

    :type pb: :class:`gcloud.datastore._generated.entity_pb2.Key`
    :param pb: The Protobuf representing the key.

    :rtype: :class:`gcloud.datastore.key.Key`
    :returns: a new `Key` instance
    """
    path_args = []
    for element in pb.path:
        path_args.append(element.kind)
        if element.id:  # Simple field (int64)
            path_args.append(element.id)
        # This is safe: we expect proto objects returned will only have
        # one of `name` or `id` set.
        if element.name:  # Simple field (string)
            path_args.append(element.name)

    project = None
    if pb.partition_id.project_id:  # Simple field (string)
        project = pb.partition_id.project_id
    namespace = None
    if pb.partition_id.namespace_id:  # Simple field (string)
        namespace = pb.partition_id.namespace_id

    return Key(*path_args, namespace=namespace, project=project)


def _pb_attr_value(val):
    """Given a value, return the protobuf attribute name and proper value.

    The Protobuf API uses different attribute names based on value types
    rather than inferring the type.  This function simply determines the
    proper attribute name based on the type of the value provided and
    returns the attribute name as well as a properly formatted value.

    Certain value types need to be coerced into a different type (such
    as a `datetime.datetime` into an integer timestamp, or a
    `gcloud.datastore.key.Key` into a Protobuf representation.  This
    function handles that for you.

    .. note::
       Values which are "text" ('unicode' in Python2, 'str' in Python3) map
       to 'string_value' in the datastore;  values which are "bytes"
       ('str' in Python2, 'bytes' in Python3) map to 'blob_value'.

    For example:

    >>> _pb_attr_value(1234)
    ('integer_value', 1234)
    >>> _pb_attr_value('my_string')
    ('string_value', 'my_string')

    :type val: `datetime.datetime`, :class:`gcloud.datastore.key.Key`,
               bool, float, integer, string
    :param val: The value to be scrutinized.

    :returns: A tuple of the attribute name and proper value type.
    """

    if isinstance(val, datetime.datetime):
        name = 'timestamp'
        value = _datetime_to_pb_timestamp(val)
    elif isinstance(val, Key):
        name, value = 'key', val.to_protobuf()
    elif isinstance(val, bool):
        name, value = 'boolean', val
    elif isinstance(val, float):
        name, value = 'double', val
    elif isinstance(val, six.integer_types):
        name, value = 'integer', val
    elif isinstance(val, six.text_type):
        name, value = 'string', val
    elif isinstance(val, (bytes, str)):
        name, value = 'blob', val
    elif isinstance(val, Entity):
        name, value = 'entity', val
    elif isinstance(val, list):
        name, value = 'array', val
    elif isinstance(val, GeoPoint):
        name, value = 'geo_point', val.to_protobuf()
    elif val is None:
        name, value = 'null', struct_pb2.NULL_VALUE
    else:
        raise ValueError("Unknown protobuf attr type %s" % type(val))

    return name + '_value', value


def _get_value_from_value_pb(value_pb):
    """Given a protobuf for a Value, get the correct value.

    The Cloud Datastore Protobuf API returns a Property Protobuf which
    has one value set and the rest blank.  This function retrieves the
    the one value provided.

    Some work is done to coerce the return value into a more useful type
    (particularly in the case of a timestamp value, or a key value).

    :type value_pb: :class:`gcloud.datastore._generated.entity_pb2.Value`
    :param value_pb: The Value Protobuf.

    :returns: The value provided by the Protobuf.
    :raises: :class:`ValueError <exceptions.ValueError>` if no value type
             has been set.
    """
    value_type = value_pb.WhichOneof('value_type')

    if value_type == 'timestamp_value':
        result = _pb_timestamp_to_datetime(value_pb.timestamp_value)

    elif value_type == 'key_value':
        result = key_from_protobuf(value_pb.key_value)

    elif value_type == 'boolean_value':
        result = value_pb.boolean_value

    elif value_type == 'double_value':
        result = value_pb.double_value

    elif value_type == 'integer_value':
        result = value_pb.integer_value

    elif value_type == 'string_value':
        result = value_pb.string_value

    elif value_type == 'blob_value':
        result = value_pb.blob_value

    elif value_type == 'entity_value':
        result = entity_from_protobuf(value_pb.entity_value)

    elif value_type == 'array_value':
        result = [_get_value_from_value_pb(value)
                  for value in value_pb.array_value.values]

    elif value_type == 'geo_point_value':
        result = GeoPoint(value_pb.geo_point_value.latitude,
                          value_pb.geo_point_value.longitude)

    elif value_type == 'null_value':
        result = None

    else:
        raise ValueError('Value protobuf did not have any value set')

    return result


def _set_protobuf_value(value_pb, val):
    """Assign 'val' to the correct subfield of 'value_pb'.

    The Protobuf API uses different attribute names based on value types
    rather than inferring the type.

    Some value types (entities, keys, lists) cannot be directly
    assigned; this function handles them correctly.

    :type value_pb: :class:`gcloud.datastore._generated.entity_pb2.Value`
    :param value_pb: The value protobuf to which the value is being assigned.

    :type val: :class:`datetime.datetime`, boolean, float, integer, string,
               :class:`gcloud.datastore.key.Key`,
               :class:`gcloud.datastore.entity.Entity`
    :param val: The value to be assigned.
    """
    attr, val = _pb_attr_value(val)
    if attr == 'key_value':
        value_pb.key_value.CopyFrom(val)
    elif attr == 'timestamp_value':
        value_pb.timestamp_value.CopyFrom(val)
    elif attr == 'entity_value':
        entity_pb = entity_to_protobuf(val)
        value_pb.entity_value.CopyFrom(entity_pb)
    elif attr == 'array_value':
        l_pb = value_pb.array_value.values
        for item in val:
            i_pb = l_pb.add()
            _set_protobuf_value(i_pb, item)
    elif attr == 'geo_point_value':
        value_pb.geo_point_value.CopyFrom(val)
    else:  # scalar, just assign
        setattr(value_pb, attr, val)


class GeoPoint(object):
    """Simple container for a geo point value.

    :type latitude: float
    :param latitude: Latitude of a point.

    :type longitude: float
    :param longitude: Longitude of a point.
    """

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def to_protobuf(self):
        """Convert the current object to protobuf.

        :rtype: :class:`google.type.latlng_pb2.LatLng`.
        :returns: The current point as a protobuf.
        """
        return latlng_pb2.LatLng(latitude=self.latitude,
                                 longitude=self.longitude)

    def __eq__(self, other):
        """Compare two geo points for equality.

        :rtype: boolean
        :returns: True if the points compare equal, else False.
        """
        if not isinstance(other, GeoPoint):
            return False

        return (self.latitude == other.latitude and
                self.longitude == other.longitude)

    def __ne__(self, other):
        """Compare two geo points for inequality.

        :rtype: boolean
        :returns: False if the points compare equal, else True.
        """
        return not self.__eq__(other)
