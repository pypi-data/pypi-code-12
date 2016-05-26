# Copyright (C) 2016 A10 Networks Inc. All rights reserved.

import operator

from neutronclient.common import utils

from a10_neutronclient import client_extension
from a10_neutronclient.resources import a10_scaling_group


class ScalingGroupExtension(client_extension.ClientExtension):

    resource = a10_scaling_group.SCALING_GROUP
    resource_plural = a10_scaling_group.SCALING_GROUPS

    resource_attribute_map = a10_scaling_group.RESOURCE_ATTRIBUTE_MAP

    object_path = '/%s' % resource_plural
    resource_path = '/%s/%%s' % resource_plural
    versions = ['2.0']


class ScalingGroupList(client_extension.List, ScalingGroupExtension):
    """List A10 scaling groups"""

    shell_command = 'a10-scaling-group-list'

    list_columns = ['id', 'name', 'scaling_policy_id', 'description']


class ScalingGroupCreate(client_extension.Create, ScalingGroupExtension):
    """Create A10 scaling group"""

    shell_command = 'a10-scaling-group-create'

    list_columns = ['id', 'name', 'scaling_policy_id', 'description']

    def add_known_arguments(self, parser):
        self._add_known_arguments(parser, ['name'])


class ScalingGroupUpdate(client_extension.Update, ScalingGroupExtension):
    """Update A10 scaling group"""

    shell_command = 'a10-scaling-group-update'

    list_columns = ['id', 'name', 'scaling_policy_id', 'description']


class ScalingGroupDelete(client_extension.Delete, ScalingGroupExtension):
    """Delete A10 scaling group"""

    shell_command = 'a10-scaling-group-delete'


class ScalingGroupShow(client_extension.Show, ScalingGroupExtension):
    """Show A10 scaling group"""

    shell_command = 'a10-scaling-group-show'


class ScalingGroupWorkerExtension(client_extension.ClientExtension):

    resource = a10_scaling_group.SCALING_GROUP_WORKER
    resource_plural = a10_scaling_group.SCALING_GROUP_WORKERS

    resource_attribute_map = a10_scaling_group.RESOURCE_ATTRIBUTE_MAP

    object_path = '/%s' % resource_plural
    resource_path = '/%s/%%s' % resource_plural
    versions = ['2.0']


class ScalingGroupWorkerList(client_extension.List, ScalingGroupWorkerExtension):
    """List A10 scaling group workers"""

    shell_command = 'a10-scaling-group-worker-list'

    list_columns = ['id', 'name', 'scaling_group_id', 'nova_instance_id', 'description']


class ScalingGroupWorkerCreate(client_extension.Create, ScalingGroupWorkerExtension):
    """Create A10 scaling group worker"""

    shell_command = 'a10-scaling-group-worker-create'

    list_columns = ['id', 'name', 'scaling_group_id', 'nova_instance_id', 'description']

    def add_known_arguments(self, parser):
        self._add_known_arguments(parser, ['scaling_group_id'])


class ScalingGroupWorkerUpdate(client_extension.Update, ScalingGroupWorkerExtension):
    """Update A10 scaling group worker"""

    shell_command = 'a10-scaling-group-worker-update'

    list_columns = ['id', 'name', 'scaling_group_id', 'nova_instance_id', 'description']


class ScalingGroupWorkerDelete(client_extension.Delete, ScalingGroupWorkerExtension):
    """Delete A10 scaling group worker"""

    shell_command = 'a10-scaling-group-worker-delete'


class ScalingGroupWorkerShow(client_extension.Show, ScalingGroupWorkerExtension):
    """Show A10 scaling group worker"""

    shell_command = 'a10-scaling-group-worker-show'


class ScalingPolicyExtension(client_extension.ClientExtension):

    resource = a10_scaling_group.SCALING_POLICY
    resource_plural = a10_scaling_group.SCALING_POLICIES

    resource_attribute_map = a10_scaling_group.RESOURCE_ATTRIBUTE_MAP

    object_path = '/%s' % resource_plural
    resource_path = '/%s/%%s' % resource_plural
    versions = ['2.0']

    def add_reactions_argument(self, parser):
        parser.add_argument(
            '--reactions',
            nargs='+',
            action='append',
            dest='reactions',
            type=utils.str2dict)

    def reaction2body(self, reaction_arg):
        reaction = {}
        reaction['alarm_id'] = self.get_resource_id(
            a10_scaling_group.SCALING_ALARM,
            reaction_arg.get('alarm'))
        reaction['action_id'] = self.get_resource_id(
            a10_scaling_group.SCALING_ACTION,
            reaction_arg.get('action'))
        return reaction

    def alter_body(self, parsed_args, body):
        if 'reactions' in body:
            body['reactions'] = map(self.reaction2body, reduce(operator.add, body['reactions'], []))
        return body


