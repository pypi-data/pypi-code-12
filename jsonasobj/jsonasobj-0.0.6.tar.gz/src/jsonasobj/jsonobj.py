# -*- coding: utf-8 -*-
# Copyright (c) 2015, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import json
from .extendednamespace import ExtendedNamespace


class JsonObj(ExtendedNamespace):
    """ A namespace/dictionary representation of a JSON object. Any name in a JSON object that is a valid python
    identifier is represented as a first-class member of the objects.  JSON identifiers that begin with "_" are
    disallowed in this implementation.
    """
    def __init__(self, **kwargs):
        """ Construct a JsonObj from set of keyword/value pairs
        :param kwargs: keyword/value pairs
        """
        ExtendedNamespace.__init__(self, **kwargs)

    def _get(self, item, default=None) -> object:
        return self[item] if item in self else default

    def _default(self, obj):
        """ a function that returns a serializable version of obj or raises TypeError
        :param obj:
        :return: Serialized version of obj
        """
        return obj.__dict__ if isinstance(obj, JsonObj) else json.JSONDecoder.default(self, obj)

    def _as_json_obj(self):
        """ Return jsonObj as pure json
        :return: Pure json image
        """
        return json.loads(self._as_json_dumps(indent=None))

    def setdefault(self, k, value):
        if k not in self:
            self[k] = JsonObj(**value) if isinstance(value, dict) else value
        return self[k]

    def _items(self):
        """ Same as dict items() except that the values are JsonObjs instead of vanilla dictionaries
        :return:
        """
        return [(k, self[k]) for k in self.__dict__.keys()]

    @property
    def _as_json(self, **kwargs):
        """ Convert a JsonObj into straight json
        :param kwargs: json.dumps arguments
        :return: JSON formatted str
        """
        return json.dumps(self, default=self._default, **kwargs)

    def _as_json_dumps(self, indent='   ', **kwargs):
        """ Convert to a stringified json object.  This is the same as _as_json with the exception that it isn't
        a property, meaning that we can actually pass arguments...
        :param indent: indent argument to dumps
        :param kwargs: other arguments for dumps
        :return: JSON formatted string
        """
        return json.dumps(self, default=self._default, indent=indent, **kwargs)

    @staticmethod
    def __as_list(value):
        """ Return a json array as a list
        :param value: array
        :return: array with JsonObj instances removed
        """
        return [e._as_dict if isinstance(e, JsonObj) else e for e in value]

    @property
    def _as_dict(self):
        """ Convert a JsonObj into a straight dictionary
        :return: dictionary that cooresponds to the json object
        """
        return {k: v._as_dict if isinstance(v, JsonObj) else
                self.__as_list(v) if isinstance(v, list) else v for k, v in self.__dict__.items()}


def loads(s: str, **kwargs):
    """ Convert a json_str into a JsonObj
    :param s: a str instance containing a JSON document
    :param kwargs: arguments see: json.load for details
    :return: JsonObj representing the json string
    """
    return json.loads(s, object_hook=lambda pairs: JsonObj(**pairs), **kwargs)


def load(fp, **kwargs):
    """ Deserialize fp (a .read()-supporting file-like object containing a JSON document) to a JsonObj
    :param fp: file-like object to deserialize
    :param kwargs: arguments. see: json.load for details
    :return: JsonObj representing fp
    """
    return loads(fp.read(), **kwargs)
