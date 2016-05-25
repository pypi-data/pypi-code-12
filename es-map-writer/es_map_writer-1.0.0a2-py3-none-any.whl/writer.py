from .scanner import Scanner
from . import MAPPING_TEMPLATE, APP_DIR
import os


class Writer(object):

    def __init__(self, db_url):
        self.db_url = db_url

    def write_mapping(self, table_name, document_type, path=None, index_name=None):
        s = Scanner(self.db_url)
        fields = s.build_props(table_name)
        index = table_name if not index_name else index_name
        vals = {
            'map_name': index,
            'doc_type': document_type,
            'fields': fields
        }
        mapping = MAPPING_TEMPLATE % (vals)
        if not path:
            path = os.getcwd() + '/{}'.format(APP_DIR)
        path = path + '/{}_es_mapping.py'.format(table_name)
        with open(path, 'a') as f:
            f.write(mapping)
        return "Mapping written."
