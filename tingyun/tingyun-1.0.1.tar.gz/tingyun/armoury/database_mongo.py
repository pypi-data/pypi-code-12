"""the module wrapt main entrance

"""

import logging

from tingyun.armoury.ammunition.mongo_tracker import wrap_mongo_trace
from tingyun.armoury.ammunition.function_tracker import wrap_function_trace

console = logging.getLogger(__name__)
_methods = ['count', 'create_index', 'distinct', 'drop', 'drop_index', 'drop_indexes', 'ensure_index', 'find',
            'find_and_modify', 'find_one', 'group', 'index_information', 'inline_map_reduce', 'insert', 'map_reduce',
            'options', 'reindex', 'remove', 'rename', 'save', 'update']


def detect_connection(module):
    """
    :param module:
    :return:
    """
    if hasattr(module, "Connection"):
        wrap_function_trace(module, 'Connection.__init__', name='%s:Connection.__init__' % module.__name__)


def detect_mongo_client(module):
    """
    :param module:
    :return:
    """
    if hasattr(module, "MongoClient"):
        wrap_function_trace(module, "MongoClient.__init__", name="%s.MongoClient.__init__" % module.__name__)


def detect_collection(module):
    """
    :param module:
    :return:
    """
    def collection_name(collection, *args, **kwargs):
        """ we get the full name include the database name with dot separated
        :param collection:
        :param args:
        :param kwargs:
        :return:
        """
        return collection.full_name

    if not hasattr(module, "Collection"):
        console.info("module(%s) has not Collection object.", module)
        return

    for m in _methods:
        if not hasattr(module.Collection, m):
            console.info("Collection has not %s method", m)
            continue

        wrap_mongo_trace(module, "Collection.%s" % m, schema=collection_name, method=m)
