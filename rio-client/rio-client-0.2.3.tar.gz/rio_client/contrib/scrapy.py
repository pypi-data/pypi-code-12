# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
from time import mktime
from datetime import datetime

from scrapy import log
from scrapy.exceptions import NotConfigured

from rio_client.base import Client

class Rio(object):

    def __init__(self, dsn, timeout, action):
        self.client = Client(dsn, timeout=timeout)
        self.action = action

    @staticmethod
    def get_setting(key, settings=None, silent=True):
        setting = os.environ.get(key) or (settings or {}).get(key)
        if not setting and not silent:
            raise NotConfigured('No %s configured' % key)
        return setting

    @classmethod
    def from_settings(cls, settings):
        dsn = cls.get_setting('RIO_DSN', settings, silent=False)
        action = cls.get_setting('RIO_ACTION', settings, silent=False) or 'scrapy-item-scraped'
        timeout = cls.get_setting('RIO_TIMEOUT', settings, silent=False) or 1
        return cls(dsn, timeout, action)

    def process_item(self, item, spider):
        data = dict(item)
        for key in data:
            if isinstance(data[key], datetime):
                data[key] = mktime(data[key].timetuple())

        try:
            info = self.client.emit(self.action, dict(item=data))
            if info['is_success']:
                log.msg('[rio-action] [success] event: %s, task: %s' % (
                    info['event_uuid'], info['task_id']))
            else:
                log.msg('[rio-action] [failure] network error')
        except Exception as e:
            log.msg('[rio-action] [failure] %s' % str(e))

        return item
