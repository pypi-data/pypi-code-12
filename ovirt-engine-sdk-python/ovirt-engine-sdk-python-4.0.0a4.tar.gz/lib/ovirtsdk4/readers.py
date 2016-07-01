# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from ovirtsdk4 import List
from ovirtsdk4 import types
from ovirtsdk4.reader import Reader


class ActionReader(Reader):

    def __init__(self):
        super(ActionReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Action()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'async':
                obj.async = Reader.read_boolean(reader)
            elif tag == 'bricks':
                obj.bricks = GlusterBrickReader.read_many(reader)
            elif tag == 'certificates':
                obj.certificates = CertificateReader.read_many(reader)
            elif tag == 'check_connectivity':
                obj.check_connectivity = Reader.read_boolean(reader)
            elif tag == 'clone':
                obj.clone = Reader.read_boolean(reader)
            elif tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'collapse_snapshots':
                obj.collapse_snapshots = Reader.read_boolean(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'connectivity_timeout':
                obj.connectivity_timeout = Reader.read_integer(reader)
            elif tag == 'data_center':
                obj.data_center = DataCenterReader.read_one(reader)
            elif tag == 'deploy_hosted_engine':
                obj.deploy_hosted_engine = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'details':
                obj.details = GlusterVolumeProfileDetailsReader.read_one(reader)
            elif tag == 'discard_snapshots':
                obj.discard_snapshots = Reader.read_boolean(reader)
            elif tag == 'disk':
                obj.disk = DiskReader.read_one(reader)
            elif tag == 'disks':
                obj.disks = DiskReader.read_many(reader)
            elif tag == 'exclusive':
                obj.exclusive = Reader.read_boolean(reader)
            elif tag == 'exclussive':
                obj.exclussive = Reader.read_boolean(reader)
            elif tag == 'fault':
                obj.fault = FaultReader.read_one(reader)
            elif tag == 'fence_type':
                obj.fence_type = Reader.read_string(reader)
            elif tag == 'filter':
                obj.filter = Reader.read_boolean(reader)
            elif tag == 'fix_layout':
                obj.fix_layout = Reader.read_boolean(reader)
            elif tag == 'force':
                obj.force = Reader.read_boolean(reader)
            elif tag == 'grace_period':
                obj.grace_period = GracePeriodReader.read_one(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'image':
                obj.image = Reader.read_string(reader)
            elif tag == 'import_as_template':
                obj.import_as_template = Reader.read_boolean(reader)
            elif tag == 'is_attached':
                obj.is_attached = Reader.read_boolean(reader)
            elif tag == 'iscsi':
                obj.iscsi = IscsiDetailsReader.read_one(reader)
            elif tag == 'iscsi_targets':
                reader.next_element()
            elif tag == 'job':
                obj.job = JobReader.read_one(reader)
            elif tag == 'logical_units':
                obj.logical_units = LogicalUnitReader.read_many(reader)
            elif tag == 'maintenance_enabled':
                obj.maintenance_enabled = Reader.read_boolean(reader)
            elif tag == 'modified_bonds':
                obj.modified_bonds = HostNicReader.read_many(reader)
            elif tag == 'modified_labels':
                obj.modified_labels = NetworkLabelReader.read_many(reader)
            elif tag == 'modified_network_attachments':
                obj.modified_network_attachments = NetworkAttachmentReader.read_many(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'option':
                obj.option = OptionReader.read_one(reader)
            elif tag == 'pause':
                obj.pause = Reader.read_boolean(reader)
            elif tag == 'power_management':
                obj.power_management = PowerManagementReader.read_one(reader)
            elif tag == 'proxy_ticket':
                obj.proxy_ticket = ProxyTicketReader.read_one(reader)
            elif tag == 'reason':
                obj.reason = Reader.read_string(reader)
            elif tag == 'removed_bonds':
                obj.removed_bonds = HostNicReader.read_many(reader)
            elif tag == 'removed_labels':
                obj.removed_labels = NetworkLabelReader.read_many(reader)
            elif tag == 'removed_network_attachments':
                obj.removed_network_attachments = NetworkAttachmentReader.read_many(reader)
            elif tag == 'resolution_type':
                obj.resolution_type = Reader.read_string(reader)
            elif tag == 'restore_memory':
                obj.restore_memory = Reader.read_boolean(reader)
            elif tag == 'root_password':
                obj.root_password = Reader.read_string(reader)
            elif tag == 'snapshot':
                obj.snapshot = SnapshotReader.read_one(reader)
            elif tag == 'ssh':
                obj.ssh = SshReader.read_one(reader)
            elif tag == 'status':
                obj.status = Reader.read_string(reader)
            elif tag == 'stop_gluster_service':
                obj.stop_gluster_service = Reader.read_boolean(reader)
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'storage_domains':
                obj.storage_domains = StorageDomainReader.read_many(reader)
            elif tag == 'succeeded':
                obj.succeeded = Reader.read_boolean(reader)
            elif tag == 'synchronized_network_attachments':
                obj.synchronized_network_attachments = NetworkAttachmentReader.read_many(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'ticket':
                obj.ticket = TicketReader.read_one(reader)
            elif tag == 'undeploy_hosted_engine':
                obj.undeploy_hosted_engine = Reader.read_boolean(reader)
            elif tag == 'use_cloud_init':
                obj.use_cloud_init = Reader.read_boolean(reader)
            elif tag == 'use_sysprep':
                obj.use_sysprep = Reader.read_boolean(reader)
            elif tag == 'virtual_functions_configuration':
                obj.virtual_functions_configuration = HostNicVirtualFunctionsConfigurationReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ActionReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class AffinityGroupReader(Reader):

    def __init__(self):
        super(AffinityGroupReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.AffinityGroup()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'enforcing':
                obj.enforcing = Reader.read_boolean(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'positive':
                obj.positive = Reader.read_boolean(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'link':
                AffinityGroupReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(AffinityGroupReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "vms":
                obj.vms = list
        reader.next_element()


class AffinityLabelReader(Reader):

    def __init__(self):
        super(AffinityLabelReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.AffinityLabel()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'hosts':
                obj.hosts = HostReader.read_many(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'read_only':
                obj.read_only = Reader.read_boolean(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'link':
                AffinityLabelReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(AffinityLabelReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "hosts":
                obj.hosts = list
            elif rel == "vms":
                obj.vms = list
        reader.next_element()


class AgentReader(Reader):

    def __init__(self):
        super(AgentReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Agent()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'concurrent':
                obj.concurrent = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'encrypt_options':
                obj.encrypt_options = Reader.read_boolean(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'options':
                obj.options = OptionReader.read_many(reader)
            elif tag == 'order':
                obj.order = Reader.read_integer(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'type':
                obj.type = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(AgentReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class AgentConfigurationReader(Reader):

    def __init__(self):
        super(AgentConfigurationReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.AgentConfiguration()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'broker_type':
                obj.broker_type = types.MessageBrokerType(Reader.read_string(reader).lower())
            elif tag == 'network_mappings':
                obj.network_mappings = Reader.read_string(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(AgentConfigurationReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ApiReader(Reader):

    def __init__(self):
        super(ApiReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Api()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'product_info':
                obj.product_info = ProductInfoReader.read_one(reader)
            elif tag == 'special_objects':
                obj.special_objects = SpecialObjectsReader.read_one(reader)
            elif tag == 'summary':
                obj.summary = ApiSummaryReader.read_one(reader)
            elif tag == 'time':
                obj.time = Reader.read_date(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ApiReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ApiSummaryReader(Reader):

    def __init__(self):
        super(ApiSummaryReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ApiSummary()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'hosts':
                obj.hosts = ApiSummaryItemReader.read_one(reader)
            elif tag == 'storage_domains':
                obj.storage_domains = ApiSummaryItemReader.read_one(reader)
            elif tag == 'users':
                obj.users = ApiSummaryItemReader.read_one(reader)
            elif tag == 'vms':
                obj.vms = ApiSummaryItemReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ApiSummaryReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ApiSummaryItemReader(Reader):

    def __init__(self):
        super(ApiSummaryItemReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ApiSummaryItem()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'active':
                obj.active = Reader.read_integer(reader)
            elif tag == 'total':
                obj.total = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ApiSummaryItemReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ApplicationReader(Reader):

    def __init__(self):
        super(ApplicationReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Application()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ApplicationReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class AuthorizedKeyReader(Reader):

    def __init__(self):
        super(AuthorizedKeyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.AuthorizedKey()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'key':
                obj.key = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'user':
                obj.user = UserReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(AuthorizedKeyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class BalanceReader(Reader):

    def __init__(self):
        super(BalanceReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Balance()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'scheduling_policy':
                obj.scheduling_policy = SchedulingPolicyReader.read_one(reader)
            elif tag == 'scheduling_policy_unit':
                obj.scheduling_policy_unit = SchedulingPolicyUnitReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(BalanceReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class BiosReader(Reader):

    def __init__(self):
        super(BiosReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Bios()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'boot_menu':
                obj.boot_menu = BootMenuReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(BiosReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class BlockStatisticReader(Reader):

    def __init__(self):
        super(BlockStatisticReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.BlockStatistic()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(BlockStatisticReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class BondingReader(Reader):

    def __init__(self):
        super(BondingReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Bonding()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'options':
                obj.options = OptionReader.read_many(reader)
            elif tag == 'slaves':
                obj.slaves = HostNicReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(BondingReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class BookmarkReader(Reader):

    def __init__(self):
        super(BookmarkReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Bookmark()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'value':
                obj.value = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(BookmarkReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class BootReader(Reader):

    def __init__(self):
        super(BootReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Boot()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'devices':
                reader.next_element()
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(BootReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class BootMenuReader(Reader):

    def __init__(self):
        super(BootMenuReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.BootMenu()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(BootMenuReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class BrickProfileDetailReader(Reader):

    def __init__(self):
        super(BrickProfileDetailReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.BrickProfileDetail()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'brick':
                obj.brick = GlusterBrickReader.read_one(reader)
            elif tag == 'profile_details':
                obj.profile_details = ProfileDetailReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(BrickProfileDetailReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class CdromReader(Reader):

    def __init__(self):
        super(CdromReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Cdrom()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'file':
                obj.file = FileReader.read_one(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'link':
                CdromReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(CdromReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "vms":
                obj.vms = list
        reader.next_element()


class CertificateReader(Reader):

    def __init__(self):
        super(CertificateReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Certificate()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'content':
                obj.content = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'organization':
                obj.organization = Reader.read_string(reader)
            elif tag == 'subject':
                obj.subject = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(CertificateReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class CloudInitReader(Reader):

    def __init__(self):
        super(CloudInitReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.CloudInit()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'authorized_keys':
                obj.authorized_keys = AuthorizedKeyReader.read_many(reader)
            elif tag == 'files':
                obj.files = FileReader.read_many(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'network_configuration':
                obj.network_configuration = NetworkConfigurationReader.read_one(reader)
            elif tag == 'regenerate_ssh_keys':
                obj.regenerate_ssh_keys = Reader.read_boolean(reader)
            elif tag == 'timezone':
                obj.timezone = Reader.read_string(reader)
            elif tag == 'users':
                obj.users = UserReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(CloudInitReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ClusterReader(Reader):

    def __init__(self):
        super(ClusterReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Cluster()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'affinity_groups':
                obj.affinity_groups = AffinityGroupReader.read_many(reader)
            elif tag == 'ballooning_enabled':
                obj.ballooning_enabled = Reader.read_boolean(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'cpu':
                obj.cpu = CpuReader.read_one(reader)
            elif tag == 'cpu_profiles':
                obj.cpu_profiles = CpuProfileReader.read_many(reader)
            elif tag == 'data_center':
                obj.data_center = DataCenterReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'display':
                obj.display = DisplayReader.read_one(reader)
            elif tag == 'error_handling':
                obj.error_handling = ErrorHandlingReader.read_one(reader)
            elif tag == 'fencing_policy':
                obj.fencing_policy = FencingPolicyReader.read_one(reader)
            elif tag == 'gluster_hooks':
                obj.gluster_hooks = GlusterHookReader.read_many(reader)
            elif tag == 'gluster_service':
                obj.gluster_service = Reader.read_boolean(reader)
            elif tag == 'gluster_volumes':
                obj.gluster_volumes = GlusterVolumeReader.read_many(reader)
            elif tag == 'ha_reservation':
                obj.ha_reservation = Reader.read_boolean(reader)
            elif tag == 'ksm':
                obj.ksm = KsmReader.read_one(reader)
            elif tag == 'mac_pool':
                obj.mac_pool = MacPoolReader.read_one(reader)
            elif tag == 'maintenance_reason_required':
                obj.maintenance_reason_required = Reader.read_boolean(reader)
            elif tag == 'management_network':
                obj.management_network = NetworkReader.read_one(reader)
            elif tag == 'memory_policy':
                obj.memory_policy = MemoryPolicyReader.read_one(reader)
            elif tag == 'migration':
                obj.migration = MigrationOptionsReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'network_filters':
                obj.network_filters = NetworkFilterReader.read_many(reader)
            elif tag == 'networks':
                obj.networks = NetworkReader.read_many(reader)
            elif tag == 'optional_reason':
                obj.optional_reason = Reader.read_boolean(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'required_rng_sources':
                reader.next_element()
            elif tag == 'scheduling_policy':
                obj.scheduling_policy = SchedulingPolicyReader.read_one(reader)
            elif tag == 'serial_number':
                obj.serial_number = SerialNumberReader.read_one(reader)
            elif tag == 'supported_versions':
                obj.supported_versions = VersionReader.read_many(reader)
            elif tag == 'threads_as_cores':
                obj.threads_as_cores = Reader.read_boolean(reader)
            elif tag == 'trusted_service':
                obj.trusted_service = Reader.read_boolean(reader)
            elif tag == 'tunnel_migration':
                obj.tunnel_migration = Reader.read_boolean(reader)
            elif tag == 'version':
                obj.version = VersionReader.read_one(reader)
            elif tag == 'virt_service':
                obj.virt_service = Reader.read_boolean(reader)
            elif tag == 'link':
                ClusterReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ClusterReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "affinitygroups":
                obj.affinity_groups = list
            elif rel == "cpuprofiles":
                obj.cpu_profiles = list
            elif rel == "glusterhooks":
                obj.gluster_hooks = list
            elif rel == "glustervolumes":
                obj.gluster_volumes = list
            elif rel == "networkfilters":
                obj.network_filters = list
            elif rel == "networks":
                obj.networks = list
            elif rel == "permissions":
                obj.permissions = list
        reader.next_element()


class ClusterLevelReader(Reader):

    def __init__(self):
        super(ClusterLevelReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ClusterLevel()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'cpu_types':
                obj.cpu_types = CpuTypeReader.read_many(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ClusterLevelReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ConfigurationReader(Reader):

    def __init__(self):
        super(ConfigurationReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Configuration()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'data':
                obj.data = Reader.read_string(reader)
            elif tag == 'type':
                obj.type = types.ConfigurationType(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ConfigurationReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ConsoleReader(Reader):

    def __init__(self):
        super(ConsoleReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Console()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ConsoleReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class CoreReader(Reader):

    def __init__(self):
        super(CoreReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Core()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'index':
                obj.index = Reader.read_integer(reader)
            elif tag == 'socket':
                obj.socket = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(CoreReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class CpuReader(Reader):

    def __init__(self):
        super(CpuReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Cpu()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'architecture':
                obj.architecture = types.Architecture(Reader.read_string(reader).lower())
            elif tag == 'cores':
                obj.cores = CoreReader.read_many(reader)
            elif tag == 'cpu_tune':
                obj.cpu_tune = CpuTuneReader.read_one(reader)
            elif tag == 'level':
                obj.level = Reader.read_integer(reader)
            elif tag == 'mode':
                obj.mode = types.CpuMode(Reader.read_string(reader).lower())
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'speed':
                obj.speed = Reader.read_decimal(reader)
            elif tag == 'topology':
                obj.topology = CpuTopologyReader.read_one(reader)
            elif tag == 'type':
                obj.type = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(CpuReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class CpuProfileReader(Reader):

    def __init__(self):
        super(CpuProfileReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.CpuProfile()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'qos':
                obj.qos = QosReader.read_one(reader)
            elif tag == 'link':
                CpuProfileReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(CpuProfileReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "permissions":
                obj.permissions = list
        reader.next_element()


class CpuTopologyReader(Reader):

    def __init__(self):
        super(CpuTopologyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.CpuTopology()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cores':
                obj.cores = Reader.read_integer(reader)
            elif tag == 'sockets':
                obj.sockets = Reader.read_integer(reader)
            elif tag == 'threads':
                obj.threads = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(CpuTopologyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class CpuTuneReader(Reader):

    def __init__(self):
        super(CpuTuneReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.CpuTune()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'vcpu_pins':
                obj.vcpu_pins = VcpuPinReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(CpuTuneReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class CpuTypeReader(Reader):

    def __init__(self):
        super(CpuTypeReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.CpuType()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'architecture':
                obj.architecture = types.Architecture(Reader.read_string(reader).lower())
            elif tag == 'level':
                obj.level = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(CpuTypeReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class CustomPropertyReader(Reader):

    def __init__(self):
        super(CustomPropertyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.CustomProperty()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'regexp':
                obj.regexp = Reader.read_string(reader)
            elif tag == 'value':
                obj.value = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(CustomPropertyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class DataCenterReader(Reader):

    def __init__(self):
        super(DataCenterReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.DataCenter()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'clusters':
                obj.clusters = ClusterReader.read_many(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'iscsi_bonds':
                obj.iscsi_bonds = IscsiBondReader.read_many(reader)
            elif tag == 'local':
                obj.local = Reader.read_boolean(reader)
            elif tag == 'mac_pool':
                obj.mac_pool = MacPoolReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'networks':
                obj.networks = NetworkReader.read_many(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'qoss':
                obj.qoss = QosReader.read_many(reader)
            elif tag == 'quota_mode':
                obj.quota_mode = types.QuotaModeType(Reader.read_string(reader).lower())
            elif tag == 'quotas':
                obj.quotas = QuotaReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.DataCenterStatus(Reader.read_string(reader).lower())
            elif tag == 'storage_domains':
                obj.storage_domains = StorageDomainReader.read_many(reader)
            elif tag == 'storage_format':
                obj.storage_format = types.StorageFormat(Reader.read_string(reader).lower())
            elif tag == 'supported_versions':
                obj.supported_versions = VersionReader.read_many(reader)
            elif tag == 'version':
                obj.version = VersionReader.read_one(reader)
            elif tag == 'link':
                DataCenterReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(DataCenterReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "clusters":
                obj.clusters = list
            elif rel == "iscsibonds":
                obj.iscsi_bonds = list
            elif rel == "networks":
                obj.networks = list
            elif rel == "permissions":
                obj.permissions = list
            elif rel == "qoss":
                obj.qoss = list
            elif rel == "quotas":
                obj.quotas = list
            elif rel == "storagedomains":
                obj.storage_domains = list
        reader.next_element()


class DeviceReader(Reader):

    def __init__(self):
        super(DeviceReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Device()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'link':
                DeviceReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(DeviceReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "vms":
                obj.vms = list
        reader.next_element()


class DiskReader(Reader):

    def __init__(self):
        super(DiskReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Disk()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'active':
                obj.active = Reader.read_boolean(reader)
            elif tag == 'actual_size':
                obj.actual_size = Reader.read_integer(reader)
            elif tag == 'alias':
                obj.alias = Reader.read_string(reader)
            elif tag == 'bootable':
                obj.bootable = Reader.read_boolean(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disk_profile':
                obj.disk_profile = DiskProfileReader.read_one(reader)
            elif tag == 'format':
                obj.format = types.DiskFormat(Reader.read_string(reader).lower())
            elif tag == 'image_id':
                obj.image_id = Reader.read_string(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'interface':
                obj.interface = types.DiskInterface(Reader.read_string(reader).lower())
            elif tag == 'logical_name':
                obj.logical_name = Reader.read_string(reader)
            elif tag == 'lun_storage':
                obj.lun_storage = HostStorageReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'openstack_volume_type':
                obj.openstack_volume_type = OpenStackVolumeTypeReader.read_one(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'propagate_errors':
                obj.propagate_errors = Reader.read_boolean(reader)
            elif tag == 'provisioned_size':
                obj.provisioned_size = Reader.read_integer(reader)
            elif tag == 'quota':
                obj.quota = QuotaReader.read_one(reader)
            elif tag == 'read_only':
                obj.read_only = Reader.read_boolean(reader)
            elif tag == 'sgio':
                obj.sgio = types.ScsiGenericIO(Reader.read_string(reader).lower())
            elif tag == 'shareable':
                obj.shareable = Reader.read_boolean(reader)
            elif tag == 'snapshot':
                obj.snapshot = SnapshotReader.read_one(reader)
            elif tag == 'sparse':
                obj.sparse = Reader.read_boolean(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.DiskStatus(Reader.read_string(reader).lower())
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'storage_domains':
                obj.storage_domains = StorageDomainReader.read_many(reader)
            elif tag == 'storage_type':
                obj.storage_type = types.DiskStorageType(Reader.read_string(reader).lower())
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'uses_scsi_reservation':
                obj.uses_scsi_reservation = Reader.read_boolean(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'wipe_after_delete':
                obj.wipe_after_delete = Reader.read_boolean(reader)
            elif tag == 'link':
                DiskReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(DiskReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "permissions":
                obj.permissions = list
            elif rel == "statistics":
                obj.statistics = list
            elif rel == "storagedomains":
                obj.storage_domains = list
            elif rel == "vms":
                obj.vms = list
        reader.next_element()


class DiskAttachmentReader(Reader):

    def __init__(self):
        super(DiskAttachmentReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.DiskAttachment()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'bootable':
                obj.bootable = Reader.read_boolean(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disk':
                obj.disk = DiskReader.read_one(reader)
            elif tag == 'interface':
                obj.interface = types.DiskInterface(Reader.read_string(reader).lower())
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(DiskAttachmentReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class DiskProfileReader(Reader):

    def __init__(self):
        super(DiskProfileReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.DiskProfile()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'qos':
                obj.qos = QosReader.read_one(reader)
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'link':
                DiskProfileReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(DiskProfileReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "permissions":
                obj.permissions = list
        reader.next_element()


class DiskSnapshotReader(Reader):

    def __init__(self):
        super(DiskSnapshotReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.DiskSnapshot()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'active':
                obj.active = Reader.read_boolean(reader)
            elif tag == 'actual_size':
                obj.actual_size = Reader.read_integer(reader)
            elif tag == 'alias':
                obj.alias = Reader.read_string(reader)
            elif tag == 'bootable':
                obj.bootable = Reader.read_boolean(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disk':
                obj.disk = DiskReader.read_one(reader)
            elif tag == 'disk_profile':
                obj.disk_profile = DiskProfileReader.read_one(reader)
            elif tag == 'format':
                obj.format = types.DiskFormat(Reader.read_string(reader).lower())
            elif tag == 'image_id':
                obj.image_id = Reader.read_string(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'interface':
                obj.interface = types.DiskInterface(Reader.read_string(reader).lower())
            elif tag == 'logical_name':
                obj.logical_name = Reader.read_string(reader)
            elif tag == 'lun_storage':
                obj.lun_storage = HostStorageReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'openstack_volume_type':
                obj.openstack_volume_type = OpenStackVolumeTypeReader.read_one(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'propagate_errors':
                obj.propagate_errors = Reader.read_boolean(reader)
            elif tag == 'provisioned_size':
                obj.provisioned_size = Reader.read_integer(reader)
            elif tag == 'quota':
                obj.quota = QuotaReader.read_one(reader)
            elif tag == 'read_only':
                obj.read_only = Reader.read_boolean(reader)
            elif tag == 'sgio':
                obj.sgio = types.ScsiGenericIO(Reader.read_string(reader).lower())
            elif tag == 'shareable':
                obj.shareable = Reader.read_boolean(reader)
            elif tag == 'snapshot':
                obj.snapshot = SnapshotReader.read_one(reader)
            elif tag == 'sparse':
                obj.sparse = Reader.read_boolean(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.DiskStatus(Reader.read_string(reader).lower())
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'storage_domains':
                obj.storage_domains = StorageDomainReader.read_many(reader)
            elif tag == 'storage_type':
                obj.storage_type = types.DiskStorageType(Reader.read_string(reader).lower())
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'uses_scsi_reservation':
                obj.uses_scsi_reservation = Reader.read_boolean(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'wipe_after_delete':
                obj.wipe_after_delete = Reader.read_boolean(reader)
            elif tag == 'link':
                DiskSnapshotReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(DiskSnapshotReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "permissions":
                obj.permissions = list
            elif rel == "statistics":
                obj.statistics = list
            elif rel == "storagedomains":
                obj.storage_domains = list
            elif rel == "vms":
                obj.vms = list
        reader.next_element()


class DisplayReader(Reader):

    def __init__(self):
        super(DisplayReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Display()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'allow_override':
                obj.allow_override = Reader.read_boolean(reader)
            elif tag == 'certificate':
                obj.certificate = CertificateReader.read_one(reader)
            elif tag == 'copy_paste_enabled':
                obj.copy_paste_enabled = Reader.read_boolean(reader)
            elif tag == 'disconnect_action':
                obj.disconnect_action = Reader.read_string(reader)
            elif tag == 'file_transfer_enabled':
                obj.file_transfer_enabled = Reader.read_boolean(reader)
            elif tag == 'keyboard_layout':
                obj.keyboard_layout = Reader.read_string(reader)
            elif tag == 'monitors':
                obj.monitors = Reader.read_integer(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'proxy':
                obj.proxy = Reader.read_string(reader)
            elif tag == 'secure_port':
                obj.secure_port = Reader.read_integer(reader)
            elif tag == 'single_qxl_pci':
                obj.single_qxl_pci = Reader.read_boolean(reader)
            elif tag == 'smartcard_enabled':
                obj.smartcard_enabled = Reader.read_boolean(reader)
            elif tag == 'type':
                obj.type = types.DisplayType(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(DisplayReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class DnsReader(Reader):

    def __init__(self):
        super(DnsReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Dns()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'search_domains':
                obj.search_domains = HostReader.read_many(reader)
            elif tag == 'servers':
                obj.servers = HostReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(DnsReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class DomainReader(Reader):

    def __init__(self):
        super(DomainReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Domain()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'groups':
                obj.groups = GroupReader.read_many(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'user':
                obj.user = UserReader.read_one(reader)
            elif tag == 'users':
                obj.users = UserReader.read_many(reader)
            elif tag == 'link':
                DomainReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(DomainReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "groups":
                obj.groups = list
            elif rel == "users":
                obj.users = list
        reader.next_element()


class EntityProfileDetailReader(Reader):

    def __init__(self):
        super(EntityProfileDetailReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.EntityProfileDetail()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'profile_details':
                obj.profile_details = ProfileDetailReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(EntityProfileDetailReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ErrorHandlingReader(Reader):

    def __init__(self):
        super(ErrorHandlingReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ErrorHandling()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'on_error':
                obj.on_error = types.MigrateOnError(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ErrorHandlingReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class EventReader(Reader):

    def __init__(self):
        super(EventReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Event()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'code':
                obj.code = Reader.read_integer(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'correlation_id':
                obj.correlation_id = Reader.read_string(reader)
            elif tag == 'custom_data':
                obj.custom_data = Reader.read_string(reader)
            elif tag == 'custom_id':
                obj.custom_id = Reader.read_integer(reader)
            elif tag == 'data_center':
                obj.data_center = DataCenterReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'flood_rate':
                obj.flood_rate = Reader.read_integer(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'origin':
                obj.origin = Reader.read_string(reader)
            elif tag == 'severity':
                obj.severity = types.LogSeverity(Reader.read_string(reader).lower())
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'time':
                obj.time = Reader.read_date(reader)
            elif tag == 'user':
                obj.user = UserReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(EventReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ExternalComputeResourceReader(Reader):

    def __init__(self):
        super(ExternalComputeResourceReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ExternalComputeResource()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'external_host_provider':
                obj.external_host_provider = ExternalHostProviderReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'provider':
                obj.provider = Reader.read_string(reader)
            elif tag == 'url':
                obj.url = Reader.read_string(reader)
            elif tag == 'user':
                obj.user = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ExternalComputeResourceReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ExternalDiscoveredHostReader(Reader):

    def __init__(self):
        super(ExternalDiscoveredHostReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ExternalDiscoveredHost()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'external_host_provider':
                obj.external_host_provider = ExternalHostProviderReader.read_one(reader)
            elif tag == 'ip':
                obj.ip = Reader.read_string(reader)
            elif tag == 'last_report':
                obj.last_report = Reader.read_string(reader)
            elif tag == 'mac':
                obj.mac = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'subnet_name':
                obj.subnet_name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ExternalDiscoveredHostReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ExternalHostReader(Reader):

    def __init__(self):
        super(ExternalHostReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ExternalHost()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'external_host_provider':
                obj.external_host_provider = ExternalHostProviderReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ExternalHostReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ExternalHostGroupReader(Reader):

    def __init__(self):
        super(ExternalHostGroupReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ExternalHostGroup()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'architecture_name':
                obj.architecture_name = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'domain_name':
                obj.domain_name = Reader.read_string(reader)
            elif tag == 'external_host_provider':
                obj.external_host_provider = ExternalHostProviderReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'operating_system_name':
                obj.operating_system_name = Reader.read_string(reader)
            elif tag == 'subnet_name':
                obj.subnet_name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ExternalHostGroupReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ExternalHostProviderReader(Reader):

    def __init__(self):
        super(ExternalHostProviderReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ExternalHostProvider()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'authentication_url':
                obj.authentication_url = Reader.read_string(reader)
            elif tag == 'certificates':
                obj.certificates = CertificateReader.read_many(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'compute_resources':
                obj.compute_resources = ExternalComputeResourceReader.read_many(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'discovered_hosts':
                obj.discovered_hosts = ExternalDiscoveredHostReader.read_many(reader)
            elif tag == 'host_groups':
                obj.host_groups = ExternalHostGroupReader.read_many(reader)
            elif tag == 'hosts':
                obj.hosts = HostReader.read_many(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            elif tag == 'requires_authentication':
                obj.requires_authentication = Reader.read_boolean(reader)
            elif tag == 'url':
                obj.url = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            elif tag == 'link':
                ExternalHostProviderReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ExternalHostProviderReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "certificates":
                obj.certificates = list
            elif rel == "computeresources":
                obj.compute_resources = list
            elif rel == "discoveredhosts":
                obj.discovered_hosts = list
            elif rel == "hostgroups":
                obj.host_groups = list
            elif rel == "hosts":
                obj.hosts = list
        reader.next_element()


class ExternalProviderReader(Reader):

    def __init__(self):
        super(ExternalProviderReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ExternalProvider()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'authentication_url':
                obj.authentication_url = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            elif tag == 'requires_authentication':
                obj.requires_authentication = Reader.read_boolean(reader)
            elif tag == 'url':
                obj.url = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ExternalProviderReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class FaultReader(Reader):

    def __init__(self):
        super(FaultReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Fault()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'detail':
                obj.detail = Reader.read_string(reader)
            elif tag == 'reason':
                obj.reason = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(FaultReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class FencingPolicyReader(Reader):

    def __init__(self):
        super(FencingPolicyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.FencingPolicy()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            elif tag == 'skip_if_connectivity_broken':
                obj.skip_if_connectivity_broken = SkipIfConnectivityBrokenReader.read_one(reader)
            elif tag == 'skip_if_sd_active':
                obj.skip_if_sd_active = SkipIfSdActiveReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(FencingPolicyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class FileReader(Reader):

    def __init__(self):
        super(FileReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.File()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'content':
                obj.content = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'type':
                obj.type = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(FileReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class FilterReader(Reader):

    def __init__(self):
        super(FilterReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Filter()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'position':
                obj.position = Reader.read_integer(reader)
            elif tag == 'scheduling_policy_unit':
                obj.scheduling_policy_unit = SchedulingPolicyUnitReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(FilterReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class FloppyReader(Reader):

    def __init__(self):
        super(FloppyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Floppy()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'file':
                obj.file = FileReader.read_one(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'link':
                FloppyReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(FloppyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "vms":
                obj.vms = list
        reader.next_element()


class FopStatisticReader(Reader):

    def __init__(self):
        super(FopStatisticReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.FopStatistic()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(FopStatisticReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class GlusterBrickReader(Reader):

    def __init__(self):
        super(GlusterBrickReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GlusterBrick()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'brick_dir':
                obj.brick_dir = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'device':
                obj.device = Reader.read_string(reader)
            elif tag == 'fs_name':
                obj.fs_name = Reader.read_string(reader)
            elif tag == 'gluster_clients':
                obj.gluster_clients = GlusterClientReader.read_many(reader)
            elif tag == 'gluster_volume':
                obj.gluster_volume = GlusterVolumeReader.read_one(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'memory_pools':
                obj.memory_pools = GlusterMemoryPoolReader.read_many(reader)
            elif tag == 'mnt_options':
                obj.mnt_options = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'pid':
                obj.pid = Reader.read_integer(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'server_id':
                obj.server_id = Reader.read_string(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.GlusterBrickStatus(Reader.read_string(reader).lower())
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'link':
                GlusterBrickReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GlusterBrickReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "statistics":
                obj.statistics = list
            elif rel == "vms":
                obj.vms = list
        reader.next_element()


class GlusterBrickAdvancedDetailsReader(Reader):

    def __init__(self):
        super(GlusterBrickAdvancedDetailsReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GlusterBrickAdvancedDetails()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'device':
                obj.device = Reader.read_string(reader)
            elif tag == 'fs_name':
                obj.fs_name = Reader.read_string(reader)
            elif tag == 'gluster_clients':
                obj.gluster_clients = GlusterClientReader.read_many(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'memory_pools':
                obj.memory_pools = GlusterMemoryPoolReader.read_many(reader)
            elif tag == 'mnt_options':
                obj.mnt_options = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'pid':
                obj.pid = Reader.read_integer(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'link':
                GlusterBrickAdvancedDetailsReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GlusterBrickAdvancedDetailsReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "vms":
                obj.vms = list
        reader.next_element()


class GlusterBrickMemoryInfoReader(Reader):

    def __init__(self):
        super(GlusterBrickMemoryInfoReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GlusterBrickMemoryInfo()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'memory_pools':
                obj.memory_pools = GlusterMemoryPoolReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GlusterBrickMemoryInfoReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class GlusterClientReader(Reader):

    def __init__(self):
        super(GlusterClientReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GlusterClient()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'bytes_read':
                obj.bytes_read = Reader.read_integer(reader)
            elif tag == 'bytes_written':
                obj.bytes_written = Reader.read_integer(reader)
            elif tag == 'client_port':
                obj.client_port = Reader.read_integer(reader)
            elif tag == 'host_name':
                obj.host_name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GlusterClientReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class GlusterHookReader(Reader):

    def __init__(self):
        super(GlusterHookReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GlusterHook()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'checksum':
                obj.checksum = Reader.read_string(reader)
            elif tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'conflict_status':
                obj.conflict_status = Reader.read_integer(reader)
            elif tag == 'conflicts':
                obj.conflicts = Reader.read_string(reader)
            elif tag == 'content':
                obj.content = Reader.read_string(reader)
            elif tag == 'content_type':
                obj.content_type = types.HookContentType(Reader.read_string(reader).lower())
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'gluster_command':
                obj.gluster_command = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'server_hooks':
                obj.server_hooks = GlusterServerHookReader.read_many(reader)
            elif tag == 'stage':
                obj.stage = types.HookStage(Reader.read_string(reader).lower())
            elif tag == 'status':
                obj.status = types.GlusterHookStatus(Reader.read_string(reader).lower())
            elif tag == 'link':
                GlusterHookReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GlusterHookReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "serverhooks":
                obj.server_hooks = list
        reader.next_element()


class GlusterMemoryPoolReader(Reader):

    def __init__(self):
        super(GlusterMemoryPoolReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GlusterMemoryPool()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'alloc_count':
                obj.alloc_count = Reader.read_integer(reader)
            elif tag == 'cold_count':
                obj.cold_count = Reader.read_integer(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'hot_count':
                obj.hot_count = Reader.read_integer(reader)
            elif tag == 'max_alloc':
                obj.max_alloc = Reader.read_integer(reader)
            elif tag == 'max_stdalloc':
                obj.max_stdalloc = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'padded_size':
                obj.padded_size = Reader.read_integer(reader)
            elif tag == 'pool_misses':
                obj.pool_misses = Reader.read_integer(reader)
            elif tag == 'type':
                obj.type = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GlusterMemoryPoolReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class GlusterServerHookReader(Reader):

    def __init__(self):
        super(GlusterServerHookReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GlusterServerHook()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'checksum':
                obj.checksum = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'content_type':
                obj.content_type = types.HookContentType(Reader.read_string(reader).lower())
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'status':
                obj.status = types.GlusterHookStatus(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GlusterServerHookReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class GlusterVolumeReader(Reader):

    def __init__(self):
        super(GlusterVolumeReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GlusterVolume()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'bricks':
                obj.bricks = GlusterBrickReader.read_many(reader)
            elif tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disperse_count':
                obj.disperse_count = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'options':
                obj.options = OptionReader.read_many(reader)
            elif tag == 'redundancy_count':
                obj.redundancy_count = Reader.read_integer(reader)
            elif tag == 'replica_count':
                obj.replica_count = Reader.read_integer(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.GlusterVolumeStatus(Reader.read_string(reader).lower())
            elif tag == 'stripe_count':
                obj.stripe_count = Reader.read_integer(reader)
            elif tag == 'transport_types':
                reader.next_element()
            elif tag == 'volume_type':
                obj.volume_type = types.GlusterVolumeType(Reader.read_string(reader).lower())
            elif tag == 'link':
                GlusterVolumeReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GlusterVolumeReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "bricks":
                obj.bricks = list
            elif rel == "statistics":
                obj.statistics = list
        reader.next_element()


class GlusterVolumeProfileDetailsReader(Reader):

    def __init__(self):
        super(GlusterVolumeProfileDetailsReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GlusterVolumeProfileDetails()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'brick_profile_details':
                obj.brick_profile_details = BrickProfileDetailReader.read_many(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'nfs_profile_details':
                obj.nfs_profile_details = NfsProfileDetailReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GlusterVolumeProfileDetailsReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class GracePeriodReader(Reader):

    def __init__(self):
        super(GracePeriodReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GracePeriod()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'expiry':
                obj.expiry = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GracePeriodReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class GraphicsConsoleReader(Reader):

    def __init__(self):
        super(GraphicsConsoleReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GraphicsConsole()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'protocol':
                obj.protocol = types.GraphicsType(Reader.read_string(reader).lower())
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'tls_port':
                obj.tls_port = Reader.read_integer(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GraphicsConsoleReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class GroupReader(Reader):

    def __init__(self):
        super(GroupReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Group()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'domain':
                obj.domain = DomainReader.read_one(reader)
            elif tag == 'domain_entry_id':
                obj.domain_entry_id = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'namespace':
                obj.namespace = Reader.read_string(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'roles':
                obj.roles = RoleReader.read_many(reader)
            elif tag == 'tags':
                obj.tags = TagReader.read_many(reader)
            elif tag == 'link':
                GroupReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GroupReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "permissions":
                obj.permissions = list
            elif rel == "roles":
                obj.roles = list
            elif rel == "tags":
                obj.tags = list
        reader.next_element()


class GuestOperatingSystemReader(Reader):

    def __init__(self):
        super(GuestOperatingSystemReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.GuestOperatingSystem()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'architecture':
                obj.architecture = Reader.read_string(reader)
            elif tag == 'codename':
                obj.codename = Reader.read_string(reader)
            elif tag == 'distribution':
                obj.distribution = Reader.read_string(reader)
            elif tag == 'family':
                obj.family = Reader.read_string(reader)
            elif tag == 'kernel':
                obj.kernel = KernelReader.read_one(reader)
            elif tag == 'version':
                obj.version = VersionReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(GuestOperatingSystemReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class HardwareInformationReader(Reader):

    def __init__(self):
        super(HardwareInformationReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.HardwareInformation()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'family':
                obj.family = Reader.read_string(reader)
            elif tag == 'manufacturer':
                obj.manufacturer = Reader.read_string(reader)
            elif tag == 'product_name':
                obj.product_name = Reader.read_string(reader)
            elif tag == 'serial_number':
                obj.serial_number = Reader.read_string(reader)
            elif tag == 'supported_rng_sources':
                reader.next_element()
            elif tag == 'uuid':
                obj.uuid = Reader.read_string(reader)
            elif tag == 'version':
                obj.version = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(HardwareInformationReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class HighAvailabilityReader(Reader):

    def __init__(self):
        super(HighAvailabilityReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.HighAvailability()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            elif tag == 'priority':
                obj.priority = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(HighAvailabilityReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class HookReader(Reader):

    def __init__(self):
        super(HookReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Hook()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'event_name':
                obj.event_name = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'md5':
                obj.md5 = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(HookReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class HostReader(Reader):

    def __init__(self):
        super(HostReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Host()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'affinity_labels':
                obj.affinity_labels = AffinityLabelReader.read_many(reader)
            elif tag == 'agents':
                obj.agents = AgentReader.read_many(reader)
            elif tag == 'auto_numa_status':
                obj.auto_numa_status = types.AutoNumaStatus(Reader.read_string(reader).lower())
            elif tag == 'certificate':
                obj.certificate = CertificateReader.read_one(reader)
            elif tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'cpu':
                obj.cpu = CpuReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'device_passthrough':
                obj.device_passthrough = HostDevicePassthroughReader.read_one(reader)
            elif tag == 'devices':
                obj.devices = DeviceReader.read_many(reader)
            elif tag == 'display':
                obj.display = DisplayReader.read_one(reader)
            elif tag == 'external_host_provider':
                obj.external_host_provider = ExternalHostProviderReader.read_one(reader)
            elif tag == 'external_status':
                obj.external_status = types.ExternalStatus(Reader.read_string(reader).lower())
            elif tag == 'hardware_information':
                obj.hardware_information = HardwareInformationReader.read_one(reader)
            elif tag == 'hooks':
                obj.hooks = HookReader.read_many(reader)
            elif tag == 'hosted_engine':
                obj.hosted_engine = HostedEngineReader.read_one(reader)
            elif tag == 'iscsi':
                obj.iscsi = IscsiDetailsReader.read_one(reader)
            elif tag == 'katello_errata':
                obj.katello_errata = KatelloErratumReader.read_many(reader)
            elif tag == 'kdump_status':
                obj.kdump_status = types.KdumpStatus(Reader.read_string(reader).lower())
            elif tag == 'ksm':
                obj.ksm = KsmReader.read_one(reader)
            elif tag == 'libvirt_version':
                obj.libvirt_version = VersionReader.read_one(reader)
            elif tag == 'max_scheduling_memory':
                obj.max_scheduling_memory = Reader.read_integer(reader)
            elif tag == 'memory':
                obj.memory = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'network_attachments':
                obj.network_attachments = NetworkAttachmentReader.read_many(reader)
            elif tag == 'nics':
                obj.nics = NicReader.read_many(reader)
            elif tag == 'host_numa_nodes':
                obj.numa_nodes = NumaNodeReader.read_many(reader)
            elif tag == 'numa_supported':
                obj.numa_supported = Reader.read_boolean(reader)
            elif tag == 'os':
                obj.os = OperatingSystemReader.read_one(reader)
            elif tag == 'override_iptables':
                obj.override_iptables = Reader.read_boolean(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'power_management':
                obj.power_management = PowerManagementReader.read_one(reader)
            elif tag == 'protocol':
                obj.protocol = types.HostProtocol(Reader.read_string(reader).lower())
            elif tag == 'root_password':
                obj.root_password = Reader.read_string(reader)
            elif tag == 'se_linux':
                obj.se_linux = SeLinuxReader.read_one(reader)
            elif tag == 'spm':
                obj.spm = SpmReader.read_one(reader)
            elif tag == 'ssh':
                obj.ssh = SshReader.read_one(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.HostStatus(Reader.read_string(reader).lower())
            elif tag == 'status_detail':
                obj.status_detail = Reader.read_string(reader)
            elif tag == 'storage_connection_extensions':
                obj.storage_connection_extensions = StorageConnectionExtensionReader.read_many(reader)
            elif tag == 'storages':
                obj.storages = HostStorageReader.read_many(reader)
            elif tag == 'summary':
                obj.summary = VmSummaryReader.read_one(reader)
            elif tag == 'tags':
                obj.tags = TagReader.read_many(reader)
            elif tag == 'transparent_hugepages':
                obj.transparent_huge_pages = TransparentHugePagesReader.read_one(reader)
            elif tag == 'type':
                obj.type = types.HostType(Reader.read_string(reader).lower())
            elif tag == 'unmanaged_networks':
                obj.unmanaged_networks = UnmanagedNetworkReader.read_many(reader)
            elif tag == 'update_available':
                obj.update_available = Reader.read_boolean(reader)
            elif tag == 'version':
                obj.version = VersionReader.read_one(reader)
            elif tag == 'link':
                HostReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(HostReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "affinitylabels":
                obj.affinity_labels = list
            elif rel == "agents":
                obj.agents = list
            elif rel == "devices":
                obj.devices = list
            elif rel == "hooks":
                obj.hooks = list
            elif rel == "katelloerrata":
                obj.katello_errata = list
            elif rel == "networkattachments":
                obj.network_attachments = list
            elif rel == "nics":
                obj.nics = list
            elif rel == "numanodes":
                obj.numa_nodes = list
            elif rel == "permissions":
                obj.permissions = list
            elif rel == "statistics":
                obj.statistics = list
            elif rel == "storageconnectionextensions":
                obj.storage_connection_extensions = list
            elif rel == "storages":
                obj.storages = list
            elif rel == "tags":
                obj.tags = list
            elif rel == "unmanagednetworks":
                obj.unmanaged_networks = list
        reader.next_element()


class HostDeviceReader(Reader):

    def __init__(self):
        super(HostDeviceReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.HostDevice()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'capability':
                obj.capability = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'iommu_group':
                obj.iommu_group = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'parent_device':
                obj.parent_device = HostDeviceReader.read_one(reader)
            elif tag == 'physical_function':
                obj.physical_function = HostDeviceReader.read_one(reader)
            elif tag == 'placeholder':
                obj.placeholder = Reader.read_boolean(reader)
            elif tag == 'product':
                obj.product = ProductReader.read_one(reader)
            elif tag == 'vendor':
                obj.vendor = VendorReader.read_one(reader)
            elif tag == 'virtual_functions':
                obj.virtual_functions = Reader.read_integer(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(HostDeviceReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class HostDevicePassthroughReader(Reader):

    def __init__(self):
        super(HostDevicePassthroughReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.HostDevicePassthrough()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(HostDevicePassthroughReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class HostNicReader(Reader):

    def __init__(self):
        super(HostNicReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.HostNic()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'base_interface':
                obj.base_interface = Reader.read_string(reader)
            elif tag == 'bonding':
                obj.bonding = BondingReader.read_one(reader)
            elif tag == 'boot_protocol':
                obj.boot_protocol = types.BootProtocol(Reader.read_string(reader).lower())
            elif tag == 'bridged':
                obj.bridged = Reader.read_boolean(reader)
            elif tag == 'check_connectivity':
                obj.check_connectivity = Reader.read_boolean(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'custom_configuration':
                obj.custom_configuration = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'ip':
                obj.ip = IpReader.read_one(reader)
            elif tag == 'ipv6':
                obj.ipv6 = IpReader.read_one(reader)
            elif tag == 'ipv6_boot_protocol':
                obj.ipv6_boot_protocol = types.BootProtocol(Reader.read_string(reader).lower())
            elif tag == 'mac':
                obj.mac = MacReader.read_one(reader)
            elif tag == 'mtu':
                obj.mtu = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'network':
                obj.network = NetworkReader.read_one(reader)
            elif tag == 'network_labels':
                obj.network_labels = NetworkLabelReader.read_many(reader)
            elif tag == 'override_configuration':
                obj.override_configuration = Reader.read_boolean(reader)
            elif tag == 'physical_function':
                obj.physical_function = HostNicReader.read_one(reader)
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            elif tag == 'qos':
                obj.qos = QosReader.read_one(reader)
            elif tag == 'speed':
                obj.speed = Reader.read_integer(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.NicStatus(Reader.read_string(reader).lower())
            elif tag == 'virtual_functions_configuration':
                obj.virtual_functions_configuration = HostNicVirtualFunctionsConfigurationReader.read_one(reader)
            elif tag == 'vlan':
                obj.vlan = VlanReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(HostNicReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class HostNicVirtualFunctionsConfigurationReader(Reader):

    def __init__(self):
        super(HostNicVirtualFunctionsConfigurationReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.HostNicVirtualFunctionsConfiguration()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'all_networks_allowed':
                obj.all_networks_allowed = Reader.read_boolean(reader)
            elif tag == 'max_number_of_virtual_functions':
                obj.max_number_of_virtual_functions = Reader.read_integer(reader)
            elif tag == 'number_of_virtual_functions':
                obj.number_of_virtual_functions = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(HostNicVirtualFunctionsConfigurationReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class HostStorageReader(Reader):

    def __init__(self):
        super(HostStorageReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.HostStorage()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'logical_units':
                obj.logical_units = LogicalUnitReader.read_many(reader)
            elif tag == 'mount_options':
                obj.mount_options = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'nfs_retrans':
                obj.nfs_retrans = Reader.read_integer(reader)
            elif tag == 'nfs_timeo':
                obj.nfs_timeo = Reader.read_integer(reader)
            elif tag == 'nfs_version':
                obj.nfs_version = types.NfsVersion(Reader.read_string(reader).lower())
            elif tag == 'override_luns':
                obj.override_luns = Reader.read_boolean(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'path':
                obj.path = Reader.read_string(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'portal':
                obj.portal = Reader.read_string(reader)
            elif tag == 'target':
                obj.target = Reader.read_string(reader)
            elif tag == 'type':
                obj.type = types.StorageType(Reader.read_string(reader).lower())
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            elif tag == 'vfs_type':
                obj.vfs_type = Reader.read_string(reader)
            elif tag == 'volume_group':
                obj.volume_group = VolumeGroupReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(HostStorageReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class HostedEngineReader(Reader):

    def __init__(self):
        super(HostedEngineReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.HostedEngine()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'active':
                obj.active = Reader.read_boolean(reader)
            elif tag == 'configured':
                obj.configured = Reader.read_boolean(reader)
            elif tag == 'global_maintenance':
                obj.global_maintenance = Reader.read_boolean(reader)
            elif tag == 'local_maintenance':
                obj.local_maintenance = Reader.read_boolean(reader)
            elif tag == 'score':
                obj.score = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(HostedEngineReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class IconReader(Reader):

    def __init__(self):
        super(IconReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Icon()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'data':
                obj.data = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'media_type':
                obj.media_type = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(IconReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class IdentifiedReader(Reader):

    def __init__(self):
        super(IdentifiedReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Identified()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(IdentifiedReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ImageReader(Reader):

    def __init__(self):
        super(ImageReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Image()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ImageReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class InitializationReader(Reader):

    def __init__(self):
        super(InitializationReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Initialization()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'active_directory_ou':
                obj.active_directory_ou = Reader.read_string(reader)
            elif tag == 'authorized_ssh_keys':
                obj.authorized_ssh_keys = Reader.read_string(reader)
            elif tag == 'cloud_init':
                obj.cloud_init = CloudInitReader.read_one(reader)
            elif tag == 'configuration':
                obj.configuration = ConfigurationReader.read_one(reader)
            elif tag == 'custom_script':
                obj.custom_script = Reader.read_string(reader)
            elif tag == 'dns_search':
                obj.dns_search = Reader.read_string(reader)
            elif tag == 'dns_servers':
                obj.dns_servers = Reader.read_string(reader)
            elif tag == 'domain':
                obj.domain = Reader.read_string(reader)
            elif tag == 'host_name':
                obj.host_name = Reader.read_string(reader)
            elif tag == 'input_locale':
                obj.input_locale = Reader.read_string(reader)
            elif tag == 'nic_configurations':
                obj.nic_configurations = NicConfigurationReader.read_many(reader)
            elif tag == 'org_name':
                obj.org_name = Reader.read_string(reader)
            elif tag == 'regenerate_ids':
                obj.regenerate_ids = Reader.read_boolean(reader)
            elif tag == 'regenerate_ssh_keys':
                obj.regenerate_ssh_keys = Reader.read_boolean(reader)
            elif tag == 'root_password':
                obj.root_password = Reader.read_string(reader)
            elif tag == 'system_locale':
                obj.system_locale = Reader.read_string(reader)
            elif tag == 'timezone':
                obj.timezone = Reader.read_string(reader)
            elif tag == 'ui_language':
                obj.ui_language = Reader.read_string(reader)
            elif tag == 'user_locale':
                obj.user_locale = Reader.read_string(reader)
            elif tag == 'user_name':
                obj.user_name = Reader.read_string(reader)
            elif tag == 'windows_license_key':
                obj.windows_license_key = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(InitializationReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class InstanceTypeReader(Reader):

    def __init__(self):
        super(InstanceTypeReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.InstanceType()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'bios':
                obj.bios = BiosReader.read_one(reader)
            elif tag == 'cdroms':
                obj.cdroms = CdromReader.read_many(reader)
            elif tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'console':
                obj.console = ConsoleReader.read_one(reader)
            elif tag == 'cpu':
                obj.cpu = CpuReader.read_one(reader)
            elif tag == 'cpu_profile':
                obj.cpu_profile = CpuProfileReader.read_one(reader)
            elif tag == 'cpu_shares':
                obj.cpu_shares = Reader.read_integer(reader)
            elif tag == 'creation_time':
                obj.creation_time = Reader.read_date(reader)
            elif tag == 'custom_compatibility_version':
                obj.custom_compatibility_version = VersionReader.read_one(reader)
            elif tag == 'custom_cpu_model':
                obj.custom_cpu_model = Reader.read_string(reader)
            elif tag == 'custom_emulated_machine':
                obj.custom_emulated_machine = Reader.read_string(reader)
            elif tag == 'custom_properties':
                obj.custom_properties = CustomPropertyReader.read_many(reader)
            elif tag == 'delete_protected':
                obj.delete_protected = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disks':
                obj.disks = DiskReader.read_many(reader)
            elif tag == 'display':
                obj.display = DisplayReader.read_one(reader)
            elif tag == 'domain':
                obj.domain = DomainReader.read_one(reader)
            elif tag == 'graphics_consoles':
                obj.graphics_consoles = GraphicsConsoleReader.read_many(reader)
            elif tag == 'high_availability':
                obj.high_availability = HighAvailabilityReader.read_one(reader)
            elif tag == 'initialization':
                obj.initialization = InitializationReader.read_one(reader)
            elif tag == 'io':
                obj.io = IoReader.read_one(reader)
            elif tag == 'large_icon':
                obj.large_icon = IconReader.read_one(reader)
            elif tag == 'memory':
                obj.memory = Reader.read_integer(reader)
            elif tag == 'memory_policy':
                obj.memory_policy = MemoryPolicyReader.read_one(reader)
            elif tag == 'migration':
                obj.migration = MigrationOptionsReader.read_one(reader)
            elif tag == 'migration_downtime':
                obj.migration_downtime = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'nics':
                obj.nics = NicReader.read_many(reader)
            elif tag == 'origin':
                obj.origin = Reader.read_string(reader)
            elif tag == 'os':
                obj.os = OperatingSystemReader.read_one(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'rng_device':
                obj.rng_device = RngDeviceReader.read_one(reader)
            elif tag == 'serial_number':
                obj.serial_number = SerialNumberReader.read_one(reader)
            elif tag == 'small_icon':
                obj.small_icon = IconReader.read_one(reader)
            elif tag == 'soundcard_enabled':
                obj.soundcard_enabled = Reader.read_boolean(reader)
            elif tag == 'sso':
                obj.sso = SsoReader.read_one(reader)
            elif tag == 'start_paused':
                obj.start_paused = Reader.read_boolean(reader)
            elif tag == 'stateless':
                obj.stateless = Reader.read_boolean(reader)
            elif tag == 'status':
                obj.status = types.TemplateStatus(Reader.read_string(reader).lower())
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'tags':
                obj.tags = TagReader.read_many(reader)
            elif tag == 'time_zone':
                obj.time_zone = TimeZoneReader.read_one(reader)
            elif tag == 'tunnel_migration':
                obj.tunnel_migration = Reader.read_boolean(reader)
            elif tag == 'type':
                obj.type = types.VmType(Reader.read_string(reader).lower())
            elif tag == 'usb':
                obj.usb = UsbReader.read_one(reader)
            elif tag == 'version':
                obj.version = TemplateVersionReader.read_one(reader)
            elif tag == 'virtio_scsi':
                obj.virtio_scsi = VirtioScsiReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'watchdogs':
                obj.watchdogs = WatchdogReader.read_many(reader)
            elif tag == 'link':
                InstanceTypeReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(InstanceTypeReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "cdroms":
                obj.cdroms = list
            elif rel == "disks":
                obj.disks = list
            elif rel == "graphicsconsoles":
                obj.graphics_consoles = list
            elif rel == "nics":
                obj.nics = list
            elif rel == "permissions":
                obj.permissions = list
            elif rel == "tags":
                obj.tags = list
            elif rel == "watchdogs":
                obj.watchdogs = list
        reader.next_element()


class IoReader(Reader):

    def __init__(self):
        super(IoReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Io()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'threads':
                obj.threads = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(IoReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class IpReader(Reader):

    def __init__(self):
        super(IpReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Ip()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'gateway':
                obj.gateway = Reader.read_string(reader)
            elif tag == 'netmask':
                obj.netmask = Reader.read_string(reader)
            elif tag == 'version':
                obj.version = types.IpVersion(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(IpReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class IpAddressAssignmentReader(Reader):

    def __init__(self):
        super(IpAddressAssignmentReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.IpAddressAssignment()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'assignment_method':
                obj.assignment_method = types.BootProtocol(Reader.read_string(reader).lower())
            elif tag == 'ip':
                obj.ip = IpReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(IpAddressAssignmentReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class IscsiBondReader(Reader):

    def __init__(self):
        super(IscsiBondReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.IscsiBond()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'data_center':
                obj.data_center = DataCenterReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'networks':
                obj.networks = NetworkReader.read_many(reader)
            elif tag == 'storage_connections':
                obj.storage_connections = StorageConnectionReader.read_many(reader)
            elif tag == 'link':
                IscsiBondReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(IscsiBondReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "networks":
                obj.networks = list
            elif rel == "storageconnections":
                obj.storage_connections = list
        reader.next_element()


class IscsiDetailsReader(Reader):

    def __init__(self):
        super(IscsiDetailsReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.IscsiDetails()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'disk_id':
                obj.disk_id = Reader.read_string(reader)
            elif tag == 'initiator':
                obj.initiator = Reader.read_string(reader)
            elif tag == 'lun_mapping':
                obj.lun_mapping = Reader.read_integer(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'paths':
                obj.paths = Reader.read_integer(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'portal':
                obj.portal = Reader.read_string(reader)
            elif tag == 'product_id':
                obj.product_id = Reader.read_string(reader)
            elif tag == 'serial':
                obj.serial = Reader.read_string(reader)
            elif tag == 'size':
                obj.size = Reader.read_integer(reader)
            elif tag == 'status':
                obj.status = Reader.read_string(reader)
            elif tag == 'storage_domain_id':
                obj.storage_domain_id = Reader.read_string(reader)
            elif tag == 'target':
                obj.target = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            elif tag == 'vendor_id':
                obj.vendor_id = Reader.read_string(reader)
            elif tag == 'volume_group_id':
                obj.volume_group_id = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(IscsiDetailsReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class JobReader(Reader):

    def __init__(self):
        super(JobReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Job()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'auto_cleared':
                obj.auto_cleared = Reader.read_boolean(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'end_time':
                obj.end_time = Reader.read_date(reader)
            elif tag == 'external':
                obj.external = Reader.read_boolean(reader)
            elif tag == 'last_updated':
                obj.last_updated = Reader.read_date(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'owner':
                obj.owner = UserReader.read_one(reader)
            elif tag == 'start_time':
                obj.start_time = Reader.read_date(reader)
            elif tag == 'status':
                obj.status = types.JobStatus(Reader.read_string(reader).lower())
            elif tag == 'steps':
                obj.steps = StepReader.read_many(reader)
            elif tag == 'link':
                JobReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(JobReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "steps":
                obj.steps = list
        reader.next_element()


class KatelloErratumReader(Reader):

    def __init__(self):
        super(KatelloErratumReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.KatelloErratum()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'issued':
                obj.issued = Reader.read_date(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'packages':
                obj.packages = PackageReader.read_many(reader)
            elif tag == 'severity':
                obj.severity = Reader.read_string(reader)
            elif tag == 'solution':
                obj.solution = Reader.read_string(reader)
            elif tag == 'summary':
                obj.summary = Reader.read_string(reader)
            elif tag == 'title':
                obj.title = Reader.read_string(reader)
            elif tag == 'type':
                obj.type = Reader.read_string(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(KatelloErratumReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class KernelReader(Reader):

    def __init__(self):
        super(KernelReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Kernel()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'version':
                obj.version = VersionReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(KernelReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class KsmReader(Reader):

    def __init__(self):
        super(KsmReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Ksm()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            elif tag == 'merge_across_nodes':
                obj.merge_across_nodes = Reader.read_boolean(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(KsmReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class LogicalUnitReader(Reader):

    def __init__(self):
        super(LogicalUnitReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.LogicalUnit()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'disk_id':
                obj.disk_id = Reader.read_string(reader)
            elif tag == 'lun_mapping':
                obj.lun_mapping = Reader.read_integer(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'paths':
                obj.paths = Reader.read_integer(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'portal':
                obj.portal = Reader.read_string(reader)
            elif tag == 'product_id':
                obj.product_id = Reader.read_string(reader)
            elif tag == 'serial':
                obj.serial = Reader.read_string(reader)
            elif tag == 'size':
                obj.size = Reader.read_integer(reader)
            elif tag == 'status':
                obj.status = types.LunStatus(Reader.read_string(reader).lower())
            elif tag == 'storage_domain_id':
                obj.storage_domain_id = Reader.read_string(reader)
            elif tag == 'target':
                obj.target = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            elif tag == 'vendor_id':
                obj.vendor_id = Reader.read_string(reader)
            elif tag == 'volume_group_id':
                obj.volume_group_id = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(LogicalUnitReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class MacReader(Reader):

    def __init__(self):
        super(MacReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Mac()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(MacReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class MacPoolReader(Reader):

    def __init__(self):
        super(MacPoolReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.MacPool()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'allow_duplicates':
                obj.allow_duplicates = Reader.read_boolean(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'default_pool':
                obj.default_pool = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'ranges':
                obj.ranges = RangeReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(MacPoolReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class MemoryOverCommitReader(Reader):

    def __init__(self):
        super(MemoryOverCommitReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.MemoryOverCommit()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'percent':
                obj.percent = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(MemoryOverCommitReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class MemoryPolicyReader(Reader):

    def __init__(self):
        super(MemoryPolicyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.MemoryPolicy()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'ballooning':
                obj.ballooning = Reader.read_boolean(reader)
            elif tag == 'guaranteed':
                obj.guaranteed = Reader.read_integer(reader)
            elif tag == 'over_commit':
                obj.over_commit = MemoryOverCommitReader.read_one(reader)
            elif tag == 'transparent_hugepages':
                obj.transparent_huge_pages = TransparentHugePagesReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(MemoryPolicyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class MethodReader(Reader):

    def __init__(self):
        super(MethodReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Method()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = types.SsoMethod(value.lower())

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(MethodReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class MigrationBandwidthReader(Reader):

    def __init__(self):
        super(MigrationBandwidthReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.MigrationBandwidth()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'assignment_method':
                obj.assignment_method = types.MigrationBandwidthAssignmentMethod(Reader.read_string(reader).lower())
            elif tag == 'custom_value':
                obj.custom_value = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(MigrationBandwidthReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class MigrationOptionsReader(Reader):

    def __init__(self):
        super(MigrationOptionsReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.MigrationOptions()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'auto_converge':
                obj.auto_converge = types.InheritableBoolean(Reader.read_string(reader).lower())
            elif tag == 'bandwidth':
                obj.bandwidth = MigrationBandwidthReader.read_one(reader)
            elif tag == 'compressed':
                obj.compressed = types.InheritableBoolean(Reader.read_string(reader).lower())
            elif tag == 'policy':
                obj.policy = MigrationPolicyReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(MigrationOptionsReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class MigrationPolicyReader(Reader):

    def __init__(self):
        super(MigrationPolicyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.MigrationPolicy()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(MigrationPolicyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class NetworkReader(Reader):

    def __init__(self):
        super(NetworkReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Network()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'data_center':
                obj.data_center = DataCenterReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'display':
                obj.display = Reader.read_boolean(reader)
            elif tag == 'ip':
                obj.ip = IpReader.read_one(reader)
            elif tag == 'mtu':
                obj.mtu = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'network_labels':
                obj.network_labels = NetworkLabelReader.read_many(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'profile_required':
                obj.profile_required = Reader.read_boolean(reader)
            elif tag == 'qos':
                obj.qos = QosReader.read_one(reader)
            elif tag == 'required':
                obj.required = Reader.read_boolean(reader)
            elif tag == 'status':
                obj.status = types.NetworkStatus(Reader.read_string(reader).lower())
            elif tag == 'stp':
                obj.stp = Reader.read_boolean(reader)
            elif tag == 'usages':
                reader.next_element()
            elif tag == 'vlan':
                obj.vlan = VlanReader.read_one(reader)
            elif tag == 'vnic_profiles':
                obj.vnic_profiles = VnicProfileReader.read_many(reader)
            elif tag == 'link':
                NetworkReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(NetworkReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "networklabels":
                obj.network_labels = list
            elif rel == "permissions":
                obj.permissions = list
            elif rel == "vnicprofiles":
                obj.vnic_profiles = list
        reader.next_element()


class NetworkAttachmentReader(Reader):

    def __init__(self):
        super(NetworkAttachmentReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.NetworkAttachment()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'host_nic':
                obj.host_nic = HostNicReader.read_one(reader)
            elif tag == 'in_sync':
                obj.in_sync = Reader.read_boolean(reader)
            elif tag == 'ip_address_assignments':
                obj.ip_address_assignments = IpAddressAssignmentReader.read_many(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'network':
                obj.network = NetworkReader.read_one(reader)
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            elif tag == 'qos':
                obj.qos = QosReader.read_one(reader)
            elif tag == 'reported_configurations':
                obj.reported_configurations = ReportedConfigurationReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(NetworkAttachmentReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class NetworkConfigurationReader(Reader):

    def __init__(self):
        super(NetworkConfigurationReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.NetworkConfiguration()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'dns':
                obj.dns = DnsReader.read_one(reader)
            elif tag == 'nics':
                obj.nics = NicReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(NetworkConfigurationReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class NetworkFilterReader(Reader):

    def __init__(self):
        super(NetworkFilterReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.NetworkFilter()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'version':
                obj.version = VersionReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(NetworkFilterReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class NetworkLabelReader(Reader):

    def __init__(self):
        super(NetworkLabelReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.NetworkLabel()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host_nic':
                obj.host_nic = HostNicReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'network':
                obj.network = NetworkReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(NetworkLabelReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class NfsProfileDetailReader(Reader):

    def __init__(self):
        super(NfsProfileDetailReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.NfsProfileDetail()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'nfs_server_ip':
                obj.nfs_server_ip = Reader.read_string(reader)
            elif tag == 'profile_details':
                obj.profile_details = ProfileDetailReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(NfsProfileDetailReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class NicReader(Reader):

    def __init__(self):
        super(NicReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Nic()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'boot_protocol':
                obj.boot_protocol = types.BootProtocol(Reader.read_string(reader).lower())
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'interface':
                obj.interface = types.NicInterface(Reader.read_string(reader).lower())
            elif tag == 'linked':
                obj.linked = Reader.read_boolean(reader)
            elif tag == 'mac':
                obj.mac = MacReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'network':
                obj.network = NetworkReader.read_one(reader)
            elif tag == 'network_attachments':
                obj.network_attachments = NetworkAttachmentReader.read_many(reader)
            elif tag == 'network_labels':
                obj.network_labels = NetworkLabelReader.read_many(reader)
            elif tag == 'on_boot':
                obj.on_boot = Reader.read_boolean(reader)
            elif tag == 'plugged':
                obj.plugged = Reader.read_boolean(reader)
            elif tag == 'reported_devices':
                obj.reported_devices = ReportedDeviceReader.read_many(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'virtual_function_allowed_labels':
                obj.virtual_function_allowed_labels = NetworkLabelReader.read_many(reader)
            elif tag == 'virtual_function_allowed_networks':
                obj.virtual_function_allowed_networks = NetworkReader.read_many(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'vnic_profile':
                obj.vnic_profile = VnicProfileReader.read_one(reader)
            elif tag == 'link':
                NicReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(NicReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "networkattachments":
                obj.network_attachments = list
            elif rel == "networklabels":
                obj.network_labels = list
            elif rel == "reporteddevices":
                obj.reported_devices = list
            elif rel == "statistics":
                obj.statistics = list
            elif rel == "virtualfunctionallowedlabels":
                obj.virtual_function_allowed_labels = list
            elif rel == "virtualfunctionallowednetworks":
                obj.virtual_function_allowed_networks = list
            elif rel == "vms":
                obj.vms = list
        reader.next_element()


class NicConfigurationReader(Reader):

    def __init__(self):
        super(NicConfigurationReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.NicConfiguration()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'boot_protocol':
                obj.boot_protocol = types.BootProtocol(Reader.read_string(reader).lower())
            elif tag == 'ip':
                obj.ip = IpReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'on_boot':
                obj.on_boot = Reader.read_boolean(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(NicConfigurationReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class NumaNodeReader(Reader):

    def __init__(self):
        super(NumaNodeReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.NumaNode()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'cpu':
                obj.cpu = CpuReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'index':
                obj.index = Reader.read_integer(reader)
            elif tag == 'memory':
                obj.memory = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'node_distance':
                obj.node_distance = Reader.read_string(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'link':
                NumaNodeReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(NumaNodeReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "statistics":
                obj.statistics = list
        reader.next_element()


class NumaNodePinReader(Reader):

    def __init__(self):
        super(NumaNodePinReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.NumaNodePin()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'host_numa_node':
                obj.host_numa_node = NumaNodeReader.read_one(reader)
            elif tag == 'index':
                obj.index = Reader.read_integer(reader)
            elif tag == 'pinned':
                obj.pinned = Reader.read_boolean(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(NumaNodePinReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class OpenStackImageReader(Reader):

    def __init__(self):
        super(OpenStackImageReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OpenStackImage()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'openstack_image_provider':
                obj.openstack_image_provider = OpenStackImageProviderReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OpenStackImageReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class OpenStackImageProviderReader(Reader):

    def __init__(self):
        super(OpenStackImageProviderReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OpenStackImageProvider()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'authentication_url':
                obj.authentication_url = Reader.read_string(reader)
            elif tag == 'certificates':
                obj.certificates = CertificateReader.read_many(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'images':
                obj.images = OpenStackImageReader.read_many(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            elif tag == 'requires_authentication':
                obj.requires_authentication = Reader.read_boolean(reader)
            elif tag == 'tenant_name':
                obj.tenant_name = Reader.read_string(reader)
            elif tag == 'url':
                obj.url = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            elif tag == 'link':
                OpenStackImageProviderReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OpenStackImageProviderReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "certificates":
                obj.certificates = list
            elif rel == "images":
                obj.images = list
        reader.next_element()


class OpenStackNetworkReader(Reader):

    def __init__(self):
        super(OpenStackNetworkReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OpenStackNetwork()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'openstack_network_provider':
                obj.openstack_network_provider = OpenStackNetworkProviderReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OpenStackNetworkReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class OpenStackNetworkProviderReader(Reader):

    def __init__(self):
        super(OpenStackNetworkProviderReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OpenStackNetworkProvider()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'agent_configuration':
                obj.agent_configuration = AgentConfigurationReader.read_one(reader)
            elif tag == 'authentication_url':
                obj.authentication_url = Reader.read_string(reader)
            elif tag == 'certificates':
                obj.certificates = CertificateReader.read_many(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'networks':
                obj.networks = OpenStackNetworkReader.read_many(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'plugin_type':
                obj.plugin_type = types.NetworkPluginType(Reader.read_string(reader).lower())
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            elif tag == 'read_only':
                obj.read_only = Reader.read_boolean(reader)
            elif tag == 'requires_authentication':
                obj.requires_authentication = Reader.read_boolean(reader)
            elif tag == 'subnets':
                obj.subnets = OpenStackSubnetReader.read_many(reader)
            elif tag == 'tenant_name':
                obj.tenant_name = Reader.read_string(reader)
            elif tag == 'type':
                obj.type = types.OpenStackNetworkProviderType(Reader.read_string(reader).lower())
            elif tag == 'url':
                obj.url = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            elif tag == 'link':
                OpenStackNetworkProviderReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OpenStackNetworkProviderReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "certificates":
                obj.certificates = list
            elif rel == "networks":
                obj.networks = list
            elif rel == "subnets":
                obj.subnets = list
        reader.next_element()


class OpenStackProviderReader(Reader):

    def __init__(self):
        super(OpenStackProviderReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OpenStackProvider()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'authentication_url':
                obj.authentication_url = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            elif tag == 'requires_authentication':
                obj.requires_authentication = Reader.read_boolean(reader)
            elif tag == 'tenant_name':
                obj.tenant_name = Reader.read_string(reader)
            elif tag == 'url':
                obj.url = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OpenStackProviderReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class OpenStackSubnetReader(Reader):

    def __init__(self):
        super(OpenStackSubnetReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OpenStackSubnet()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cidr':
                obj.cidr = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'dns_servers':
                reader.next_element()
            elif tag == 'gateway':
                obj.gateway = Reader.read_string(reader)
            elif tag == 'ip_version':
                obj.ip_version = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'openstack_network':
                obj.openstack_network = OpenStackNetworkReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OpenStackSubnetReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class OpenStackVolumeProviderReader(Reader):

    def __init__(self):
        super(OpenStackVolumeProviderReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OpenStackVolumeProvider()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'authentication_keys':
                obj.authentication_keys = OpenstackVolumeAuthenticationKeyReader.read_many(reader)
            elif tag == 'authentication_url':
                obj.authentication_url = Reader.read_string(reader)
            elif tag == 'certificates':
                obj.certificates = CertificateReader.read_many(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'data_center':
                obj.data_center = DataCenterReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            elif tag == 'requires_authentication':
                obj.requires_authentication = Reader.read_boolean(reader)
            elif tag == 'tenant_name':
                obj.tenant_name = Reader.read_string(reader)
            elif tag == 'url':
                obj.url = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            elif tag == 'volume_types':
                obj.volume_types = OpenStackVolumeTypeReader.read_many(reader)
            elif tag == 'link':
                OpenStackVolumeProviderReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OpenStackVolumeProviderReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "authenticationkeys":
                obj.authentication_keys = list
            elif rel == "certificates":
                obj.certificates = list
            elif rel == "volumetypes":
                obj.volume_types = list
        reader.next_element()


class OpenStackVolumeTypeReader(Reader):

    def __init__(self):
        super(OpenStackVolumeTypeReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OpenStackVolumeType()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'openstack_volume_provider':
                obj.openstack_volume_provider = OpenStackVolumeProviderReader.read_one(reader)
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OpenStackVolumeTypeReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class OpenstackVolumeAuthenticationKeyReader(Reader):

    def __init__(self):
        super(OpenstackVolumeAuthenticationKeyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OpenstackVolumeAuthenticationKey()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'creation_date':
                obj.creation_date = Reader.read_date(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'openstack_volume_provider':
                obj.openstack_volume_provider = OpenStackVolumeProviderReader.read_one(reader)
            elif tag == 'usage_type':
                obj.usage_type = types.OpenstackVolumeAuthenticationKeyUsageType(Reader.read_string(reader).lower())
            elif tag == 'uuid':
                obj.uuid = Reader.read_string(reader)
            elif tag == 'value':
                obj.value = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OpenstackVolumeAuthenticationKeyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class OperatingSystemReader(Reader):

    def __init__(self):
        super(OperatingSystemReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OperatingSystem()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'boot':
                obj.boot = BootReader.read_one(reader)
            elif tag == 'cmdline':
                obj.cmdline = Reader.read_string(reader)
            elif tag == 'custom_kernel_cmdline':
                obj.custom_kernel_cmdline = Reader.read_string(reader)
            elif tag == 'initrd':
                obj.initrd = Reader.read_string(reader)
            elif tag == 'kernel':
                obj.kernel = Reader.read_string(reader)
            elif tag == 'reported_kernel_cmdline':
                obj.reported_kernel_cmdline = Reader.read_string(reader)
            elif tag == 'type':
                obj.type = Reader.read_string(reader)
            elif tag == 'version':
                obj.version = VersionReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OperatingSystemReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class OperatingSystemInfoReader(Reader):

    def __init__(self):
        super(OperatingSystemInfoReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.OperatingSystemInfo()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'large_icon':
                obj.large_icon = IconReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'small_icon':
                obj.small_icon = IconReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OperatingSystemInfoReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class OptionReader(Reader):

    def __init__(self):
        super(OptionReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Option()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'type':
                obj.type = Reader.read_string(reader)
            elif tag == 'value':
                obj.value = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(OptionReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class PackageReader(Reader):

    def __init__(self):
        super(PackageReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Package()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(PackageReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class PayloadReader(Reader):

    def __init__(self):
        super(PayloadReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Payload()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'files':
                obj.files = FileReader.read_many(reader)
            elif tag == 'type':
                obj.type = types.VmDeviceType(Reader.read_string(reader).lower())
            elif tag == 'volume_id':
                obj.volume_id = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(PayloadReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class PermissionReader(Reader):

    def __init__(self):
        super(PermissionReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Permission()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'data_center':
                obj.data_center = DataCenterReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disk':
                obj.disk = DiskReader.read_one(reader)
            elif tag == 'group':
                obj.group = GroupReader.read_one(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'role':
                obj.role = RoleReader.read_one(reader)
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'user':
                obj.user = UserReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vm_pool':
                obj.vm_pool = VmPoolReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(PermissionReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class PermitReader(Reader):

    def __init__(self):
        super(PermitReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Permit()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'administrative':
                obj.administrative = Reader.read_boolean(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'role':
                obj.role = RoleReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(PermitReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class PmProxyReader(Reader):

    def __init__(self):
        super(PmProxyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.PmProxy()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'type':
                obj.type = types.PmProxyType(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(PmProxyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class PortMirroringReader(Reader):

    def __init__(self):
        super(PortMirroringReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.PortMirroring()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(PortMirroringReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class PowerManagementReader(Reader):

    def __init__(self):
        super(PowerManagementReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.PowerManagement()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'agents':
                obj.agents = AgentReader.read_many(reader)
            elif tag == 'automatic_pm_enabled':
                obj.automatic_pm_enabled = Reader.read_boolean(reader)
            elif tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            elif tag == 'kdump_detection':
                obj.kdump_detection = Reader.read_boolean(reader)
            elif tag == 'options':
                obj.options = OptionReader.read_many(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'pm_proxies':
                obj.pm_proxies = PmProxyReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.PowerManagementStatus(Reader.read_string(reader).lower())
            elif tag == 'type':
                obj.type = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(PowerManagementReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ProductReader(Reader):

    def __init__(self):
        super(ProductReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Product()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ProductReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ProductInfoReader(Reader):

    def __init__(self):
        super(ProductInfoReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ProductInfo()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'vendor':
                obj.vendor = Reader.read_string(reader)
            elif tag == 'version':
                obj.version = VersionReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ProductInfoReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ProfileDetailReader(Reader):

    def __init__(self):
        super(ProfileDetailReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ProfileDetail()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'block_statistics':
                obj.block_statistics = BlockStatisticReader.read_many(reader)
            elif tag == 'duration':
                obj.duration = Reader.read_integer(reader)
            elif tag == 'fop_statistics':
                obj.fop_statistics = FopStatisticReader.read_many(reader)
            elif tag == 'profile_type':
                obj.profile_type = Reader.read_string(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ProfileDetailReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class PropertyReader(Reader):

    def __init__(self):
        super(PropertyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Property()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'value':
                obj.value = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(PropertyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ProxyTicketReader(Reader):

    def __init__(self):
        super(ProxyTicketReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ProxyTicket()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'value':
                obj.value = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ProxyTicketReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class QosReader(Reader):

    def __init__(self):
        super(QosReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Qos()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'cpu_limit':
                obj.cpu_limit = Reader.read_integer(reader)
            elif tag == 'data_center':
                obj.data_center = DataCenterReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'inbound_average':
                obj.inbound_average = Reader.read_integer(reader)
            elif tag == 'inbound_burst':
                obj.inbound_burst = Reader.read_integer(reader)
            elif tag == 'inbound_peak':
                obj.inbound_peak = Reader.read_integer(reader)
            elif tag == 'max_iops':
                obj.max_iops = Reader.read_integer(reader)
            elif tag == 'max_read_iops':
                obj.max_read_iops = Reader.read_integer(reader)
            elif tag == 'max_read_throughput':
                obj.max_read_throughput = Reader.read_integer(reader)
            elif tag == 'max_throughput':
                obj.max_throughput = Reader.read_integer(reader)
            elif tag == 'max_write_iops':
                obj.max_write_iops = Reader.read_integer(reader)
            elif tag == 'max_write_throughput':
                obj.max_write_throughput = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'outbound_average':
                obj.outbound_average = Reader.read_integer(reader)
            elif tag == 'outbound_average_linkshare':
                obj.outbound_average_linkshare = Reader.read_integer(reader)
            elif tag == 'outbound_average_realtime':
                obj.outbound_average_realtime = Reader.read_integer(reader)
            elif tag == 'outbound_average_upperlimit':
                obj.outbound_average_upperlimit = Reader.read_integer(reader)
            elif tag == 'outbound_burst':
                obj.outbound_burst = Reader.read_integer(reader)
            elif tag == 'outbound_peak':
                obj.outbound_peak = Reader.read_integer(reader)
            elif tag == 'type':
                obj.type = types.QosType(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(QosReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class QuotaReader(Reader):

    def __init__(self):
        super(QuotaReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Quota()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cluster_hard_limit_pct':
                obj.cluster_hard_limit_pct = Reader.read_integer(reader)
            elif tag == 'cluster_soft_limit_pct':
                obj.cluster_soft_limit_pct = Reader.read_integer(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'data_center':
                obj.data_center = DataCenterReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disks':
                obj.disks = DiskReader.read_many(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'quota_cluster_limits':
                obj.quota_cluster_limits = QuotaClusterLimitReader.read_many(reader)
            elif tag == 'quota_storage_limits':
                obj.quota_storage_limits = QuotaStorageLimitReader.read_many(reader)
            elif tag == 'storage_hard_limit_pct':
                obj.storage_hard_limit_pct = Reader.read_integer(reader)
            elif tag == 'storage_soft_limit_pct':
                obj.storage_soft_limit_pct = Reader.read_integer(reader)
            elif tag == 'users':
                obj.users = UserReader.read_many(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'link':
                QuotaReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(QuotaReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "permissions":
                obj.permissions = list
            elif rel == "quotaclusterlimits":
                obj.quota_cluster_limits = list
            elif rel == "quotastoragelimits":
                obj.quota_storage_limits = list
        reader.next_element()


class QuotaClusterLimitReader(Reader):

    def __init__(self):
        super(QuotaClusterLimitReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.QuotaClusterLimit()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'memory_limit':
                obj.memory_limit = Reader.read_decimal(reader)
            elif tag == 'memory_usage':
                obj.memory_usage = Reader.read_decimal(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'quota':
                obj.quota = QuotaReader.read_one(reader)
            elif tag == 'vcpu_limit':
                obj.vcpu_limit = Reader.read_integer(reader)
            elif tag == 'vcpu_usage':
                obj.vcpu_usage = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(QuotaClusterLimitReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class QuotaStorageLimitReader(Reader):

    def __init__(self):
        super(QuotaStorageLimitReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.QuotaStorageLimit()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'limit':
                obj.limit = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'quota':
                obj.quota = QuotaReader.read_one(reader)
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'usage':
                obj.usage = Reader.read_decimal(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(QuotaStorageLimitReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class RangeReader(Reader):

    def __init__(self):
        super(RangeReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Range()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'from':
                obj.from_ = Reader.read_string(reader)
            elif tag == 'to':
                obj.to = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(RangeReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class RateReader(Reader):

    def __init__(self):
        super(RateReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Rate()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'bytes':
                obj.bytes = Reader.read_integer(reader)
            elif tag == 'period':
                obj.period = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(RateReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ReportedConfigurationReader(Reader):

    def __init__(self):
        super(ReportedConfigurationReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ReportedConfiguration()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'actual_value':
                obj.actual_value = Reader.read_string(reader)
            elif tag == 'expected_value':
                obj.expected_value = Reader.read_string(reader)
            elif tag == 'in_sync':
                obj.in_sync = Reader.read_boolean(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ReportedConfigurationReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class ReportedDeviceReader(Reader):

    def __init__(self):
        super(ReportedDeviceReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.ReportedDevice()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'ips':
                obj.ips = IpReader.read_many(reader)
            elif tag == 'mac':
                obj.mac = MacReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'type':
                obj.type = types.ReportedDeviceType(Reader.read_string(reader).lower())
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ReportedDeviceReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class RngDeviceReader(Reader):

    def __init__(self):
        super(RngDeviceReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.RngDevice()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'rate':
                obj.rate = RateReader.read_one(reader)
            elif tag == 'source':
                obj.source = types.RngSource(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(RngDeviceReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class RoleReader(Reader):

    def __init__(self):
        super(RoleReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Role()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'administrative':
                obj.administrative = Reader.read_boolean(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'mutable':
                obj.mutable = Reader.read_boolean(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'permits':
                obj.permits = PermitReader.read_many(reader)
            elif tag == 'user':
                obj.user = UserReader.read_one(reader)
            elif tag == 'link':
                RoleReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(RoleReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "permits":
                obj.permits = list
        reader.next_element()


class SchedulingPolicyReader(Reader):

    def __init__(self):
        super(SchedulingPolicyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.SchedulingPolicy()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'balances':
                obj.balances = BalanceReader.read_many(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'default_policy':
                obj.default_policy = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'filters':
                obj.filters = FilterReader.read_many(reader)
            elif tag == 'locked':
                obj.locked = Reader.read_boolean(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            elif tag == 'weight':
                obj.weight = WeightReader.read_many(reader)
            elif tag == 'link':
                SchedulingPolicyReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SchedulingPolicyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "balances":
                obj.balances = list
            elif rel == "filters":
                obj.filters = list
            elif rel == "weight":
                obj.weight = list
        reader.next_element()


class SchedulingPolicyUnitReader(Reader):

    def __init__(self):
        super(SchedulingPolicyUnitReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.SchedulingPolicyUnit()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            elif tag == 'internal':
                obj.internal = Reader.read_boolean(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'properties':
                obj.properties = PropertyReader.read_many(reader)
            elif tag == 'type':
                obj.type = types.PolicyUnitType(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SchedulingPolicyUnitReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class SeLinuxReader(Reader):

    def __init__(self):
        super(SeLinuxReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.SeLinux()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'mode':
                obj.mode = types.SeLinuxMode(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SeLinuxReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class SerialNumberReader(Reader):

    def __init__(self):
        super(SerialNumberReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.SerialNumber()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'policy':
                obj.policy = types.SerialNumberPolicy(Reader.read_string(reader).lower())
            elif tag == 'value':
                obj.value = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SerialNumberReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class SessionReader(Reader):

    def __init__(self):
        super(SessionReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Session()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'console_user':
                obj.console_user = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'ip':
                obj.ip = IpReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'protocol':
                obj.protocol = Reader.read_string(reader)
            elif tag == 'user':
                obj.user = UserReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SessionReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class SkipIfConnectivityBrokenReader(Reader):

    def __init__(self):
        super(SkipIfConnectivityBrokenReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.SkipIfConnectivityBroken()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            elif tag == 'threshold':
                obj.threshold = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SkipIfConnectivityBrokenReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class SkipIfSdActiveReader(Reader):

    def __init__(self):
        super(SkipIfSdActiveReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.SkipIfSdActive()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SkipIfSdActiveReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class SnapshotReader(Reader):

    def __init__(self):
        super(SnapshotReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Snapshot()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'affinity_labels':
                obj.affinity_labels = AffinityLabelReader.read_many(reader)
            elif tag == 'applications':
                obj.applications = ApplicationReader.read_many(reader)
            elif tag == 'bios':
                obj.bios = BiosReader.read_one(reader)
            elif tag == 'cdroms':
                obj.cdroms = CdromReader.read_many(reader)
            elif tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'console':
                obj.console = ConsoleReader.read_one(reader)
            elif tag == 'cpu':
                obj.cpu = CpuReader.read_one(reader)
            elif tag == 'cpu_profile':
                obj.cpu_profile = CpuProfileReader.read_one(reader)
            elif tag == 'cpu_shares':
                obj.cpu_shares = Reader.read_integer(reader)
            elif tag == 'creation_time':
                obj.creation_time = Reader.read_date(reader)
            elif tag == 'custom_compatibility_version':
                obj.custom_compatibility_version = VersionReader.read_one(reader)
            elif tag == 'custom_cpu_model':
                obj.custom_cpu_model = Reader.read_string(reader)
            elif tag == 'custom_emulated_machine':
                obj.custom_emulated_machine = Reader.read_string(reader)
            elif tag == 'custom_properties':
                obj.custom_properties = CustomPropertyReader.read_many(reader)
            elif tag == 'date':
                obj.date = Reader.read_date(reader)
            elif tag == 'delete_protected':
                obj.delete_protected = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disk_attachments':
                obj.disk_attachments = DiskAttachmentReader.read_many(reader)
            elif tag == 'disks':
                obj.disks = DiskReader.read_many(reader)
            elif tag == 'display':
                obj.display = DisplayReader.read_one(reader)
            elif tag == 'domain':
                obj.domain = DomainReader.read_one(reader)
            elif tag == 'external_host_provider':
                obj.external_host_provider = ExternalHostProviderReader.read_one(reader)
            elif tag == 'floppies':
                obj.floppies = FloppyReader.read_many(reader)
            elif tag == 'fqdn':
                obj.fqdn = Reader.read_string(reader)
            elif tag == 'graphics_consoles':
                obj.graphics_consoles = GraphicsConsoleReader.read_many(reader)
            elif tag == 'guest_operating_system':
                obj.guest_operating_system = GuestOperatingSystemReader.read_one(reader)
            elif tag == 'guest_time_zone':
                obj.guest_time_zone = TimeZoneReader.read_one(reader)
            elif tag == 'high_availability':
                obj.high_availability = HighAvailabilityReader.read_one(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'host_devices':
                obj.host_devices = HostDeviceReader.read_many(reader)
            elif tag == 'initialization':
                obj.initialization = InitializationReader.read_one(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'io':
                obj.io = IoReader.read_one(reader)
            elif tag == 'katello_errata':
                obj.katello_errata = KatelloErratumReader.read_many(reader)
            elif tag == 'large_icon':
                obj.large_icon = IconReader.read_one(reader)
            elif tag == 'memory':
                obj.memory = Reader.read_integer(reader)
            elif tag == 'memory_policy':
                obj.memory_policy = MemoryPolicyReader.read_one(reader)
            elif tag == 'migration':
                obj.migration = MigrationOptionsReader.read_one(reader)
            elif tag == 'migration_downtime':
                obj.migration_downtime = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'next_run_configuration_exists':
                obj.next_run_configuration_exists = Reader.read_boolean(reader)
            elif tag == 'nics':
                obj.nics = NicReader.read_many(reader)
            elif tag == 'host_numa_nodes':
                obj.numa_nodes = NumaNodeReader.read_many(reader)
            elif tag == 'numa_tune_mode':
                obj.numa_tune_mode = types.NumaTuneMode(Reader.read_string(reader).lower())
            elif tag == 'origin':
                obj.origin = Reader.read_string(reader)
            elif tag == 'os':
                obj.os = OperatingSystemReader.read_one(reader)
            elif tag == 'payloads':
                obj.payloads = PayloadReader.read_many(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'persist_memorystate':
                obj.persist_memorystate = Reader.read_boolean(reader)
            elif tag == 'placement_policy':
                obj.placement_policy = VmPlacementPolicyReader.read_one(reader)
            elif tag == 'quota':
                obj.quota = QuotaReader.read_one(reader)
            elif tag == 'reported_devices':
                obj.reported_devices = ReportedDeviceReader.read_many(reader)
            elif tag == 'rng_device':
                obj.rng_device = RngDeviceReader.read_one(reader)
            elif tag == 'run_once':
                obj.run_once = Reader.read_boolean(reader)
            elif tag == 'serial_number':
                obj.serial_number = SerialNumberReader.read_one(reader)
            elif tag == 'sessions':
                obj.sessions = SessionReader.read_many(reader)
            elif tag == 'small_icon':
                obj.small_icon = IconReader.read_one(reader)
            elif tag == 'snapshot_status':
                obj.snapshot_status = types.SnapshotStatus(Reader.read_string(reader).lower())
            elif tag == 'snapshot_type':
                obj.snapshot_type = types.SnapshotType(Reader.read_string(reader).lower())
            elif tag == 'snapshots':
                obj.snapshots = SnapshotReader.read_many(reader)
            elif tag == 'soundcard_enabled':
                obj.soundcard_enabled = Reader.read_boolean(reader)
            elif tag == 'sso':
                obj.sso = SsoReader.read_one(reader)
            elif tag == 'start_paused':
                obj.start_paused = Reader.read_boolean(reader)
            elif tag == 'start_time':
                obj.start_time = Reader.read_date(reader)
            elif tag == 'stateless':
                obj.stateless = Reader.read_boolean(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.VmStatus(Reader.read_string(reader).lower())
            elif tag == 'status_detail':
                obj.status_detail = Reader.read_string(reader)
            elif tag == 'stop_reason':
                obj.stop_reason = Reader.read_string(reader)
            elif tag == 'stop_time':
                obj.stop_time = Reader.read_date(reader)
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'tags':
                obj.tags = TagReader.read_many(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'time_zone':
                obj.time_zone = TimeZoneReader.read_one(reader)
            elif tag == 'tunnel_migration':
                obj.tunnel_migration = Reader.read_boolean(reader)
            elif tag == 'type':
                obj.type = types.VmType(Reader.read_string(reader).lower())
            elif tag == 'usb':
                obj.usb = UsbReader.read_one(reader)
            elif tag == 'use_latest_template_version':
                obj.use_latest_template_version = Reader.read_boolean(reader)
            elif tag == 'virtio_scsi':
                obj.virtio_scsi = VirtioScsiReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vm_pool':
                obj.vm_pool = VmPoolReader.read_one(reader)
            elif tag == 'watchdogs':
                obj.watchdogs = WatchdogReader.read_many(reader)
            elif tag == 'link':
                SnapshotReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SnapshotReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "affinitylabels":
                obj.affinity_labels = list
            elif rel == "applications":
                obj.applications = list
            elif rel == "cdroms":
                obj.cdroms = list
            elif rel == "diskattachments":
                obj.disk_attachments = list
            elif rel == "disks":
                obj.disks = list
            elif rel == "floppies":
                obj.floppies = list
            elif rel == "graphicsconsoles":
                obj.graphics_consoles = list
            elif rel == "hostdevices":
                obj.host_devices = list
            elif rel == "katelloerrata":
                obj.katello_errata = list
            elif rel == "nics":
                obj.nics = list
            elif rel == "numanodes":
                obj.numa_nodes = list
            elif rel == "permissions":
                obj.permissions = list
            elif rel == "reporteddevices":
                obj.reported_devices = list
            elif rel == "sessions":
                obj.sessions = list
            elif rel == "snapshots":
                obj.snapshots = list
            elif rel == "statistics":
                obj.statistics = list
            elif rel == "tags":
                obj.tags = list
            elif rel == "watchdogs":
                obj.watchdogs = list
        reader.next_element()


class SpecialObjectsReader(Reader):

    def __init__(self):
        super(SpecialObjectsReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.SpecialObjects()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'blank_template':
                obj.blank_template = TemplateReader.read_one(reader)
            elif tag == 'root_tag':
                obj.root_tag = TagReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SpecialObjectsReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class SpmReader(Reader):

    def __init__(self):
        super(SpmReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Spm()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'priority':
                obj.priority = Reader.read_integer(reader)
            elif tag == 'status':
                obj.status = types.SpmStatus(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SpmReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class SshReader(Reader):

    def __init__(self):
        super(SshReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Ssh()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'authentication_method':
                obj.authentication_method = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'fingerprint':
                obj.fingerprint = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'user':
                obj.user = UserReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SshReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class SshPublicKeyReader(Reader):

    def __init__(self):
        super(SshPublicKeyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.SshPublicKey()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'content':
                obj.content = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'user':
                obj.user = UserReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SshPublicKeyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class SsoReader(Reader):

    def __init__(self):
        super(SsoReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Sso()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'methods':
                obj.methods = MethodReader.read_many(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(SsoReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class StatisticReader(Reader):

    def __init__(self):
        super(StatisticReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Statistic()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'brick':
                obj.brick = GlusterBrickReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disk':
                obj.disk = DiskReader.read_one(reader)
            elif tag == 'gluster_volume':
                obj.gluster_volume = GlusterVolumeReader.read_one(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'host_nic':
                obj.host_nic = HostNicReader.read_one(reader)
            elif tag == 'host_numa_node':
                obj.host_numa_node = NumaNodeReader.read_one(reader)
            elif tag == 'kind':
                obj.kind = types.StatisticKind(Reader.read_string(reader).lower())
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'nic':
                obj.nic = NicReader.read_one(reader)
            elif tag == 'step':
                obj.step = StepReader.read_one(reader)
            elif tag == 'type':
                obj.type = types.ValueType(Reader.read_string(reader).lower())
            elif tag == 'unit':
                obj.unit = types.StatisticUnit(Reader.read_string(reader).lower())
            elif tag == 'values':
                obj.values = ValueReader.read_many(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(StatisticReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class StepReader(Reader):

    def __init__(self):
        super(StepReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Step()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'end_time':
                obj.end_time = Reader.read_date(reader)
            elif tag == 'external':
                obj.external = Reader.read_boolean(reader)
            elif tag == 'external_type':
                obj.external_type = types.ExternalSystemType(Reader.read_string(reader).lower())
            elif tag == 'job':
                obj.job = JobReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'number':
                obj.number = Reader.read_integer(reader)
            elif tag == 'parent_step':
                obj.parent_step = StepReader.read_one(reader)
            elif tag == 'start_time':
                obj.start_time = Reader.read_date(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.StepStatus(Reader.read_string(reader).lower())
            elif tag == 'type':
                obj.type = types.StepEnum(Reader.read_string(reader).lower())
            elif tag == 'link':
                StepReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(StepReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "statistics":
                obj.statistics = list
        reader.next_element()


class StorageConnectionReader(Reader):

    def __init__(self):
        super(StorageConnectionReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.StorageConnection()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'address':
                obj.address = Reader.read_string(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'mount_options':
                obj.mount_options = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'nfs_retrans':
                obj.nfs_retrans = Reader.read_integer(reader)
            elif tag == 'nfs_timeo':
                obj.nfs_timeo = Reader.read_integer(reader)
            elif tag == 'nfs_version':
                obj.nfs_version = types.NfsVersion(Reader.read_string(reader).lower())
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'path':
                obj.path = Reader.read_string(reader)
            elif tag == 'port':
                obj.port = Reader.read_integer(reader)
            elif tag == 'portal':
                obj.portal = Reader.read_string(reader)
            elif tag == 'target':
                obj.target = Reader.read_string(reader)
            elif tag == 'type':
                obj.type = types.StorageType(Reader.read_string(reader).lower())
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            elif tag == 'vfs_type':
                obj.vfs_type = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(StorageConnectionReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class StorageConnectionExtensionReader(Reader):

    def __init__(self):
        super(StorageConnectionExtensionReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.StorageConnectionExtension()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'target':
                obj.target = Reader.read_string(reader)
            elif tag == 'username':
                obj.username = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(StorageConnectionExtensionReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class StorageDomainReader(Reader):

    def __init__(self):
        super(StorageDomainReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.StorageDomain()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'available':
                obj.available = Reader.read_integer(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'committed':
                obj.committed = Reader.read_integer(reader)
            elif tag == 'critical_space_action_blocker':
                obj.critical_space_action_blocker = Reader.read_integer(reader)
            elif tag == 'data_center':
                obj.data_center = DataCenterReader.read_one(reader)
            elif tag == 'data_centers':
                obj.data_centers = DataCenterReader.read_many(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disk_profiles':
                obj.disk_profiles = DiskProfileReader.read_many(reader)
            elif tag == 'disk_snapshots':
                obj.disk_snapshots = DiskSnapshotReader.read_many(reader)
            elif tag == 'disks':
                obj.disks = DiskReader.read_many(reader)
            elif tag == 'external_status':
                obj.external_status = types.ExternalStatus(Reader.read_string(reader).lower())
            elif tag == 'files':
                obj.files = FileReader.read_many(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'images':
                obj.images = ImageReader.read_many(reader)
            elif tag == 'import':
                obj.import_ = Reader.read_boolean(reader)
            elif tag == 'master':
                obj.master = Reader.read_boolean(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.StorageDomainStatus(Reader.read_string(reader).lower())
            elif tag == 'storage':
                obj.storage = HostStorageReader.read_one(reader)
            elif tag == 'storage_connections':
                obj.storage_connections = StorageConnectionReader.read_many(reader)
            elif tag == 'storage_format':
                obj.storage_format = types.StorageFormat(Reader.read_string(reader).lower())
            elif tag == 'templates':
                obj.templates = TemplateReader.read_many(reader)
            elif tag == 'type':
                obj.type = types.StorageDomainType(Reader.read_string(reader).lower())
            elif tag == 'used':
                obj.used = Reader.read_integer(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'warning_low_space_indicator':
                obj.warning_low_space_indicator = Reader.read_integer(reader)
            elif tag == 'wipe_after_delete':
                obj.wipe_after_delete = Reader.read_boolean(reader)
            elif tag == 'link':
                StorageDomainReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(StorageDomainReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "datacenters":
                obj.data_centers = list
            elif rel == "diskprofiles":
                obj.disk_profiles = list
            elif rel == "disksnapshots":
                obj.disk_snapshots = list
            elif rel == "disks":
                obj.disks = list
            elif rel == "files":
                obj.files = list
            elif rel == "images":
                obj.images = list
            elif rel == "permissions":
                obj.permissions = list
            elif rel == "storageconnections":
                obj.storage_connections = list
            elif rel == "templates":
                obj.templates = list
            elif rel == "vms":
                obj.vms = list
        reader.next_element()


class TagReader(Reader):

    def __init__(self):
        super(TagReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Tag()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'group':
                obj.group = GroupReader.read_one(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'parent':
                obj.parent = TagReader.read_one(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'user':
                obj.user = UserReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(TagReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class TemplateReader(Reader):

    def __init__(self):
        super(TemplateReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Template()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'bios':
                obj.bios = BiosReader.read_one(reader)
            elif tag == 'cdroms':
                obj.cdroms = CdromReader.read_many(reader)
            elif tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'console':
                obj.console = ConsoleReader.read_one(reader)
            elif tag == 'cpu':
                obj.cpu = CpuReader.read_one(reader)
            elif tag == 'cpu_profile':
                obj.cpu_profile = CpuProfileReader.read_one(reader)
            elif tag == 'cpu_shares':
                obj.cpu_shares = Reader.read_integer(reader)
            elif tag == 'creation_time':
                obj.creation_time = Reader.read_date(reader)
            elif tag == 'custom_compatibility_version':
                obj.custom_compatibility_version = VersionReader.read_one(reader)
            elif tag == 'custom_cpu_model':
                obj.custom_cpu_model = Reader.read_string(reader)
            elif tag == 'custom_emulated_machine':
                obj.custom_emulated_machine = Reader.read_string(reader)
            elif tag == 'custom_properties':
                obj.custom_properties = CustomPropertyReader.read_many(reader)
            elif tag == 'delete_protected':
                obj.delete_protected = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disks':
                obj.disks = DiskReader.read_many(reader)
            elif tag == 'display':
                obj.display = DisplayReader.read_one(reader)
            elif tag == 'domain':
                obj.domain = DomainReader.read_one(reader)
            elif tag == 'graphics_consoles':
                obj.graphics_consoles = GraphicsConsoleReader.read_many(reader)
            elif tag == 'high_availability':
                obj.high_availability = HighAvailabilityReader.read_one(reader)
            elif tag == 'initialization':
                obj.initialization = InitializationReader.read_one(reader)
            elif tag == 'io':
                obj.io = IoReader.read_one(reader)
            elif tag == 'large_icon':
                obj.large_icon = IconReader.read_one(reader)
            elif tag == 'memory':
                obj.memory = Reader.read_integer(reader)
            elif tag == 'memory_policy':
                obj.memory_policy = MemoryPolicyReader.read_one(reader)
            elif tag == 'migration':
                obj.migration = MigrationOptionsReader.read_one(reader)
            elif tag == 'migration_downtime':
                obj.migration_downtime = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'nics':
                obj.nics = NicReader.read_many(reader)
            elif tag == 'origin':
                obj.origin = Reader.read_string(reader)
            elif tag == 'os':
                obj.os = OperatingSystemReader.read_one(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'rng_device':
                obj.rng_device = RngDeviceReader.read_one(reader)
            elif tag == 'serial_number':
                obj.serial_number = SerialNumberReader.read_one(reader)
            elif tag == 'small_icon':
                obj.small_icon = IconReader.read_one(reader)
            elif tag == 'soundcard_enabled':
                obj.soundcard_enabled = Reader.read_boolean(reader)
            elif tag == 'sso':
                obj.sso = SsoReader.read_one(reader)
            elif tag == 'start_paused':
                obj.start_paused = Reader.read_boolean(reader)
            elif tag == 'stateless':
                obj.stateless = Reader.read_boolean(reader)
            elif tag == 'status':
                obj.status = types.TemplateStatus(Reader.read_string(reader).lower())
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'tags':
                obj.tags = TagReader.read_many(reader)
            elif tag == 'time_zone':
                obj.time_zone = TimeZoneReader.read_one(reader)
            elif tag == 'tunnel_migration':
                obj.tunnel_migration = Reader.read_boolean(reader)
            elif tag == 'type':
                obj.type = types.VmType(Reader.read_string(reader).lower())
            elif tag == 'usb':
                obj.usb = UsbReader.read_one(reader)
            elif tag == 'version':
                obj.version = TemplateVersionReader.read_one(reader)
            elif tag == 'virtio_scsi':
                obj.virtio_scsi = VirtioScsiReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'watchdogs':
                obj.watchdogs = WatchdogReader.read_many(reader)
            elif tag == 'link':
                TemplateReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(TemplateReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "cdroms":
                obj.cdroms = list
            elif rel == "disks":
                obj.disks = list
            elif rel == "graphicsconsoles":
                obj.graphics_consoles = list
            elif rel == "nics":
                obj.nics = list
            elif rel == "permissions":
                obj.permissions = list
            elif rel == "tags":
                obj.tags = list
            elif rel == "watchdogs":
                obj.watchdogs = list
        reader.next_element()


class TemplateVersionReader(Reader):

    def __init__(self):
        super(TemplateVersionReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.TemplateVersion()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'base_template':
                obj.base_template = TemplateReader.read_one(reader)
            elif tag == 'version_name':
                obj.version_name = Reader.read_string(reader)
            elif tag == 'version_number':
                obj.version_number = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(TemplateVersionReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class TicketReader(Reader):

    def __init__(self):
        super(TicketReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Ticket()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'expiry':
                obj.expiry = Reader.read_integer(reader)
            elif tag == 'value':
                obj.value = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(TicketReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class TimeZoneReader(Reader):

    def __init__(self):
        super(TimeZoneReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.TimeZone()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'utc_offset':
                obj.utc_offset = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(TimeZoneReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class TransparentHugePagesReader(Reader):

    def __init__(self):
        super(TransparentHugePagesReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.TransparentHugePages()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(TransparentHugePagesReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class UnmanagedNetworkReader(Reader):

    def __init__(self):
        super(UnmanagedNetworkReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.UnmanagedNetwork()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'host_nic':
                obj.host_nic = HostNicReader.read_one(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(UnmanagedNetworkReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class UsbReader(Reader):

    def __init__(self):
        super(UsbReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Usb()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            elif tag == 'type':
                obj.type = types.UsbType(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(UsbReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class UserReader(Reader):

    def __init__(self):
        super(UserReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.User()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'department':
                obj.department = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'domain':
                obj.domain = DomainReader.read_one(reader)
            elif tag == 'domain_entry_id':
                obj.domain_entry_id = Reader.read_string(reader)
            elif tag == 'email':
                obj.email = Reader.read_string(reader)
            elif tag == 'groups':
                obj.groups = GroupReader.read_many(reader)
            elif tag == 'last_name':
                obj.last_name = Reader.read_string(reader)
            elif tag == 'logged_in':
                obj.logged_in = Reader.read_boolean(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'namespace':
                obj.namespace = Reader.read_string(reader)
            elif tag == 'password':
                obj.password = Reader.read_string(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'principal':
                obj.principal = Reader.read_string(reader)
            elif tag == 'roles':
                obj.roles = RoleReader.read_many(reader)
            elif tag == 'ssh_public_keys':
                obj.ssh_public_keys = SshPublicKeyReader.read_many(reader)
            elif tag == 'tags':
                obj.tags = TagReader.read_many(reader)
            elif tag == 'user_name':
                obj.user_name = Reader.read_string(reader)
            elif tag == 'link':
                UserReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(UserReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "groups":
                obj.groups = list
            elif rel == "permissions":
                obj.permissions = list
            elif rel == "roles":
                obj.roles = list
            elif rel == "sshpublickeys":
                obj.ssh_public_keys = list
            elif rel == "tags":
                obj.tags = list
        reader.next_element()


class ValueReader(Reader):

    def __init__(self):
        super(ValueReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Value()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'datum':
                obj.datum = Reader.read_decimal(reader)
            elif tag == 'detail':
                obj.detail = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(ValueReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class VcpuPinReader(Reader):

    def __init__(self):
        super(VcpuPinReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.VcpuPin()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cpu_set':
                obj.cpu_set = Reader.read_string(reader)
            elif tag == 'vcpu':
                obj.vcpu = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VcpuPinReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class VendorReader(Reader):

    def __init__(self):
        super(VendorReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Vendor()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VendorReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class VersionReader(Reader):

    def __init__(self):
        super(VersionReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Version()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'build':
                obj.build = Reader.read_integer(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'full_version':
                obj.full_version = Reader.read_string(reader)
            elif tag == 'major':
                obj.major = Reader.read_integer(reader)
            elif tag == 'minor':
                obj.minor = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'revision':
                obj.revision = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VersionReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class VirtioScsiReader(Reader):

    def __init__(self):
        super(VirtioScsiReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.VirtioScsi()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'enabled':
                obj.enabled = Reader.read_boolean(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VirtioScsiReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class VirtualNumaNodeReader(Reader):

    def __init__(self):
        super(VirtualNumaNodeReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.VirtualNumaNode()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'cpu':
                obj.cpu = CpuReader.read_one(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'index':
                obj.index = Reader.read_integer(reader)
            elif tag == 'memory':
                obj.memory = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'node_distance':
                obj.node_distance = Reader.read_string(reader)
            elif tag == 'numa_node_pins':
                obj.numa_node_pins = NumaNodePinReader.read_many(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'link':
                VirtualNumaNodeReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VirtualNumaNodeReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "statistics":
                obj.statistics = list
        reader.next_element()


class VlanReader(Reader):

    def __init__(self):
        super(VlanReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Vlan()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = Reader.parse_integer(value)

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VlanReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class VmReader(Reader):

    def __init__(self):
        super(VmReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Vm()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'affinity_labels':
                obj.affinity_labels = AffinityLabelReader.read_many(reader)
            elif tag == 'applications':
                obj.applications = ApplicationReader.read_many(reader)
            elif tag == 'bios':
                obj.bios = BiosReader.read_one(reader)
            elif tag == 'cdroms':
                obj.cdroms = CdromReader.read_many(reader)
            elif tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'console':
                obj.console = ConsoleReader.read_one(reader)
            elif tag == 'cpu':
                obj.cpu = CpuReader.read_one(reader)
            elif tag == 'cpu_profile':
                obj.cpu_profile = CpuProfileReader.read_one(reader)
            elif tag == 'cpu_shares':
                obj.cpu_shares = Reader.read_integer(reader)
            elif tag == 'creation_time':
                obj.creation_time = Reader.read_date(reader)
            elif tag == 'custom_compatibility_version':
                obj.custom_compatibility_version = VersionReader.read_one(reader)
            elif tag == 'custom_cpu_model':
                obj.custom_cpu_model = Reader.read_string(reader)
            elif tag == 'custom_emulated_machine':
                obj.custom_emulated_machine = Reader.read_string(reader)
            elif tag == 'custom_properties':
                obj.custom_properties = CustomPropertyReader.read_many(reader)
            elif tag == 'delete_protected':
                obj.delete_protected = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'disk_attachments':
                obj.disk_attachments = DiskAttachmentReader.read_many(reader)
            elif tag == 'disks':
                obj.disks = DiskReader.read_many(reader)
            elif tag == 'display':
                obj.display = DisplayReader.read_one(reader)
            elif tag == 'domain':
                obj.domain = DomainReader.read_one(reader)
            elif tag == 'external_host_provider':
                obj.external_host_provider = ExternalHostProviderReader.read_one(reader)
            elif tag == 'floppies':
                obj.floppies = FloppyReader.read_many(reader)
            elif tag == 'fqdn':
                obj.fqdn = Reader.read_string(reader)
            elif tag == 'graphics_consoles':
                obj.graphics_consoles = GraphicsConsoleReader.read_many(reader)
            elif tag == 'guest_operating_system':
                obj.guest_operating_system = GuestOperatingSystemReader.read_one(reader)
            elif tag == 'guest_time_zone':
                obj.guest_time_zone = TimeZoneReader.read_one(reader)
            elif tag == 'high_availability':
                obj.high_availability = HighAvailabilityReader.read_one(reader)
            elif tag == 'host':
                obj.host = HostReader.read_one(reader)
            elif tag == 'host_devices':
                obj.host_devices = HostDeviceReader.read_many(reader)
            elif tag == 'initialization':
                obj.initialization = InitializationReader.read_one(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'io':
                obj.io = IoReader.read_one(reader)
            elif tag == 'katello_errata':
                obj.katello_errata = KatelloErratumReader.read_many(reader)
            elif tag == 'large_icon':
                obj.large_icon = IconReader.read_one(reader)
            elif tag == 'memory':
                obj.memory = Reader.read_integer(reader)
            elif tag == 'memory_policy':
                obj.memory_policy = MemoryPolicyReader.read_one(reader)
            elif tag == 'migration':
                obj.migration = MigrationOptionsReader.read_one(reader)
            elif tag == 'migration_downtime':
                obj.migration_downtime = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'next_run_configuration_exists':
                obj.next_run_configuration_exists = Reader.read_boolean(reader)
            elif tag == 'nics':
                obj.nics = NicReader.read_many(reader)
            elif tag == 'host_numa_nodes':
                obj.numa_nodes = NumaNodeReader.read_many(reader)
            elif tag == 'numa_tune_mode':
                obj.numa_tune_mode = types.NumaTuneMode(Reader.read_string(reader).lower())
            elif tag == 'origin':
                obj.origin = Reader.read_string(reader)
            elif tag == 'os':
                obj.os = OperatingSystemReader.read_one(reader)
            elif tag == 'payloads':
                obj.payloads = PayloadReader.read_many(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'placement_policy':
                obj.placement_policy = VmPlacementPolicyReader.read_one(reader)
            elif tag == 'quota':
                obj.quota = QuotaReader.read_one(reader)
            elif tag == 'reported_devices':
                obj.reported_devices = ReportedDeviceReader.read_many(reader)
            elif tag == 'rng_device':
                obj.rng_device = RngDeviceReader.read_one(reader)
            elif tag == 'run_once':
                obj.run_once = Reader.read_boolean(reader)
            elif tag == 'serial_number':
                obj.serial_number = SerialNumberReader.read_one(reader)
            elif tag == 'sessions':
                obj.sessions = SessionReader.read_many(reader)
            elif tag == 'small_icon':
                obj.small_icon = IconReader.read_one(reader)
            elif tag == 'snapshots':
                obj.snapshots = SnapshotReader.read_many(reader)
            elif tag == 'soundcard_enabled':
                obj.soundcard_enabled = Reader.read_boolean(reader)
            elif tag == 'sso':
                obj.sso = SsoReader.read_one(reader)
            elif tag == 'start_paused':
                obj.start_paused = Reader.read_boolean(reader)
            elif tag == 'start_time':
                obj.start_time = Reader.read_date(reader)
            elif tag == 'stateless':
                obj.stateless = Reader.read_boolean(reader)
            elif tag == 'statistics':
                obj.statistics = StatisticReader.read_many(reader)
            elif tag == 'status':
                obj.status = types.VmStatus(Reader.read_string(reader).lower())
            elif tag == 'status_detail':
                obj.status_detail = Reader.read_string(reader)
            elif tag == 'stop_reason':
                obj.stop_reason = Reader.read_string(reader)
            elif tag == 'stop_time':
                obj.stop_time = Reader.read_date(reader)
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'tags':
                obj.tags = TagReader.read_many(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'time_zone':
                obj.time_zone = TimeZoneReader.read_one(reader)
            elif tag == 'tunnel_migration':
                obj.tunnel_migration = Reader.read_boolean(reader)
            elif tag == 'type':
                obj.type = types.VmType(Reader.read_string(reader).lower())
            elif tag == 'usb':
                obj.usb = UsbReader.read_one(reader)
            elif tag == 'use_latest_template_version':
                obj.use_latest_template_version = Reader.read_boolean(reader)
            elif tag == 'virtio_scsi':
                obj.virtio_scsi = VirtioScsiReader.read_one(reader)
            elif tag == 'vm_pool':
                obj.vm_pool = VmPoolReader.read_one(reader)
            elif tag == 'watchdogs':
                obj.watchdogs = WatchdogReader.read_many(reader)
            elif tag == 'link':
                VmReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VmReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "affinitylabels":
                obj.affinity_labels = list
            elif rel == "applications":
                obj.applications = list
            elif rel == "cdroms":
                obj.cdroms = list
            elif rel == "diskattachments":
                obj.disk_attachments = list
            elif rel == "disks":
                obj.disks = list
            elif rel == "floppies":
                obj.floppies = list
            elif rel == "graphicsconsoles":
                obj.graphics_consoles = list
            elif rel == "hostdevices":
                obj.host_devices = list
            elif rel == "katelloerrata":
                obj.katello_errata = list
            elif rel == "nics":
                obj.nics = list
            elif rel == "numanodes":
                obj.numa_nodes = list
            elif rel == "permissions":
                obj.permissions = list
            elif rel == "reporteddevices":
                obj.reported_devices = list
            elif rel == "sessions":
                obj.sessions = list
            elif rel == "snapshots":
                obj.snapshots = list
            elif rel == "statistics":
                obj.statistics = list
            elif rel == "tags":
                obj.tags = list
            elif rel == "watchdogs":
                obj.watchdogs = list
        reader.next_element()


class VmBaseReader(Reader):

    def __init__(self):
        super(VmBaseReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.VmBase()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'bios':
                obj.bios = BiosReader.read_one(reader)
            elif tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'console':
                obj.console = ConsoleReader.read_one(reader)
            elif tag == 'cpu':
                obj.cpu = CpuReader.read_one(reader)
            elif tag == 'cpu_profile':
                obj.cpu_profile = CpuProfileReader.read_one(reader)
            elif tag == 'cpu_shares':
                obj.cpu_shares = Reader.read_integer(reader)
            elif tag == 'creation_time':
                obj.creation_time = Reader.read_date(reader)
            elif tag == 'custom_compatibility_version':
                obj.custom_compatibility_version = VersionReader.read_one(reader)
            elif tag == 'custom_cpu_model':
                obj.custom_cpu_model = Reader.read_string(reader)
            elif tag == 'custom_emulated_machine':
                obj.custom_emulated_machine = Reader.read_string(reader)
            elif tag == 'custom_properties':
                obj.custom_properties = CustomPropertyReader.read_many(reader)
            elif tag == 'delete_protected':
                obj.delete_protected = Reader.read_boolean(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'display':
                obj.display = DisplayReader.read_one(reader)
            elif tag == 'domain':
                obj.domain = DomainReader.read_one(reader)
            elif tag == 'high_availability':
                obj.high_availability = HighAvailabilityReader.read_one(reader)
            elif tag == 'initialization':
                obj.initialization = InitializationReader.read_one(reader)
            elif tag == 'io':
                obj.io = IoReader.read_one(reader)
            elif tag == 'large_icon':
                obj.large_icon = IconReader.read_one(reader)
            elif tag == 'memory':
                obj.memory = Reader.read_integer(reader)
            elif tag == 'memory_policy':
                obj.memory_policy = MemoryPolicyReader.read_one(reader)
            elif tag == 'migration':
                obj.migration = MigrationOptionsReader.read_one(reader)
            elif tag == 'migration_downtime':
                obj.migration_downtime = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'origin':
                obj.origin = Reader.read_string(reader)
            elif tag == 'os':
                obj.os = OperatingSystemReader.read_one(reader)
            elif tag == 'rng_device':
                obj.rng_device = RngDeviceReader.read_one(reader)
            elif tag == 'serial_number':
                obj.serial_number = SerialNumberReader.read_one(reader)
            elif tag == 'small_icon':
                obj.small_icon = IconReader.read_one(reader)
            elif tag == 'soundcard_enabled':
                obj.soundcard_enabled = Reader.read_boolean(reader)
            elif tag == 'sso':
                obj.sso = SsoReader.read_one(reader)
            elif tag == 'start_paused':
                obj.start_paused = Reader.read_boolean(reader)
            elif tag == 'stateless':
                obj.stateless = Reader.read_boolean(reader)
            elif tag == 'storage_domain':
                obj.storage_domain = StorageDomainReader.read_one(reader)
            elif tag == 'time_zone':
                obj.time_zone = TimeZoneReader.read_one(reader)
            elif tag == 'tunnel_migration':
                obj.tunnel_migration = Reader.read_boolean(reader)
            elif tag == 'type':
                obj.type = types.VmType(Reader.read_string(reader).lower())
            elif tag == 'usb':
                obj.usb = UsbReader.read_one(reader)
            elif tag == 'virtio_scsi':
                obj.virtio_scsi = VirtioScsiReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VmBaseReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class VmPlacementPolicyReader(Reader):

    def __init__(self):
        super(VmPlacementPolicyReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.VmPlacementPolicy()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'affinity':
                obj.affinity = types.VmAffinity(Reader.read_string(reader).lower())
            elif tag == 'hosts':
                obj.hosts = HostReader.read_many(reader)
            elif tag == 'link':
                VmPlacementPolicyReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VmPlacementPolicyReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "hosts":
                obj.hosts = list
        reader.next_element()


class VmPoolReader(Reader):

    def __init__(self):
        super(VmPoolReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.VmPool()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'cluster':
                obj.cluster = ClusterReader.read_one(reader)
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'display':
                obj.display = DisplayReader.read_one(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'max_user_vms':
                obj.max_user_vms = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'prestarted_vms':
                obj.prestarted_vms = Reader.read_integer(reader)
            elif tag == 'rng_device':
                obj.rng_device = RngDeviceReader.read_one(reader)
            elif tag == 'size':
                obj.size = Reader.read_integer(reader)
            elif tag == 'soundcard_enabled':
                obj.soundcard_enabled = Reader.read_boolean(reader)
            elif tag == 'stateful':
                obj.stateful = Reader.read_boolean(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'type':
                obj.type = types.VmPoolType(Reader.read_string(reader).lower())
            elif tag == 'use_latest_template_version':
                obj.use_latest_template_version = Reader.read_boolean(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'link':
                VmPoolReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VmPoolReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "permissions":
                obj.permissions = list
        reader.next_element()


class VmSummaryReader(Reader):

    def __init__(self):
        super(VmSummaryReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.VmSummary()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'active':
                obj.active = Reader.read_integer(reader)
            elif tag == 'migrating':
                obj.migrating = Reader.read_integer(reader)
            elif tag == 'total':
                obj.total = Reader.read_integer(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VmSummaryReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class VnicPassThroughReader(Reader):

    def __init__(self):
        super(VnicPassThroughReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.VnicPassThrough()

        # Process the attributes:
        obj.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'mode':
                obj.mode = types.VnicPassThroughMode(Reader.read_string(reader).lower())
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VnicPassThroughReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class VnicProfileReader(Reader):

    def __init__(self):
        super(VnicProfileReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.VnicProfile()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'custom_properties':
                obj.custom_properties = CustomPropertyReader.read_many(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'network':
                obj.network = NetworkReader.read_one(reader)
            elif tag == 'network_filter':
                obj.network_filter = NetworkFilterReader.read_one(reader)
            elif tag == 'pass_through':
                obj.pass_through = VnicPassThroughReader.read_one(reader)
            elif tag == 'permissions':
                obj.permissions = PermissionReader.read_many(reader)
            elif tag == 'port_mirroring':
                obj.port_mirroring = Reader.read_boolean(reader)
            elif tag == 'qos':
                obj.qos = QosReader.read_one(reader)
            elif tag == 'link':
                VnicProfileReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VnicProfileReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "permissions":
                obj.permissions = list
        reader.next_element()


class VolumeGroupReader(Reader):

    def __init__(self):
        super(VolumeGroupReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.VolumeGroup()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'logical_units':
                obj.logical_units = LogicalUnitReader.read_many(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(VolumeGroupReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs


class WatchdogReader(Reader):

    def __init__(self):
        super(WatchdogReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Watchdog()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'action':
                obj.action = types.WatchdogAction(Reader.read_string(reader).lower())
            elif tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'instance_type':
                obj.instance_type = InstanceTypeReader.read_one(reader)
            elif tag == 'model':
                obj.model = types.WatchdogModel(Reader.read_string(reader).lower())
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'template':
                obj.template = TemplateReader.read_one(reader)
            elif tag == 'vm':
                obj.vm = VmReader.read_one(reader)
            elif tag == 'vms':
                obj.vms = VmReader.read_many(reader)
            elif tag == 'link':
                WatchdogReader._read_link(reader, obj)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(WatchdogReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs

    @staticmethod
    def _read_link(reader, obj):
        # Process the attributes:
        href = reader.get_attribute('href')
        rel = reader.get_attribute('rel')
        if href and rel:
            list = List(href)
            if rel == "vms":
                obj.vms = list
        reader.next_element()


class WeightReader(Reader):

    def __init__(self):
        super(WeightReader, self).__init__()

    @staticmethod
    def read_one(reader):
        # Do nothing if there aren't more tags:
        if not reader.forward():
            return None

        # Create the object:
        obj = types.Weight()

        # Process the attributes:
        obj.href = reader.get_attribute('href')
        value = reader.get_attribute('id')
        if value is not None:
            obj.id = value

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return obj

        # Process the inner elements:
        while reader.forward():
            tag = reader.node_name()
            if tag == 'comment':
                obj.comment = Reader.read_string(reader)
            elif tag == 'description':
                obj.description = Reader.read_string(reader)
            elif tag == 'factor':
                obj.factor = Reader.read_integer(reader)
            elif tag == 'name':
                obj.name = Reader.read_string(reader)
            elif tag == 'scheduling_policy':
                obj.scheduling_policy = SchedulingPolicyReader.read_one(reader)
            elif tag == 'scheduling_policy_unit':
                obj.scheduling_policy_unit = SchedulingPolicyUnitReader.read_one(reader)
            else:
                reader.next_element()

        # Discard the end tag:
        reader.read()

        return obj

    @staticmethod
    def read_many(reader):
        # Do nothing if there aren't more tags:
        objs = List()
        if not reader.forward():
            return objs

        # Process the attributes:
        objs.href = reader.get_attribute('href')

        # Discard the start tag:
        empty = reader.empty_element()
        reader.read()
        if empty:
            return objs

        # Process the inner elements:
        while reader.forward():
            objs.append(WeightReader.read_one(reader))

        # Discard the end tag:
        reader.read()

        return objs
