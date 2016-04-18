#!/usr/bin/env python
"""Module for Mamba database interaction.

Copyright 2015 Brocade Communications Systems, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import pynos.device
import pynos.versions.base.interface

switches = ['10.24.39.211', '10.24.39.203']
auth = ('admin', 'password')
for switch in switches:
    conn = (switch, '22')
    with pynos.device.Device(conn=conn, auth=auth) as dev:
        int_type = 'tengigabitethernet'
        name = '225/0/3'
        ip_addr = '20.10.10.1/24'
        version = 4
        # output = dev.interface.disable_switchport(inter_type=
        #                                           int_type, inter=name)
        output = dev.interface.ip_address(int_type=int_type,
                                          name=name, ip_addr=ip_addr)
        result = dev.interface.get_ip_addresses(int_type=int_type,
                                                name=name, version=version)
        print result
        assert len(result) >= 1
        output = dev.interface.ip_address(int_type=int_type,
                                          name=name, ip_addr=ip_addr,
                                          delete=True)
        ip_addr = 'fc00:1:3:1ad3:0:0:23:a/64'
        version = 6
        output = dev.interface.ip_address(int_type=int_type,
                                          name=name, ip_addr=ip_addr)
        result = dev.interface.get_ip_addresses(int_type=int_type,
                                                name=name, version=version)
        print result
        assert len(result) >= 1
        output = dev.interface.ip_address(int_type=int_type,
                                          name=name, ip_addr=ip_addr,
                                          delete=True)
