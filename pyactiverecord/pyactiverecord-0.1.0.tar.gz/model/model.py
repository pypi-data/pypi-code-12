from model.database import Database as Database
from model.locator import Locator as Locator
from model.column import Column as Column

class Model:
    id = Column(type="int")

    @property
    def attributes(self):
        return {k for k, v in self.__class__.__dict__.items() if v.__class__ == Column}

    def __new__(cls, *args, **kwargs):
        if not cls.is_exist_table():
            cls.create()
        return super().__new__(cls)

    def __init__(self):
        pass

    @classmethod
    def query(cls, where=[], order=[]):
        criteria = Locator.query(cls)
        return criteria.query(where, order)

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

    def save(self):
        connector = None
        try:
            connector = Database.connector()
            cursor = connector.cursor()
            try:
                sql = "insert into " + self.__class__.__name__.lower() + " ("
                for a in self.attributes:
                    sql += a + ","
                sql = sql[0:-1] + ") values("
                for a in self.attributes:
                    column = getattr(self, a)
                    if isinstance(getattr(self, a), int):
                        sql += str(column) + ","
                    else:
                        if column is not None:
                            sql += "\"" + str(column) + "\","
                        else:
                            sql += "\"\","
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
                sql = "delete from " + self.__class__.__name__.lower() + " where id = " + str(getattr(self, "id")) + ";"

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
