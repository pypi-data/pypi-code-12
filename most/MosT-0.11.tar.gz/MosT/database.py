# -*- coding: utf-8 -*-
__author__ = 'tangke'
import pymysql

from datacontext import DataContext
from log import MyLog


class DataBase:
    def __init__(self, database_name):
        self._name = database_name
        self._env = DataContext.env
        self._conn = None

    def _connect(self):
        if self._conn is None and self._name in DataContext.database_dict:
            database_config_obj = DataContext.database_dict[self._name+self._env]
            try:
                self._conn = pymysql.connect(host=database_config_obj['url'], port=database_config_obj['port'],
                                             user=database_config_obj['username'], passwd=database_config_obj['passwd'],
                                             charset=database_config_obj['charset'], db=self._name)
            except Exception, e:
                MyLog.log().debug(e)

    def _close_conn(self):
        if self._conn is not None:
            self._conn.close()

    def execute_sql(self, select_sql):
        self._connect()
        try:
            cur = self._conn.cursor()
            cur.execute(select_sql)
            return cur
        except Exception, e:
            MyLog.log().debug(e)
        finally:
            self._close_conn()

    def execute_commit(self, *args):
        self._connect()
        try:
            cur = self._conn.cursor()
            for sql in args:
                cur.execute(sql)
            self._conn.commit()
            self._close_conn()
        except Exception, e:
            MyLog.log().debug(e)
        finally:
            self._close_conn()



if __name__ == '__main__':
    from MosT.universalconfig import read_database_config
    read_database_config()
    print DataBase("smartmatch_syn").execute_sql("select * from papers limit 1")
