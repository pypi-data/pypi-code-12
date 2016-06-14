import re

from threading import RLock

from pymongo import MongoClient


__all__ = [
    'MongoClientPool',
    'KwargsqlToMongo',
]


class MongoClientPool(object):
    lock = RLock()
    connections = dict()

    @classmethod
    def get(cls, **kwargs):
        key = hash(frozenset(kwargs.items()))
        with cls.lock:
            con = cls.connections.get(key)
            if con is None:
                con = MongoClient(**kwargs)
                cls.connections[key] = con
        return con


class KwargsqlToMongo(object):
    """ Convert a kwargsql expression to PyMongo query dict.
    """
    KWARGQL_SUPPORTED_MONGO_OPS = {
        'ne', 'lt', 'ltw', 'gt', 'gte', 'in', 'nin', 'exists'
    }

    KWARGSQL_REGEX_OPS = dict(
        contains=dict(prefix='.*', suffix='.*'),
        icontains=dict(prefix='.*', suffix='.*', options='i'),
        startswith=dict(suffix='.*'),
        istartswith=dict(suffix='.*', options='i'),
        endswith=dict(prefix='.*'),
        iendswith=dict(prefix='.*', options='i'),
        iexact=dict(options='i'),
    )

    @classmethod
    def convert(cls, **kwargsql):
        """
        :param dict kwargsql:
          Kwargsql expression to convert

        :return:
          filter to be used in :py:method:`pymongo.collection.find`
        :rtype: dict
        """
        filters = []
        for k, v in kwargsql.items():
            terms = k.split('__')
            if terms[-1] in cls.KWARGQL_SUPPORTED_MONGO_OPS:
                v = {
                    '$' + terms[-1]: v
                }
                if terms[-1] == 'exists':
                    v['$exists'] = bool(v['$exists'])
                terms = terms[:-1]
            elif terms[-1] in cls.KWARGSQL_REGEX_OPS:
                config = cls.KWARGSQL_REGEX_OPS[terms[-1]]
                pattern = '^{prefix}{pattern}{suffix}$'.format(
                    prefix=config.get('prefix', ''),
                    pattern=re.escape(v),
                    suffix=config.get('suffix', '')
                )
                v = {
                    '$regex': pattern,
                    '$options': config.get('options', ''),
                }
                terms = terms[:-1]
            k = '.'.join(terms)
            filters.append({k: v})
        if len(filters) == 0:
            return {}
        if len(filters) == 1:
            return filters[0]
        else:
            return {
                '$and': filters
            }
