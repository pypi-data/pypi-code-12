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

switches = ['10.24.39.230']
auth = ('admin', 'password')
for switch in switches:
    conn = (switch, '22')
    with pynos.device.Device(conn=conn, auth=auth) as dev:
        output = dev.services.vrrp(ip_version='6', enabled=True, rbridge_id=
        '230')
        output = dev.services.vrrp(enabled=True, rbridge_id='230')
        output = dev.services.vrrp(ip_version='6', enabled=False, rbridge_id=
        '230')
        output = dev.services.vrrp(enabled=False, rbridge_id='230')
        output = dev.interface.anycast_mac(rbridge_id='230', mac=
        '0011.2233.4455')
        output = dev.interface.anycast_mac(rbridge_id='230', mac=
        '0011.2233.4455', get=True)
        output = dev.interface.anycast_mac(rbridge_id='230', mac=
        '0011.2233.4455', delete=True)
        output = dev.services.vrrp(ip_version='6', enabled=True, rbridge_id=
        '230')
        output = dev.services.vrrp(enabled=True, rbridge_id='230')
        dev.interface.anycast_mac()
