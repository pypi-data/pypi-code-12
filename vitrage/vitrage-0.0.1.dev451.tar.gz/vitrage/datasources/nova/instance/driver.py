# Copyright 2016 - Alcatel-Lucent
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,  software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND,  either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_log import log as logging

from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import SyncMode
from vitrage.datasources.nova.instance import NOVA_INSTANCE_DATASOURCE
from vitrage.datasources.nova.nova_driver_base import NovaDriverBase

LOG = logging.getLogger(__name__)


class InstanceDriver(NovaDriverBase):

    @staticmethod
    def extract_events(instances):
        return [instance.__dict__ for instance in instances]

    def get_all(self, sync_mode):
        return self.make_pickleable(
            self.extract_events(self.client.servers.list()),
            NOVA_INSTANCE_DATASOURCE,
            sync_mode,
            'manager')

    @staticmethod
    def enrich_event(event, event_type):
        event[DSProps.EVENT_TYPE] = event_type

        return InstanceDriver.make_pickleable([event],
                                              NOVA_INSTANCE_DATASOURCE,
                                              SyncMode.UPDATE)[0]

    @staticmethod
    def get_event_types(conf):
        # Add event_types to receive notifications about
        return ['compute.instance.create.start',
                'compute.instance.create.error',
                'compute.instance.create.end',
                'compute.instance.delete.start',
                'compute.instance.delete.end',
                'compute.instance.finish_resize.end',
                'compute.instance.live_migration.post.dest.end',
                'compute.instance.live_migration._post.end',
                'compute.instance.power_off.end',
                'compute.instance.power_on.end',
                'compute.instance.reboot.end',
                'compute.instance.rebuild.end',
                'compute.instance.resize.end',
                'compute.instance.resize.revert.end',
                'compute.instance.resume',
                'compute.instance.shutdown.end',
                'compute.instance.suspend',
                'compute.instance.volume.attach',
                'compute.instance.volume.detach',
                'compute.instance.pause.end',
                'compute.instance.unpause.end'
                ]

    @staticmethod
    def get_topic(conf):
        return conf[NOVA_INSTANCE_DATASOURCE].notification_topic
