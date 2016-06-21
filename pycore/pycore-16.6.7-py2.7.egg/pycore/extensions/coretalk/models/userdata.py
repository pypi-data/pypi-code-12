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


from pycore.utils import request, check_version, VersionException
from pycore.models.base_model import BaseModel

class UserData(BaseModel):
    def delete(self):
        try:
            check_version(self.oc_address, self.token, '15.12')
            request(self.oc_address, '/api/userdata/delete/', {'token': self.token,
                                                                    'userdata_id': self.id}, self.debug)
        except VersionException:
            request(self.oc_address, '/coreTalk/userdata/delete/', {'token': self.token,
                                                                    'userdata_id': self.id}, self.debug)

    def attach(self, vm):
        try:
            check_version(self.oc_address, self.token, '15.12')
            request(self.oc_address, '/api/userdata/attach/', {'token': self.token,
                                                               'userdata_id': self.id,
                                                               'vm_id': vm.id}, self.debug)
        except VersionException:
            request(self.oc_address, '/coreTalk/userdata/attach/', {'token': self.token,
                                                                    'userdata_id': self.id,
                                                                    'vm_id': vm.id}, self.debug)

    def detach(self, vm):
        try:
            check_version(self.oc_address, self.token, '15.12')
            request(self.oc_address, '/api/userdata/detach/', {'token': self.token,
                                                               'userdata_id': self.id,
                                                               'vm_id': vm.id}, self.debug)
        except VersionException:
            request(self.oc_address, '/coreTalk/userdata/detach/', {'token': self.token,
                                                                    'userdata_id': self.id,
                                                                    'vm_id': vm.id}, self.debug)


    def edit(self, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
                try:
                    check_version(self.oc_address, self.token, '15.12')
                    request(self.oc_address, '/api/userdata/edit/', {'token': self.token,
                                                                     'userdata_id': self.id,
                                                                     key: kwargs[key]}, self.debug)

                except VersionException:
                    request(self.oc_address, '/coreTalk/userdata/edit/', {'token': self.token,
                                                                          'userdata_id': self.id,
                                                                          key: kwargs[key]}, self.debug)
