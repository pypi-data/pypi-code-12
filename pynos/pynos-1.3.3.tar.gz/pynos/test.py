import pynos.device
import pynos.versions.base.lldp
import pynos.versions.base.interface
import pynos.versions.base.bgp
import pynos.versions.base.yang.brocade_vcs
import xml.etree.ElementTree as ET

conn = ('10.24.39.211', '22')
auth = ('admin', 'password')
dev = pynos.device.Device(conn=conn, auth=auth)
# dev.services.vrrp(ip_version='6', rbridge_id='226')

# request_interface = ET.Element(
#     'show-linkinfo',
#     xmlns="urn:brocade.com:mgmt:brocade-fabric-service"
# )
# interface = dev._callback(request_interface, handler='get')
# pynos.utilities.print_xml_string(interface)
# urn = "{urn:brocade.com:mgmt:brocade-lldp-ext}"
#
# result = []
#
# request_lldp = ET.Element(
#     'get-lldp-neighbor-detail',
#     xmlns="urn:brocade.com:mgmt:brocade-lldp-ext"
# )
# rbridge_id = ET.SubElement(request_lldp,"rbridge-id")
# rbridge_id.text = '1'
# lldp_result = dev._callback(request_lldp, 'get')
# pynos.utilities.print_xml_string(lldp_result)
lldp_details = dev.lldp.neighbors(rbridge_id='225')
for lldp_detail in lldp_details:
    print lldp_detail
trill_links = dev.fabric_service.trill_links
for link in trill_links:
    print link

output = dev.system.chassis_name(rbridge_id='225')
print output

result = dev.system.chassis_name(rbridge_id='225')


# namespace = 'urn:brocade.com:mgmt:brocade-mac-address-table'
# request_mac_table = ET.Element('get-mac-address-table',
#                                xmlns=namespace)
# mac_table = dev._callback(request_mac_table, handler='get')
# pynos.utilities.print_xml_string(mac_table)
request_vcs = ET.Element('show-vcs',
                         xmlns="urn:brocade.com:mgmt:brocade-vcs")
vcs = dev._callback(request_vcs, handler='get')
pynos.utilities.print_xml_string(vcs)

# vcs_node_list = dev.vcs.vcs_nodes
# for vcs_node in vcs_node_list:
#     print vcs_node

# request_vcs = ET.Element('show-linkinfo',
#                          xmlns="urn:brocade.com:mgmt:brocade-fabric-service")
# vcs = dev._callback(request_vcs, handler='get')
# pynos.utilities.print_xml_string(vcs)
#
# request_vcs = ET.Element('show-fabric-trunk-info',
#                          xmlns="urn:brocade.com:mgmt:brocade-fabric-service")
# vcs = dev._callback(request_vcs, handler='get')
# pynos.utilities.print_xml_string(vcs)


interfaces = dev.interface.interfaces
for interface in interfaces:
    print interface['interface-name'], interface['interface-type'], \
        interface['interface-mac'], interface[
        'ip-address'], interface['interface-role'], interface[
        'interface-proto-state'], interface['interface-state'], interface[
        'if-name']


# def get_interface_detail(last_interface_type, last_interface_name):
#     result = []
#     request_interface = ET.Element(
#         'get-interface-detail',
#         xmlns="urn:brocade.com:mgmt:brocade-interface-ext"
#     )
#     if last_interface_name != '':
#         last_received_int = ET.SubElement(request_interface,
#                                        "last-rcvd-interface")
#         last_int_type_el = ET.SubElement(last_received_int, "interface-type")
#         last_int_type_el.text = last_interface_type
#         last_int_name_el = ET.SubElement(last_received_int, "interface-name")
#         last_int_name_el.text = last_interface_name
#     pynos.utilities.print_xml_string(request_interface)
#     interface_result = dev._callback(request_interface, 'get')
#     return interface_result
#
#
# # ver = dev._callback(request_ver, handler='get')
# has_more = ''
# last_interface_name = ''
# last_interface_type = ''
# count = 0
# result = []
# urn = "{urn:brocade.com:mgmt:brocade-interface-ext}"
# while has_more =='' or has_more=='true':
#     interface_result = get_interface_detail(last_interface_type=
#                                         last_interface_type,
#                                         last_interface_name=last_interface_name)
#     has_more = interface_result.find('%shas-more' % urn).text
#     last_interface_type = ''
#     last_interface_name = ''
#     pynos.utilities.print_xml_string(interface_result)
#     for item in interface_result.findall('%sinterface' % urn):
#             interface_type = item.find('%sinterface-type' % urn).text
#             interface_name = item.find('%sinterface-name' % urn).text
#             count = count + 1
#             last_interface_type = interface_type
#             last_interface_name = interface_name
#             if "gigabitethernet" in interface_type:
#                 interface_role = item.find('%sport-role' % urn).text
#                 if_name = item.find('%sif-name' % urn).text
#                 interface_state = item.find('%sif-state' % urn).text
#                 interface_proto_state = item.find('%sline-protocol-state' %
#                                                   urn).text
#                 interface_mac = item.find(
#                     '%scurrent-hardware-address' % urn).text
#
#                 item_results = {'interface-type': interface_type,
#                                 'interface-name': interface_name,
#                                 'interface-role': interface_role,
#                                 'interface-role': if_name,
#                                 'interface-state': interface_state,
#                               'interface-proto-state': interface_proto_state,
#                                 'interface-mac': interface_mac}
#                 result.append(item_results)
#             elif "loopback" in interface_type:
#                 interface_role = item.find('%sport-role' % urn).text
#                 if_name = item.find('%sif-name' % urn).text
#                 interface_state = item.find('%sif-state' % urn).text
#                 interface_proto_state = item.find('%sline-protocol-state' %
#                                                   urn).text
#                 interface_mac = item.find(
#                     '%scurrent-hardware-address' % urn).text
#
#                 item_results = {'interface-type': interface_type,
#                                 'interface-name': interface_name,
#                                 'interface-role': interface_role,
#                                 'interface-role': if_name,
#                                 'interface-state': interface_state,
#                               'interface-proto-state': interface_proto_state,
#                                 'interface-mac': interface_mac}
#                 result.append(item_results)

