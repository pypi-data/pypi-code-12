# Copyright 2016 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from oslo_log import log as logging

from vitrage import clients
from vitrage.common.constants import NotifierEventTypes
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.aodh.properties import AodhState
from vitrage.entity_graph.states.normalized_alarm_severity import \
    NormalizedAlarmSeverity
from vitrage.notifier.plugins.base import NotifierBase


LOG = logging.getLogger(__name__)


severity_translation = {
    NormalizedAlarmSeverity.CRITICAL: 'critical',
    NormalizedAlarmSeverity.SEVERE: 'moderate',
    NormalizedAlarmSeverity.WARNING: 'low',
}


class AodhNotifier(NotifierBase):

    @staticmethod
    def get_notifier_name():
        return 'aodh'

    def __init__(self, conf):
        super(AodhNotifier, self).__init__(conf)
        self.client = clients.ceilometer_client(conf)

    def process_event(self, data, event_type):
        response = None
        if event_type == NotifierEventTypes.ACTIVATE_DEDUCED_ALARM_EVENT:
            if not data.get(VProps.ID):
                response = self._create_aodh_alarm(data, AodhState.ALARM)
            else:
                response = self._update_aodh_alarm(data, AodhState.ALARM)
        elif event_type == NotifierEventTypes.DEACTIVATE_DEDUCED_ALARM_EVENT:
            response = self._update_aodh_alarm(data, AodhState.OK)

        if response and response.alarm_id:
            LOG.info('Aodh Alarm id %s: ', response.alarm_id)
        else:
            LOG.error('Failed to %s Aodh Alarm \n%s', event_type, str(data))

    def _create_aodh_alarm(self, alarm, state):
        alarm_request = _alarm_request(alarm, state)
        try:
            LOG.info('Aodh Alarm - Activate: ' + str(alarm_request))
            return self.client.alarms.create(**alarm_request)
        except Exception as e:
            LOG.exception('Failed to activate Aodh Alarm Got Exception: %s', e)
            return

    def _update_aodh_alarm(self, alarm, state):
        aodh_id = alarm.get(VProps.ID)
        try:
            LOG.info('Aodh Alarm $%s update state %s', aodh_id, state)
            return self.client.alarms.update(alarm_id=aodh_id, state=state)
        except Exception as e:
            LOG.exception('Failed to update Aodh Alarm Got Exception: %s', e)
            return


def _alarm_request(data, state):
    # TODO(ihefetz) resource id should come from the alarm
    affected_resource_id = data.get(VProps.VITRAGE_ID).replace(
        'ALARM:vitrage:deduced_vm_alarm:RESOURCE:nova.instance:', '')
    alarm_name = data.get(VProps.NAME)
    aodh_alarm_name = '_'.join([alarm_name, affected_resource_id])
    severity = severity_translation.get(data.get(VProps.SEVERITY), 'low')
    return dict(
        name=aodh_alarm_name,
        description=u'Vitrage deduced alarm',
        event_rule=dict(query=[
            dict(
                field=u'resource_id',
                type='',
                op=u'eq',
                value=affected_resource_id),
            dict(
                field=u'vitrage_id',
                type='',
                op=u'eq',
                value=data.get(VProps.VITRAGE_ID))]),
        severity=severity,
        state=state,
        type=u'event')
