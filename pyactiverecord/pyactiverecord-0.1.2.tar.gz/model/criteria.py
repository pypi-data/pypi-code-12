import copy

from model.database import Database as Database
from model.column import Column as Column


class Criteria(object):
    def __init__(self, klass):
        self._klass = klass
        self._lst = []
        self._i = 0

    def initialize(self):
        self._lst = []
        self._i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == len(self._lst):
            raise StopIteration()
        value = self._lst[self._i]
        self._i += 1
        return value

    def create(self):
        self.initialize()
        connector = None
        try:
            connector = Database.connector()
            cursor = connector.cursor()
            try:
                sql = "DROP TABLE IF EXISTS `" + self._klass.__name__.lower() + "`;\n"
                cursor.execute(sql)

                sql = "create table `" + self._klass.__name__.lower() + "` (\n"
                sql += "    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,\n"
                for k, v in self._klass.__dict__.items():
                    if v.__class__ == Column:
                        if v.type == "int":
                            sql += "    `" + k + "` int(11) DEFAULT NULL,\n"
                        elif v.type == "text":
                            sql += "    `" + k + "` text,\n"
                        elif v.type == "varchar":
                            sql += "    `" + k + "` varchar(" + str(v.length) + ") DEFAULT NULL,\n"
                        elif v.type == "timestamp":
                            sql += "    `" + k + "` timestamp NULL DEFAULT NULL,\n"
                        else:
                            print("error: invalid field type `" + v.type + "`")
                sql += "    PRIMARY KEY (`id`)\n"
                sql += ") ENGINE=InnoDB DEFAULT CHARSET=utf8;\n"
                cursor.execute(sql)

                sql = "LOCK TABLES `" + self._klass.__name__.lower() + "` WRITE;"
                cursor.execute(sql)
            finally:
                cursor.close()
        finally:
            connector.commit()
            connector.close()

    def query(self, where, order):
        self.initialize()
        connector = None
        ret = None
        try:
            connector = Database.connector()
            cursor = connector.cursor()
            try:
                sql = "select * from " + self._klass.__name__.lower()
                if len(where) > 0:
                    sql += " where"
                    for i, v in enumerate(where):
                        if i > 0:
                            sql += " and"
                        sql += " " + v

                if len(order) > 0:
                    sql += " order by"
                    for v in order:
                        sql += " " + v

                sql += ";"
                cursor.execute(sql)
                ret = [dict(line) for line in [zip([column[0] for column in
                                                    cursor.description], row) for row in cursor.fetchall()]]
            finally:
                cursor.close()
                pass
        finally:
            connector.close()

        self._lst = self.recursive(ret, self._lst)
        return self

    def recursive(self, ret=[], lst=[]):
        if len(ret) == 0:
            return lst
        else:
            r = ret.pop()
            c = self._klass()
            for k, v in c.__class__.__dict__.items():
                if v.__class__ is not Column:
                    continue
                setattr(c, k, r[k])
            lst.append(c)
            return self.recursive(ret, lst)

    def where(self):
        return self

    def all(self):
        return self

    def first(self):
        return self._lst[0] if len(self._lst) > 0 else None

    def size(self):
        return len(self._lst)

    def is_exist_table(self):
        flag = True
        connector = None
        try:
            connector = Database.connector()
            cursor = connector.cursor()
            try:
                sql = "SHOW TABLES;"
                cursor.execute(sql)
                ret = [d[0] for d in cursor.fetchall()]
                if not self._klass.__name__.lower() in ret:
                    flag = False
            except Exception as e:
                print('type:' + str(type(e)))
                print('args:' + str(e.args))
            finally:
                cursor.close()
        finally:
            connector.close()
            return flag
