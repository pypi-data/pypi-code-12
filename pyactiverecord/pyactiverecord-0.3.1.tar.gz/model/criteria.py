import re
from model.database import Database as Database
from model.column import Column as Column
from model.type import Type as Type


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
                sql = "DROP TABLE IF EXISTS `" + Criteria.table_name(self) + "`;\n"
                cursor.execute(sql)

                sql = "create table `" + Criteria.table_name(self) + "` (\n"
                sql += "    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,\n"
                for k, v in Criteria.attributes(self._klass).items():
                    if k == "id":
                        continue
                    if v.type == Type.tinyint:
                        sql += "    `" + k + "` tinyint(4) DEFAULT NULL,\n"
                    elif v.type == Type.int:
                        sql += "    `" + k + "` int(11) DEFAULT NULL,\n"
                    elif v.type == Type.bigint:
                        sql += "    `" + k + "` bigint(20) DEFAULT NULL,\n"
                    elif v.type == Type.float:
                        sql += "    `" + k + "` float DEFAULT NULL,\n"
                    elif v.type == Type.double:
                        sql += "    `" + k + "` double DEFAULT NULL,\n"
                    elif v.type == Type.text:
                        sql += "    `" + k + "` text,\n"
                    elif v.type == Type.varchar:
                        sql += "    `" + k + "` varchar(" + str(v.length) + ") DEFAULT NULL,\n"
                    elif v.type == Type.date:
                        sql += "    `" + k + "` date NULL DEFAULT NULL,\n"
                    elif v.type == Type.datetime:
                        sql += "    `" + k + "` datetime NULL DEFAULT NULL,\n"
                    elif v.type == Type.timestamp:
                        sql += "    `" + k + "` timestamp NULL DEFAULT NULL,\n"
                    elif v.type == Type.time:
                        sql += "    `" + k + "` time NULL DEFAULT NULL,\n"
                sql += "    PRIMARY KEY (`id`)\n"
                sql += ") ENGINE=InnoDB DEFAULT CHARSET=utf8;\n"
                cursor.execute(sql)

                sql = "LOCK TABLES `" + Criteria.table_name(self) + "` WRITE;"
                cursor.execute(sql)
            finally:
                cursor.close()
        finally:
            connector.commit()
            connector.close()

    def query(self, where=[], order=[], limit=None):
        self.initialize()
        connector = None
        ret = None
        try:
            connector = Database.connector()
            cursor = connector.cursor()
            try:
                sql = "select * from " + Criteria.table_name(self)
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

                if limit is not None:
                    sql += " limit 0," + str(limit)

                sql += ";"
                cursor.execute(sql)
                ret = [dict(line) for line in [zip([column[0] for column in
                                                    cursor.description], row) for row in cursor.fetchall()]]
            finally:
                cursor.close()
                pass
        finally:
            connector.close()

        for r in ret:
            c = self._klass()
            for k, v in Criteria.attributes(self._klass).items():
                setattr(c, k, r[k])
            self._lst.append(c)

        return self

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
                sql = "show tables;"
                cursor.execute(sql)
                ret = [d[0] for d in cursor.fetchall()]
                if Criteria.table_name(self) not in ret:
                    flag = False
            except Exception as e:
                print('type:' + str(type(e)))
                print('args:' + str(e.args))
            finally:
                cursor.close()
        finally:
            connector.close()
            return flag

    def difference(self, attributes):
        diff = {}
        connector = None
        try:
            connector = Database.connector()
            cursor = connector.cursor()
            try:
                sql = "show columns from " + Criteria.table_name(self)
                cursor.execute(sql)
                ret = {d[0] for d in cursor.fetchall()}
                for a in attributes:
                    if a not in ret:
                        diff[a] = "new"
                for r in ret:
                    if r not in attributes:
                        diff[r] = "deleted"
            except Exception as e:
                print('type:' + str(type(e)))
                print('args:' + str(e.args))
            finally:
                cursor.close()
        finally:
            connector.close()
            return diff

    def add_column(self, name, column):
        connector = None
        try:
            connector = Database.connector()
            cursor = connector.cursor()
            try:
                sql = "alter table " + Criteria.table_name(self)
                if name == "id":
                    return
                elif column.type == Type.varchar:
                    sql += " add " + name + " " + column.type + "(" + str(column.length) + ")"
                else:
                    sql += " add " + name + " " + column.type
                cursor.execute(sql)
            finally:
                cursor.close()
        finally:
            connector.commit()
            connector.close()

    def delete_column(self, name):
        connector = None
        try:
            connector = Database.connector()
            cursor = connector.cursor()
            try:
                sql = "alter table " + Criteria.table_name(self) + " drop column " + name
                cursor.execute(sql)
            finally:
                cursor.close()
        finally:
            connector.commit()
            connector.close()

    @staticmethod
    def attributes(this):
        d = dict([(k, v) for k, v in this.__dict__.items() if v.__class__ is Column])
        if "id" not in d.keys():
            d["id"] = Column(type=Type.int)
        return d

    @staticmethod
    def table_name(this):
        return re.sub("([A-Z])", lambda x: "_" + x.group(1).lower(), this._klass.__name__)[1:]
