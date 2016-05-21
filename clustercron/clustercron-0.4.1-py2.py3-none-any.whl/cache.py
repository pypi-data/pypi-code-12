# clustercron/cache.py
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai
# -*- coding: utf-8 -*-

'''
clustercron.cache
-----------------
'''

from __future__ import unicode_literals
import fcntl
import io
import json
import logging
import logging.handlers
import sys
import time
import random

from datetime import datetime
from datetime import timedelta


if sys.version_info < (3,):
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes

logger = logging.getLogger(__name__)


class Cache(object):
    def __init__(self):
        self.master = False
        self.dct = {
            'master': self.master,
            'isodate': datetime(1970, 1, 1)
        }

    @staticmethod
    def json_serial(obj):
        '''
        JSON serializer for objects not serializable by default json code
        '''
        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial
        raise TypeError("Type not serializable")

    @staticmethod
    def iso2datetime_hook(dct):
        dct['isodate'] = datetime.strptime(
            dct['isodate'], '%Y-%m-%dT%H:%M:%S.%f')
        return dct

    def set_now(self):
        self.dct = {
            'master': self.master,
            'isodate': datetime.now(),
        }

    def load_json(self, fp):
        self.dct = json.load(fp, object_hook=self.iso2datetime_hook)
        self.master = self.dct['master']

    def safe_json(self, fp):
        fp.write(
            text_type(
                json.dumps(
                    self.dct,
                    default=self.json_serial,
                    ensure_ascii=False
                )
            )
        )

    def expired(self, expire_time):
        return datetime.now() - self.dct['isodate'] > \
            timedelta(seconds=int(expire_time))


def check(master_check, filename, expire_time, max_iter):
    cache = Cache()
    for i in range(int(max_iter)):
        file_exists = False
        retry = False
        time.sleep(random.random())
        try:
            logger.debug('Open cache file for read/write (try %s).', i + 1)
            fp = io.open(filename, 'r+')
            file_exists = True
        except IOError as error:
            if error.errno != 2:
                raise
            logger.debug('No cache file. Open new cache file for write.')
            fp = io.open(filename, 'w')
        try:
            logger.debug('Lock cache file.')
            fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as error:
            if error.errno != 11:
                raise
            logger.debug('Cache file is locked.')
            retry = True
        else:
            if file_exists:
                logger.debug('Read cache from existing file.')
                cache.load_json(fp)
                if cache.expired(expire_time):
                    logger.debug('Cache expired, do check.')
                    cache.master = master_check()
                    cache.set_now()
                    logger.debug('Write cache to existing file.')
                    fp.seek(0)
                    cache.safe_json(fp)
                    fp.truncate()
                else:
                    logger.debug('Cache not expired.')
            else:
                logger.debug('Do check.')
                cache.master = master_check()
                cache.set_now()
                logger.debug('Write cache to new file.')
                cache.safe_json(fp)
        finally:
            logger.debug('Unlock cache file.')
            fcntl.flock(fp, fcntl.LOCK_UN)
            logger.debug('Close cache file.')
            fp.close()
        if retry:
            logger.debug('Sleep 1 second before retry.')
            time.sleep(1)
            continue
        else:
            break
    logger.debug('Is master: %s,', cache.master)
    return cache.master
