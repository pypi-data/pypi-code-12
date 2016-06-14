from cloudshell.shell.core.driver_context import AutoLoadAttribute

class GenericResourceAttribute:
    def get_autoload_resource_attributes(self):
        attributes_dict = self.__dict__.copy()
        return attributes_dict.values()


class NetworkingStandardRootAttributes(GenericResourceAttribute):
    def __init__(self, relative_path='', model='', vendor='', system_name='', location='',
                 contact='', version=''):
        self.vendor = AutoLoadAttribute(relative_path, 'Vendor', vendor)
        self.system_name = AutoLoadAttribute(relative_path, 'System Name', system_name)
        self.location = AutoLoadAttribute(relative_path, 'Location', location)
        self.contact = AutoLoadAttribute(relative_path, 'Contact Name', contact)
        self.version = AutoLoadAttribute(relative_path, 'OS Version', version)
        self.model = AutoLoadAttribute(relative_path, 'Model', model)


class NetworkingStandardChassisAttributes(GenericResourceAttribute):
    def __init__(self, relative_path, serial_number='', chassis_model=''):
        self.serial_number = AutoLoadAttribute(relative_path, 'Serial Number', serial_number)
        self.model = AutoLoadAttribute(relative_path, 'Model', chassis_model)


class NetworkingStandardModuleAttributes(GenericResourceAttribute):
    def __init__(self, relative_path, serial_number='', module_model='', version=''):
        self.serial_number = AutoLoadAttribute(relative_path, 'Serial Number', serial_number)
        self.module_model = AutoLoadAttribute(relative_path, 'Model', module_model)
        self.version = AutoLoadAttribute(relative_path, 'Version', version)


class NetworkingStandardPortAttributes(GenericResourceAttribute):
    def __init__(self, relative_path, protocol_type='Transparent', description='', l2_protocol_type='ethernet', mac='',
                 mtu=0, bandwidth=0, adjacent='', ipv4_address='', ipv6_address='', duplex='', auto_negotiation=''):
        self.protocol_type = AutoLoadAttribute(relative_path, 'Protocol Type', protocol_type)
        self.port_description = AutoLoadAttribute(relative_path, 'Port Description', description)
        self.l2_protocol_type = AutoLoadAttribute(relative_path, 'L2 Protocol Type', l2_protocol_type)
        self.mac = AutoLoadAttribute(relative_path, 'MAC Address', mac)
        self.mtu = AutoLoadAttribute(relative_path, 'MTU', mtu)
        self.duplex = AutoLoadAttribute(relative_path, 'Duplex', duplex)
        self.auto_negotiation = AutoLoadAttribute(relative_path, 'Auto Negotiation', auto_negotiation)
        self.bandwidth = AutoLoadAttribute(relative_path, 'Bandwidth', bandwidth)
        self.adjacent = AutoLoadAttribute(relative_path, 'Adjacent', adjacent)
        self.ipv4_address = AutoLoadAttribute(relative_path, 'IPv4 Address', ipv4_address)
        self.ipv6_address = AutoLoadAttribute(relative_path, 'IPv6 Address', ipv6_address)


class NetworkingStandardPortChannelAttributes(GenericResourceAttribute):
    def __init__(self, relative_path, protocol_type='Transparent', description='', associated_ports='',
                 ipv4_address='', ipv6_address=''):
        self.protocol_type = AutoLoadAttribute(relative_path, 'Protocol Type', protocol_type)
        self.description = AutoLoadAttribute(relative_path, 'Port Description', description)
        self.associated_ports = AutoLoadAttribute(relative_path, 'Associated Ports', associated_ports)
        self.ipv4_address = AutoLoadAttribute(relative_path, 'IPv4 Address', ipv4_address)
        self.ipv6_address = AutoLoadAttribute(relative_path, 'IPv6 Address', ipv6_address)


class NetworkingStandardPowerPortAttributes(GenericResourceAttribute):
    def __init__(self, relative_path, serial_number='', port_model='', version='', description=''):
        self.serial_number = AutoLoadAttribute(relative_path, 'Serial Number', serial_number)
        self.port_model = AutoLoadAttribute(relative_path, 'Model', port_model)
        self.version = AutoLoadAttribute(relative_path, 'Version', version)
        self.description = AutoLoadAttribute(relative_path, 'Port Description', description)
