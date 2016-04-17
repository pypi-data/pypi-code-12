# Copyright 2016 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg

from vitrage.datasources.aodh import AODH_DATASOURCE
from vitrage.datasources.cinder.volume import CINDER_VOLUME_DATASOURCE
from vitrage.datasources.nagios import NAGIOS_DATASOURCE
from vitrage.datasources.neutron.network import NEUTRON_NETWORK_DATASOURCE
from vitrage.datasources.nova.host import NOVA_HOST_DATASOURCE
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources.nova.zone import NOVA_ZONE_DATASOURCE
from vitrage.datasources.static_physical import STATIC_PHYSICAL_DATASOURCE

OPENSTACK_CLUSTER = 'openstack.cluster'

# Register options for the service
OPTS = [

    cfg.ListOpt('types',
                default=[NOVA_HOST_DATASOURCE,
                         NOVA_INSTANCE_DATASOURCE,
                         NOVA_ZONE_DATASOURCE,
                         NAGIOS_DATASOURCE,
                         STATIC_PHYSICAL_DATASOURCE,
                         AODH_DATASOURCE,
                         CINDER_VOLUME_DATASOURCE,
                         NEUTRON_NETWORK_DATASOURCE],
                help='Names of supported data sources'),
    cfg.ListOpt('path',
                default=['vitrage.datasources'],
                help='base path for data sources'),
    cfg.IntOpt('snapshots_interval',
               default=600,
               min=10,
               help='interval between full snapshots')
]
