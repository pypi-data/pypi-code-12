"""
Copyright (c) 2016 Marta Nabozny

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


from pycore.utils import request, check_version

class Network(object):
    parent_model = None

    def start(self, gateway_ip):
        check_version(self.parent_model.oc_address, self.parent_model.token, '16.01')
        request(self.parent_model.oc_address, '/api/dhcp/start/', {'token': self.parent_model.token,
                                                                   'network_id': self.parent_model.id,
                                                                   'gateway_ip': gateway_ip}, self.parent_model.debug)


    def stop(self):
        check_version(self.parent_model.oc_address, self.parent_model.token, '16.01')
        request(self.parent_model.oc_address, '/api/dhcp/stop/', {'token': self.parent_model.token,
                                                                  'network_id': self.parent_model.id}, self.parent_model.debug)
