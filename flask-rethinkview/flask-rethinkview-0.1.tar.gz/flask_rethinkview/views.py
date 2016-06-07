from functools import wraps

import rethinkdb as r
from flask import current_app, g, request
from flask_classful import FlaskView
from functional import seq

from .response import bad_request, forbidden, not_found, ok
from .validator import ValidatorMixin


class RethinkDBMixin(object):
    _table_name = "data"
    _index_names = []

    @classmethod
    def init(cls):
        cls.create_table()
        cls.create_indices()

    @classmethod
    def create_table(cls):
        table_list = r.table_list().run(cls.get_conn())
        if cls._table_name not in table_list:
            r.table_create(cls._table_name).run(cls.get_conn())

    @classmethod
    def create_indices(cls):
        index_list = cls.get_table().index_list().run(cls.get_conn())
        seq(cls._index_names) \
            .filter(lambda name: name not in index_list) \
            .for_each(lambda name: cls.get_table().index_create(name).run(cls.get_conn()))
        cls.create_custom_indices()

    @classmethod
    def create_custom_indices(cls):
        pass

    @classmethod
    def get_conn(cls):
        return current_app.rethinkdb.conn

    @classmethod
    def get_table(cls):
        return r.table(cls._table_name)

    @classmethod
    def get_item(cls, _id):
        return cls.get_table().get(_id).run(cls.get_conn())


class RethinkDBView(FlaskView, RethinkDBMixin, ValidatorMixin):

    def index(self):
        reql = self.get_table()
        cur = reql.run(self.get_conn())
        return ok(list(cur))

    def get(self, _id):
        item = self.get_item(_id)
        if item:
            return ok(item)
        else:
            return not_found()

    def post(self):
        data = request.get_json(silent=True)
        if not self.validate(data):
            return bad_request("invalid_json")

        reql = self.get_table().insert(data)
        ret = reql.run(self.get_conn())
        return ok(ret)

    def put(self, _id):
        data = request.get_json()
        if not self.validate(data):
            return bad_request("invalid_json")

        data["id"] = _id
        reql = self.get_table().insert(data, conflict="replace")
        ret = reql.run(self.get_conn())

        return ok(ret)

    def delete(self, _id):
        reql = self.get_table().get(_id).delete()
        ret = reql.run(self.get_conn())
        return ok(ret)


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g._auth_id = request.headers.get("X-Analytica-User-ID")
        if g._auth_id is None:
            return bad_request("auth required")
        return f(*args, **kwargs)

    return decorated_function


class RethinkDBSecureView(FlaskView, RethinkDBMixin, ValidatorMixin):

    @classmethod
    def init(cls):
        super().init()
        if "_auth_id" not in cls.get_table().index_list().run(cls.get_conn()):
            cls.get_table().index_create("_auth_id").run(cls.get_conn())

    @auth_required
    def index(self):
        reql = self.get_table().get_all(g._auth_id, index="_auth_id")
        cur = reql.run(self.get_conn())
        return ok(list(cur))

    @auth_required
    def get(self, _id):
        item = self.get_item(_id)
        if item and item.get("_auth_id") == g._auth_id:
            return ok(item)
        else:
            return not_found()

    @auth_required
    def post(self):
        data = request.get_json()
        if not self.validate(data):
            return bad_request("invalid_json")

        data["_auth_id"] = g._auth_id
        reql = self.get_table().insert(data)
        ret = reql.run(self.get_conn())
        return ok(ret)

    @auth_required
    def put(self, _id):
        data = request.get_json()
        if not self.validate(data):
            return bad_request("invalid_json")

        item = self.get_item(_id)
        if item is None or item.get("_auth_id") == g._auth_id:
            data["_auth_id"] = g._auth_id
            data["id"] = _id
            reql = self.get_table().insert(data, conflict="replace")
            ret = reql.run(self.get_conn())
            return ok(ret)
        else:
            return forbidden()

    @auth_required
    def delete(self, _id):
        item = self.get_item(_id)
        if item and item.get("_auth_id") == g._auth_id:
            reql = self.get_table().get(_id).delete()
            ret = reql.run(self.get_conn())
            return ok(ret)
        else:
            return not_found()
