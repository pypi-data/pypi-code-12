__author__ = 'zhonghong'

import pymysql

from zapi.core.config import Config
from zapi.core.db import DB

class Common(object):

    def __init__(self, app_path):
        self.app_path = app_path

    @property
    def _get_db_handler(self):
        db = DB(self._get_config.db, cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        conv = db.conn._con._con.decoders.copy()
        # change mysql Decimal format to string int
        conv[0] = int
        conv[246] = int
        # change mysql datetime\date\timestamp format to string format
        conv[7] = str
        conv[10] = str
        conv[12] = str
        db.conn._con._con.decoders = conv
        return db

    @property
    def _get_config(self):
        return Config(self.app_path)