# print len(result)
# print count
# output = dev.system.host_name(rbridge_id='225', host_name='sw211')
# print output
# output = dev.system.host_name(rbridge_id='225', get=True)
# print output
# output = dev.bgp.get_bgp_neighbors(rbridge_id='225')
# for neighbor in output:
#     print neighbor
# try:
#     conf = output.data.find('.//{*}host-name').text
# except AttributeError:
#     conf = None
# print conf

int_type = 'tengigabitethernet'
name = '225/0/11'
# ip_addr = 'fc00:1:3:1ad3:0:0:23:a/64'
version = 6
# output = dev.interface.disable_switchport(inter_type=
# int_type, inter=name)
# output = dev.interface.ip_address(int_type=int_type,
# name=name, ip_addr=ip_addr)
# output = dev.interface.get_ip_addresses(int_type=int_type,
#                                         name=name, version=version)
# result = []
# if version == 4:
#     try:
#         for item in output.data.findall('.//{*}address/{*}address'):
#             result.append(item.text)
#     except AttributeError:
#         conf = None
# elif version == 6:
#     try:
#         for item in output.data.findall('.//{*}address/{*}ipv6-address/{'
#                                         '*}address'):
#             result.append(item.text)
#     except AttributeError:
#         conf = None
# print result
# output = dev.bgp.local_asn(local_as='65535', rbridge_id='225')
# print output
# output = dev.system.rbridge_id(get=True)
# try:
#     conf = output.data.find('.//{*}rbridge-id/{*}rbridge-id').text
# except AttributeError:
#     conf = None
# print conf
# output = dev.bgp.local_asn(get=True, rbridge_id='40')
# try:
#     conf = output.data.find('.//{*}local-as').text
# except AttributeError:
#     conf = None
# print conf
# print dev.interface.interfaces
# print dev.bgp.local_asn()
# print dev.bgp.local_as
# print dev.bgp.enabled
# print dev.firmware_version
# namespace = "urn:brocade.com:mgmt:brocade-firmware-ext"
# request_ver = ET.Element("show-firmware-version", xmlns=namespace)
# ver = dev._callback(request_ver, handler='get')
# pynos.utilities.print_xml_string(ver)
# print ver.find('.//*{%s}firmware-full-version' % namespace).text
# request_lldp = ET.Element(
#             'get-lldp-neighbor-detail',
#             xmlns="urn:brocade.com:mgmt:brocade-lldp-ext"
#         )
# lldp = dev._callback(request_lldp, handler='get')
# pynos.utilities.print_xml_string(lldp)
request_interface = ET.Element(
    'get-interface-detail',
    xmlns="urn:brocade.com:mgmt:brocade-interface-ext"
)
# interface = dev._callback(request_interface, handler='get')
# pynos.utilities.print_xml_string(interface)

# namespace = 'urn:brocade.com:mgmt:brocade-mac-address-table'
# request_mac_table = ET.Element('get-mac-address-table',
#                                xmlns=namespace)
# result = dev._callback(request_mac_table, handler='get')
# pynos.utilities.print_xml_string(result)
# for entry in result.findall('{%s}mac-address-table' % namespace):
#     address = entry.find('{%s}mac-address' % namespace).text
#     vlan = entry.find('{%s}vlanid' % namespace).text
#     mac_type = entry.find('{%s}mac-type' % namespace).text
#     state = entry.find('{%s}mac-state' % namespace).text
#     interface = entry.find('{%s}forwarding-interface' % namespace)
#     interface_type = interface.find('{%s}interface-type' %
#                                     namespace).text
#     interface_name = interface.find('{%s}interface-name' %
#                                     namespace).text
#     interface = '%s%s' % (interface_type, interface_name)

# table.append(dict(mac_address=address, interface=interface,
#                   state=state, vlan=vlan,
#                   type=mac_type))
