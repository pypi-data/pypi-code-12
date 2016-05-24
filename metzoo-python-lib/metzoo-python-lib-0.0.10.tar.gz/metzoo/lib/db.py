# -*- coding: utf-8 -*-

import sqlite3
import logging

def trim(s):
    return " ".join([line.strip() for line in s.split("\n")]).strip()

from collections import namedtuple
MetzooData = namedtuple('MetzooData', ['data_id', 'timestamp', 'agent', 'metric', 'value'])


class DB(object):
    CREATE_TABLE = trim("""
        CREATE TABLE IF NOT EXISTS data (
              data_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            timestamp INTEGER,
                agent TEXT NOT NULL,
               metric TEXT NOT NULL,
                value REAL
        );
    """)

    def __init__(self, filename):
        self.logger = logging.getLogger("metzoo-db")
        self.filename = filename
        self.run(DB.CREATE_TABLE)


    INSERT = trim("""
        INSERT INTO data (timestamp, agent, metric, value)
        VALUES ({}, '{}', '{}', {})
    """)

    def save(self, timestamp, agent, metric, value):
        if not (type(timestamp) in [int, long]):
            raise ValueError("'timestamp' should be an integer")

        if type(agent) is not str:
            raise ValueError("'agent' should be a string")

        if type(metric) is not str:
            raise ValueError("'metric' should be a string")

        if not (type(value) in [int, long, float]):
            raise ValueError("'metric' should be a real number")

        self.run(DB.INSERT.format(timestamp, agent, metric, value))


    SELECT = trim("""
        SELECT data_id, timestamp, agent, metric, value
        FROM data
    """)

    def load(self):
        rows = self.select(DB.SELECT)
        return [MetzooData(row[0], row[1], row[2], row[3], row[4]) for row in rows]


    DELETE = trim("""
        DELETE FROM data
        WHERE data_id IS {}
    """)

    def delete(self, data_id):
        self.run(DB.DELETE.format(data_id))


    def run(self, query):
        self.logger.debug("run :: {}".format(query))
        try:
            connection = sqlite3.connect(self.filename)
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            connection.close()
        except Exception as e:
            self.logger.debug("  Exception: {}".format(e))
            raise e

    def select(self, query):
        self.logger.debug("select :: {}".format(query))
        try:
            connection = sqlite3.connect(self.filename)
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            connection.close()
        except Exception as e:
            self.logger.debug("  Exception: {}".format(e))
            raise e
        return result
