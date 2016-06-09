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

import pycore.extensions.coretalk.models.userdata
import pycore.extensions.coretalk.models.sshkey
from pycore.utils import request, check_version, VersionException

class Api():
    def __init__(self, parent_model):
        # This is handler for top-level API object. It handles URL to CoreCluster's API interface
        self.parent_model = parent_model


    def userdata_by_id(self, id):
        try:
            check_version(self.parent_model.oc_address, self.parent_model.token, '15.12')
            resp = request(self.parent_model.oc_address, '/api/userdata/get_by_id/', {'token': self.parent_model.token, 'userdata_id': id})
        except VersionException:
            resp = request(self.parent_model.oc_address, '/coreTalk/userdata/get_by_id/', {'token': self.parent_model.token, 'userdata_id': id})

        return pycore.extensions.coretalk.models.userdata.UserData(self.oc_address, self.token, resp, self.debug)


    def userdata_list(self):
        """
        List user data objects from cloud
        :return: list of userdata objects
        """
        try:
            check_version(self.parent_model.oc_address, self.parent_model.token, '15.12')
            resp = request(self.parent_model.oc_address, '/api/userdata/get_list/', {'token': self.parent_model.token})
        except VersionException:
            resp = request(self.parent_model.oc_address, '/coreTalk/userdata/get_list/', {'token': self.parent_model.token})
        return [pycore.extensions.coretalk.models.userdata.UserData(self.parent_model.oc_address, self.parent_model.token, ud) for ud in resp]


    def userdata_by_name(self, name):
        """
        List user data objects from cloud
        :return: list of userdata objects
        """
        d = []
        try:
            check_version(self.parent_model.oc_address, self.parent_model.token, '15.12')
            resp = request(self.parent_model.oc_address, '/api/userdata/get_list/', {'token': self.parent_model.token})
        except VersionException:
            resp = request(self.parent_model.oc_address, '/coreTalk/userdata/get_list/', {'token': self.parent_model.token})
        return [pycore.extensions.coretalk.models.userdata.UserData(self.parent_model.oc_address, self.parent_model.token, ud) for ud in resp if ud['name'] == name]


    def userdata_create(self, name, data, convert_from=None):
        try:
            check_version(self.parent_model.oc_address, self.parent_model.token, '15.12')
            resp = request(self.parent_model.oc_address, '/api/userdata/create/', {'token': self.parent_model.token,
                                                                                   'name': name,
                                                                                   'data': data,
                                                                                   'convert_from': convert_from})
        except VersionException:
            resp = request(self.parent_model.oc_address, '/coreTalk/userdata/create/', {'token': self.parent_model.token,
                                                                                        'name': name,
                                                                                        'data': data})
        return pycore.extensions.coretalk.models.userdata.UserData(self.parent_model.oc_address, self.parent_model.token, resp)
