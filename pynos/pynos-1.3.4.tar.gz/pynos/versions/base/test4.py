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
switches = ['10.24.39.211', '10.24.39.203']
auth = ('admin', 'password')
for switch in switches:
    conn = (switch, '22')
    with pynos.device.Device(conn=conn, auth=auth) as dev:
        output = dev.services.vrrp(ip_version='6', enabled = True,
                                   rbridge_id = '225')
        output = dev.services.vrrp(enabled=True, rbridge_id = '225')
        output = dev.interface.set_ip('tengigabitethernet', '225/0/18',
                                      '10.1.1.2/24')
        output = dev.interface.ip_address(name='225/0/18', int_type =
        'tengigabitethernet', ip_addr =
        '2001:4818:f000:1ab:cafe:beef:1000:2/64')

        dev.interface.vrrp_vip(int_type='tengigabitethernet', name =
        '225/0/18', vrid = '1', vip = '10.1.1.1/24')

        dev.interface.vrrp_vip(int_type='tengigabitethernet', name =
        '225/0/18', vrid = '1', vip = 'fe80::cafe:beef:1000:1/64')

        dev.interface.vrrp_vip(int_type='tengigabitethernet', name =
        '225/0/18', vrid = '1', vip = '2001:4818:f000:1ab:cafe:beef:1000:1/64')

        dev.interface.vrrp_priority(int_type = 'tengigabitethernet', name =
        '225/0/18', vrid = '1', ip_version = '4', priority = '66')

        dev.interface.vrrp_priority(int_type = 'tengigabitethernet', name =
        '225/0/18', vrid = '1', ip_version = '6', priority = '77')

        output = dev.interface.add_vlan_int('88')

        output = dev.interface.ip_address(int_type='ve', name = '88',
                                          ip_addr = '172.16.10.1/24', rbridge_id = '225')

        output = dev.interface.ip_address(int_type='ve', name = '88',
                                          rbridge_id = '225', ip_addr =
                                          '2003:4818:f000:1ab:cafe:beef:1000:2/64')
        dev.interface.vrrp_vip(int_type='ve', name='88', vrid = '1',
                               vip = '172.16.10.2/24', rbridge_id = '225')
        dev.interface.vrrp_vip(int_type='ve', name='88', rbridge_id = '225',
                               vrid = '1', vip = 'fe80::dafe:beef:1000:1/64')
        dev.interface.vrrp_vip(int_type='ve', rbridge_id='225', name = '88',
                               vrid = '1', vip =
                               '2003:4818:f000:1ab:cafe:beef:1000:1/64')

        dev.interface.vrrp_priority(int_type='ve', name='88', rbridge_id =
        '225', vrid = '1', ip_version = '4', priority = '66')

        dev.interface.vrrp_priority(int_type='ve', name='88', rbridge_id =
        '225', vrid = '1', ip_version='6', priority='77')

        output = dev.services.vrrp(ip_version='6', enabled = False,
                                   rbridge_id='225')
        output = dev.services.vrrp(enabled=False, rbridge_id='225')
