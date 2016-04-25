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


def rbridge_id_protocol_hide_vrrp_holder_vrrp(self, **kwargs):
    """Auto Generated Code
    """
    config = ET.Element("config")
    rbridge_id = ET.SubElement(config, "rbridge-id",
                               xmlns="urn:brocade.com:mgmt:brocade-rbridge")
    rbridge_id_key = ET.SubElement(rbridge_id, "rbridge-id")
    rbridge_id_key.text = kwargs.pop('rbridge_id')
    protocol = ET.SubElement(rbridge_id, "protocol",
                             xmlns="urn:brocade.com:mgmt:brocade-interface")
    hide_vrrp_holder = ET.SubElement(protocol, "hide-vrrp-holder",
                                     xmlns="urn:brocade.com:mgmt:brocade-vrrp")
    vrrp = ET.SubElement(hide_vrrp_holder, "vrrp")

    callback = kwargs.pop('callback', self._callback)
    return callback(config)


def rbridge_id_protocol_hide_vrrp_holder_vrrp(self, **kwargs):
    """Auto Generated Code
    """
    config = ET.Element("config")
    rbridge_id = ET.SubElement(config, "rbridge-id",
                               xmlns="urn:brocade.com:mgmt:brocade-rbridge")
    rbridge_id_key = ET.SubElement(rbridge_id, "rbridge-id")
    rbridge_id_key.text = kwargs.pop('rbridge_id')
    protocol = ET.SubElement(rbridge_id, "protocol",
                             xmlns="urn:brocade.com:mgmt:brocade-interface")
    hide_vrrp_holder = ET.SubElement(protocol, "hide-vrrp-holder",
                                     xmlns="urn:brocade.com:mgmt:brocade-vrrp")
    vrrp = ET.SubElement(hide_vrrp_holder, "vrrp")

    callback = kwargs.pop('callback', self._callback)
    return callback(config)

def rbridge_id_ipv6_proto_vrrpv3_vrrp(self, **kwargs):
    """Auto Generated Code
    """
    config = ET.Element("config")
    rbridge_id = ET.SubElement(config, "rbridge-id",
                               xmlns="urn:brocade.com:mgmt:brocade-rbridge")
    rbridge_id_key = ET.SubElement(rbridge_id, "rbridge-id")
    rbridge_id_key.text = kwargs.pop('rbridge_id')
    ipv6 = ET.SubElement(rbridge_id, "ipv6")
    proto_vrrpv3 = ET.SubElement(ipv6, "proto-vrrpv3",
                                 xmlns="urn:brocade.com:mgmt:brocade-vrrpv3")
    vrrp = ET.SubElement(proto_vrrpv3, "vrrp")

    callback = kwargs.pop('callback', self._callback)
    return callback(config)


def rbridge_id_ipv6_proto_vrrpv3_vrrp(self, **kwargs):
    """Auto Generated Code
    """
    config = ET.Element("config")
    rbridge_id = ET.SubElement(config, "rbridge-id",
                               xmlns="urn:brocade.com:mgmt:brocade-rbridge")
    rbridge_id_key = ET.SubElement(rbridge_id, "rbridge-id")
    rbridge_id_key.text = kwargs.pop('rbridge_id')
    ipv6 = ET.SubElement(rbridge_id, "ipv6")
    proto_vrrpv3 = ET.SubElement(ipv6, "proto-vrrpv3",
                                 xmlns="urn:brocade.com:mgmt:brocade-vrrpv3")
    vrrp = ET.SubElement(proto_vrrpv3, "vrrp")

    callback = kwargs.pop('callback', self._callback)
    return callback(config)







