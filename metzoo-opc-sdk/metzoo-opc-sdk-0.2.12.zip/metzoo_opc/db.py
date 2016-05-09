# -*- coding: utf-8 -*-

import sqlite3
import logging

from .data import OPCData


def trim(s):
    r = ""
    for line in s.split("\n"):
        r += line.strip() + " "
    return r.strip()


class DB(object):
    __CREATE_TABLE__ = trim("""
        CREATE TABLE IF NOT EXISTS data (
              data_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                  tag TEXT NOT NULL,
                value REAL,
              quality TEXT NOT NULL,
            timestamp INTEGER
        );
    """)

    def __init__(self, filename, mapping):
        self.__filename = filename
        self.__run(DB.__CREATE_TABLE__)
        self._mapping = mapping


    __INSERT__ = trim("""
        INSERT INTO data (tag, value, quality, timestamp)
        VALUES ("{}", {}, "{}", {})
    """)

    def save(self, data):
        self.__run(DB.__INSERT__.format(data.tag, data.value, data.quality, data.timestamp).replace("None", "NULL"))


    __SELECT__ = trim("""
        SELECT data_id, tag, value, quality, timestamp
        FROM data
        WHERE quality='Good'
        ORDER BY data_id
    """)

    def load(self):
        rows = self.__select(DB.__SELECT__)
        return [OPCData(row[0], row[1], row[2], row[3], row[4], self._mapping) for row in rows]


    __DELETE__ = trim("""
        DELETE FROM data
        WHERE data_id IN ({})
    """)

    def delete(self, data_id):
        self.__run(DB.__DELETE__.format(data_id).replace("[","").replace("]",""))


    def __run(self, query):
        logging.getLogger("MetzooOPC.DB").debug("run :: {}".format(query))
        connection = sqlite3.connect(self.__filename)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()

    def __select(self, query):
        logging.getLogger("MetzooOPC.DB").debug("select :: {}".format(query))
        connection = sqlite3.connect(self.__filename)
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()
        return result
