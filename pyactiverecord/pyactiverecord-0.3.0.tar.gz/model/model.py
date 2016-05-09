import re

from model.database import Database as Database
from model.locator import Locator as Locator
from model.column import Column as Column
from model.type import Type as Type


class Model:
    id = Column(type=Type.int)

    def __new__(cls, *args, **kwargs):
        if not cls.is_exist_table():
            cls.create()
        else:
            attributes = Model.attributes(cls)
            diff = cls.difference(attributes)
            if diff is not None:
                for k, v in diff.items():
                    if v == "new":
                        column = getattr(cls, k)
                        cls.add_column(k, column)
                    elif v == "deleted":
                        cls.delete_column(k)
        return super().__new__(cls)

    def __init__(self):
        pass

    @classmethod
    def query(cls, where=[], order=[], limit=None):
        criteria = Locator.query(cls)
        return criteria.query(where, order, limit)

    @classmethod
    def all(cls):
        criteria = Locator.query(cls)
        return criteria.all()

    @classmethod
    def size(cls):
        criteria = Locator.query(cls)
        return criteria.size()

    @classmethod
    def create(cls):
        criteria = Locator.query(cls)
        return criteria.create()

    @classmethod
    def remove(cls):
        pass

    @classmethod
    def is_exist_table(cls):
        criteria = Locator.query(cls)
        return criteria.is_exist_table()

    @classmethod
    def difference(cls, attributes):
        criteria = Locator.query(cls)
        return criteria.difference(attributes)

    @classmethod
    def add_column(cls, name, column):
        criteria = Locator.query(cls)
        return criteria.add_column(name, column)

    @classmethod
    def delete_column(cls, name):
        criteria = Locator.query(cls)
        return criteria.delete_column(name)

    def save(self):
        connector = None
        try:
            connector = Database.connector()
            cursor = connector.cursor()
            try:
                sql = "insert into " + Model.table_name(self) + " ("
                for k, v in Model.attributes(self).items():
                    if k == "id" and v.__class__ is Column:
                        continue
                    sql += k + ","
                sql = sql[0:-1] + ") values("
                for k, v in Model.attributes(self).items():
                    if k == "id" and v.__class__ is Column:
                        continue
                    value = getattr(self, k)
                    if isinstance(getattr(self, k), int):
                        sql += str(value) + ","
                    else:
                        if value is not None and value.__class__ is not Column:
                            sql += "\"" + str(value) + "\","
                        else:
                            sql += "null,"
                sql = sql[0:-1] + ")"
                cursor.execute(sql)
                connector.commit()
                pass
            except Exception as e:
                print('type:' + str(type(e)))
                print('args:' + str(e.args))
            finally:
                cursor.close()
        finally:
            connector.close()

    def delete(self):
        connector = None
        try:
            connector = Database.connector()
            cursor = connector.cursor()
            try:
                sql = "delete from " + Model.table_name(self) + " where id = " + str(getattr(self, "id")) + ";"

                cursor.execute(sql)
                connector.commit()
                pass
            except Exception as e:
                print('type:' + str(type(e)))
                print('args:' + str(e.args))
            finally:
                cursor.close()
        finally:
            connector.close()

    @staticmethod
    def attributes(this):
        d = {}
        if isinstance(this, object.__class__):
            d = dict([(k, v) for k, v in this.__dict__.items() if v.__class__ == Column])
        else:
            d = dict([(k, v) for k, v in this.__class__.__dict__.items() if v.__class__ == Column])
        if "id" not in d.keys():
            d["id"] = Column(type=Type.int)
        return d

    @staticmethod
    def table_name(this):
        return re.sub("([A-Z])", lambda x: "_" + x.group(1).lower(), this.__class__.__name__)[1:]