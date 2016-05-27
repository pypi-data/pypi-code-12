# clustercron/elb.py
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai
# -*- coding: utf-8 -*-

'''
clustercron.elb
---------------
'''

from __future__ import unicode_literals

import logging
import requests
import boto.ec2.elb


logger = logging.getLogger(__name__)


class Elb(object):
    URL_INSTANCE_ID = \
        'http://169.254.169.254/1.0/meta-data/instance-id'

    def __init__(self, lb_name, timeout=3):
        self.lb_name = lb_name
        self.timeout = timeout

    def _get_instance_id(self):
        logger.debug('Get instance ID')
        instance_id = None
        try:
            resp = requests.get(self.URL_INSTANCE_ID, timeout=self.timeout)
        except Exception as error:
            logger.error('Could not get instance health states: %s', error)
        else:
            instance_id = resp.text
            logger.info('Instance ID: %s', instance_id)
        return instance_id

    def _get_inst_health_states(self):
        logger.debug('Get instance health states')
        inst_health_states = []
        try:
            conn = boto.ec2.elb.ELBConnection()
            lb = conn.get_all_load_balancers(
                load_balancer_names=[self.lb_name])[0]
            inst_health_states = lb.get_instance_health()
        except Exception as error:
            print(error)
            logger.error('Could not get instance health states: %s', error)
        else:
            logger.debug('Instance health states: %s', inst_health_states)
        return inst_health_states

    def _is_master(self, instance_id, inst_health_states):
        logger.debug('Check if instance is master')
        res = False
        instances_all = sorted([x.instance_id for x in inst_health_states])
        logger.info(
            'All instances: %s Instance in list: %s',
            ', '.join(instances_all),
            instance_id in instances_all,
        )
        instances_in_service = sorted([
            x.instance_id for x in inst_health_states
            if x.state == 'InService'
        ])
        logger.info(
            'Instances in service: %s Instance in list: %s',
            ', '.join(instances_in_service),
            instance_id in instances_in_service,
        )
        if instances_in_service:
            res = instance_id == instances_in_service[0]
        logger.info('This instance master: %s', res)
        return res

    def master(self):
        instance_id = self._get_instance_id()
        if instance_id:
            inst_health_states = self._get_inst_health_states()
            return self._is_master(instance_id, inst_health_states)
        return False
