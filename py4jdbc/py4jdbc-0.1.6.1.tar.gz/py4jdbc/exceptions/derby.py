from collections import ChainMap

from py4jdbc.exceptions import dbapi2
from py4jdbc.exceptions import sqlstate


exc_classes = ChainMap(sqlstate.exc_classes).new_child()


class _DerbyCodeAgg(dbapi2.CodeAggregatorMeta):
    exc_classes = exc_classes


class ExecutionError(dbapi2.DatabaseError, metaclass=_DerbyCodeAgg):
    code = 'F0'
