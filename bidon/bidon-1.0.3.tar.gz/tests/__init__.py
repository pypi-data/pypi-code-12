import os
from collections import namedtuple

from bidon.configuration import Configuration
from bidon.db.access import DataAccess, ModelAccess


CONFIG = Configuration(core=None, test_rowcount=False, test_callproc=False, is_pg=False)
TEST_ROOT = os.path.dirname(os.path.abspath(__file__))


def configure(args):
  database = args.database
  if database == "postgres":
    configure_postgres(args)
  elif database == "mysql":
    configure_mysql(args)
  elif database == "sqlite":
    configure_sqlite(args)


def configure_postgres(args):
  from psycopg2.extras import Json
  from psycopg2.extensions import register_adapter

  from bidon.db.core import get_pg_core

  port = args.port or 5432

  CONFIG.update(core=get_pg_core("dbname=bidon_test user=postgres host=localhost port={}".format(port)),
                test_rowcount=True,
                test_callproc=True,
                is_pg=True)
  CONFIG.freeze()

  register_adapter(dict, lambda d: Json(d))


def configure_mysql(args):
  from pymysql.cursors import Cursor

  from bidon.db.core import get_mysql_core

  class NamedTupleCursorMixin(object):
    def _do_get_result(self):
      super(NamedTupleCursorMixin, self)._do_get_result()
      if self.description:
        fields = [f.name for f in self._result.fields]
        Row = namedtuple("Row", fields)
        self._rows = [Row(*row) for row in self._rows]

  class NamedTupleCursor(NamedTupleCursorMixin, Cursor):
    pass

  defaults_file = os.path.join(os.path.expanduser("~"), ".mysql-defaults/localhost")
  CONFIG.update(core=et_mysql_core(dict(read_default_file=defaults_file, database="bidon_test"),
                                   cursor_factory=NamedTupleCursor),
                test_rowcount=True,
                test_callproc=True)
  CONFIG.freeze()


def configure_sqlite(args):
  from bidon.db.core import get_sqlite_core

  def get_namedtuple_factory():
    fields = []
    Row = None
    def namedtuple_factory(cursor, row):
      nonlocal fields, Row
      _fields = [col[0] for col in cursor.description]
      if _fields != fields:
        fields = _fields
        Row = namedtuple("Row", fields)
      return Row(*row)
    return namedtuple_factory

  CONFIG.update(core=get_sqlite_core("tests/fixtures/test.sqlite3",
                                     cursor_factory=get_namedtuple_factory()),
                test_rowcount=False,
                test_callproc=False)
  CONFIG.freeze()


def get_data_access():
  return DataAccess(CONFIG.core)


def get_model_access():
  return ModelAccess(CONFIG.core)


from .db import *
from .util import *
from .spreadsheet import *
from .xml import XMLStreamWriterTestCase
from .test_configuration import ConfigurationTestCase
from .test_data_table import DataTableTestCase
from .test_field_mapping import FieldMappingTestCase
from .test_json_patch import JSONPatchTestCase
