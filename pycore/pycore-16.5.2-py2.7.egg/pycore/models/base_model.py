"""
Copyright (c) 2014 Maciej Nabozny

This file is part of CloudOver project.

CloudOver is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pycore.utils import request, calc_hash
import importlib


class BaseModel(object):
    api_modules = None

    def __init__(self, address, token, object_dict, debug=False):
        self.token = token
        self.oc_address = address
        self.debug = debug

        for key in object_dict.keys():
            setattr(self, key, object_dict[key])

        class_id = '%s_id' % self.__class__.__name__.lower()

        if not hasattr(self.__class__, 'api_modules'):
            self.__class__.api_modules = request(self.oc_address, '/api/api/list_api_modules/', {'token': self.token}, self.debug)

        if self.__class__.api_modules is None:
            self.__class__.api_modules = request(self.oc_address, '/api/api/list_api_modules/', {'token': self.token}, self.debug)

        self.__class__.api_modules = [m.split('.')[0] for m in self.__class__.api_modules]

        available_extensions = importlib.import_module('pycore.extensions')

        for extension in self.__class__.api_modules:
            try:
                ext_model = importlib.import_module('pycore.extensions.%s.models.%s' % (extension, self.__class__.__name__.lower()))

                ext = getattr(ext_model, self.__class__.__name__)()
                setattr(self, extension, ext)
                setattr(ext, 'parent_model', self)
            except Exception as e:
                pass

    def __eq__(self, other):
        if other == None:
            return False
        if not isinstance(other, self.__class__):
            return False

        return self.id == other.id and self.oc_address == other.oc_address