class ScalingPolicyList(client_extension.List, ScalingPolicyExtension):
    """List A10 scaling policies"""

    shell_command = 'a10-scaling-policy-list'

    list_columns = ['id', 'name', 'cooldown', 'min_instances', 'max_instances', 'description']


class ScalingPolicyCreate(client_extension.Create, ScalingPolicyExtension):
    """Create A10 scaling policy"""

    shell_command = 'a10-scaling-policy-create'

    list_columns = ['id', 'name', 'cooldown', 'min_instances', 'max_instances', 'description']

    def add_known_arguments(self, parser):
        self.add_reactions_argument(parser)
        self._add_known_arguments(parser, ['name'], ignore=['reactions'])


class ScalingPolicyUpdate(client_extension.Update, ScalingPolicyExtension):
    """Update A10 scaling policy"""

    shell_command = 'a10-scaling-policy-update'

    list_columns = ['id', 'name', 'cooldown', 'min_instances', 'max_instances', 'description']

    def add_known_arguments(self, parser):
        self.add_reactions_argument(parser)
        self._add_known_arguments(parser, [], ignore=['reactions'])


class ScalingPolicyDelete(client_extension.Delete, ScalingPolicyExtension):
    """Delete A10 scaling policy"""

    shell_command = 'a10-scaling-policy-delete'


class ScalingPolicyShow(client_extension.Show, ScalingPolicyExtension):
    """Show A10 scaling policy"""

    shell_command = 'a10-scaling-policy-show'


class ScalingAlarmExtension(client_extension.ClientExtension):

    resource = a10_scaling_group.SCALING_ALARM
    resource_plural = a10_scaling_group.SCALING_ALARMS

    resource_attribute_map = a10_scaling_group.RESOURCE_ATTRIBUTE_MAP

    object_path = '/%s' % resource_plural
    resource_path = '/%s/%%s' % resource_plural
    versions = ['2.0']


class ScalingAlarmList(client_extension.List, ScalingAlarmExtension):
    """List A10 scaling alarms"""

    shell_command = 'a10-scaling-alarm-list'

    list_columns = ['id', 'name',
                    'aggregation', 'measurement',
                    'operator', 'threshold', 'unit',
                    'period', 'period_unit',
                    'description']


class ScalingAlarmCreate(client_extension.Create, ScalingAlarmExtension):
    """Create A10 scaling alarm"""

    shell_command = 'a10-scaling-alarm-create'

    list_columns = ['id', 'name',
                    'aggregation', 'measurement',
                    'operator', 'threshold', 'unit',
                    'period', 'period_unit',
                    'description']

    def add_known_arguments(self, parser):
        self._add_known_arguments(parser, ['name'])


class ScalingAlarmUpdate(client_extension.Update, ScalingAlarmExtension):
    """Update A10 scaling alarm"""

    shell_command = 'a10-scaling-alarm-update'

    list_columns = ['id', 'name',
                    'aggregation', 'measurement',
                    'operator', 'threshold', 'unit',
                    'period', 'period_unit',
                    'description']


class ScalingAlarmDelete(client_extension.Delete, ScalingAlarmExtension):
    """Delete A10 scaling alarm"""

    shell_command = 'a10-scaling-alarm-delete'


class ScalingAlarmShow(client_extension.Show, ScalingAlarmExtension):
    """Show A10 scaling alarm"""

    shell_command = 'a10-scaling-alarm-show'


class ScalingActionExtension(client_extension.ClientExtension):

    resource = a10_scaling_group.SCALING_ACTION
    resource_plural = a10_scaling_group.SCALING_ACTIONS

    resource_attribute_map = a10_scaling_group.RESOURCE_ATTRIBUTE_MAP

    object_path = '/%s' % resource_plural
    resource_path = '/%s/%%s' % resource_plural
    versions = ['2.0']


class ScalingActionList(client_extension.List, ScalingActionExtension):
    """List A10 scaling actions"""

    shell_command = 'a10-scaling-action-list'

    list_columns = ['id', 'name', 'action', 'amount', 'description']


class ScalingActionCreate(client_extension.Create, ScalingActionExtension):
    """Create A10 scaling action"""

    shell_command = 'a10-scaling-action-create'

    list_columns = ['id', 'name', 'action', 'amount', 'description']

    def add_known_arguments(self, parser):
        self._add_known_arguments(parser, ['name'])


class ScalingActionUpdate(client_extension.Update, ScalingActionExtension):
    """Update A10 scaling action"""

    shell_command = 'a10-scaling-action-update'

    list_columns = ['id', 'name', 'action', 'amount', 'description']


class ScalingActionDelete(client_extension.Delete, ScalingActionExtension):
    """Delete A10 scaling action"""

    shell_command = 'a10-scaling-action-delete'


class ScalingActionShow(client_extension.Show, ScalingActionExtension):
    """Show A10 scaling action"""

    shell_command = 'a10-scaling-action-show'
