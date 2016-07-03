from sqlent.src.query import Query

class _BaseModel(object):
    pk = 'id'

    def __init__(self, d=None):
        if d is not None:
            self.set_from_dict(d)

    def set_from_dict(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)

    def outboundHasOne(self, ForeignModelClass, foreign_pk_name, this_fk_name):
        with self.__class__.connection.cursor() as cur:
            sql_statement = "SELECT * FROM {foreign_table_name} where {foreign_pk_name} = {this_fk_val};".format(
                foreign_table_name = ForeignModelClass.table_name,
                foreign_pk_name = foreign_pk_name,
                this_fk_val = getattr(self, this_fk_name))
            cur.execute(sql_statement)
            result = cur.fetchone()
            return ForeignModelClass(result)

    def inboundHasMany(self, ForeignModelClass, foreign_fk_name, this_pk_name):
        with self.__class__.connection.cursor() as cur:
            cur.execute(Query().select().table(ForeignModelClass.table_name).where_equal(foreign_fk_name, getattr(self, this_pk_name)).toString())
            results = cur.fetchall()
            return [ForeignModelClass(r) for r in results]

    @classmethod
    def all(cls):
        cur = cls.connection.cursor()
        cur.execute(Query().select().table(cls.table_name).to_string())
        results = cur.fetchall()
        cur.close()
        return [cls(r) for r in results]


def get_base_model(conn):
    class BaseModel(_BaseModel):
        pass
    BaseModel.connection = conn
    return BaseModel
