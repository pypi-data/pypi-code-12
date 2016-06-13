__author__ = 'zhonghong'

from zapi.core.utils import decorate_list

class Z_Model(object):

    def __getattr__(self, in_field):
        dynamic_properties = ["find_by_", "delete_by_"]
        query = None

        for idx, prop in enumerate(dynamic_properties):
            if in_field.startswith(prop):
                size_of_query = len(dynamic_properties[idx])
                field = in_field[size_of_query:]
                query = in_field[:size_of_query]
                break
        if query is None:
            raise AttributeError(in_field)
        dynamic_query = {
            "find_by_": lambda value: self._find(field, value, self.__tablename__),
            "delete_by_": lambda value: self._delete(field, value, self.__tablename__)
        }[query]
        return dynamic_query

    @decorate_list
    def _find(self, field, value, table):
        self.db.where(field, value)
        return self.db.get(table)

    def _delete(self, field, value, table):
        return self.db.delete(table, {field: value}, 1)

    def get_list(self, cols='*', where=None, like=None, group_by=None, order_by=None, limit=0):
        self.db.select(cols)
        if where:
            self.db.where(where)
        if like:
            self.db.like(like['field'], like['match'], like['side'])
        if group_by:
            self.db.group_by(group_by)
        if order_by:
            self.db.order_by(order_by['field'], order_by['direction'])
        return self.db.get(self.__tablename__)

    def create(self, **kwargs):
        _set = {}
        fields = self.get_fields()
        for field in kwargs.keys():
            if field in fields:
                _set[field] = kwargs[field]

        result = self.db.insert(self.__tablename__, _set)
        if result is False:
            return []
        key, value = _set.popitem()
        return getattr(self.db, 'find_by_%s' % key)(value, self.__tablename__)

    def create_multi(self, _set):
        result = self.db.insert_batch(self.__tablename__, _set)
        return result

    def update(self, _set, _where):
        result = self.db.update(self.__tablename__, _set, _where, 1)
        return result or None

    def get(self, id_):
        results = getattr(self.db, 'find_by_%s_id' % self.__tablename__)(id_, self.__tablename__)
        if results is False:
            results = getattr(self.db, 'find_by_id')(id_, self.__tablename__) or [{}]
        return results[0]

    def get_multi(self, ids):
        return [self.get(id_) for id_ in ids]

    def get_fields(self):
        return self.db.get_fields(self.__tablename__)

    @property
    def tablename(self):
        return self.__tablename__
