import pickle
import functools

from py4j.protocol import Py4JJavaError


# DB-API 2.0 Module Interface Exceptions
class Error(Exception):
    pass

class JavaError(Error):

    def __init__(self, java_exc, *args, **kwargs):
        super().__init__(java_exc.tb_stripped(), *args, **kwargs)
        self.java_exc = java_exc

class Warning(JavaError):
    pass

class InterfaceError(JavaError):
    pass

class DatabaseError(JavaError):
    pass

class InternalError(DatabaseError):
    pass

class OperationalError(DatabaseError):
    pass

class ProgrammingError(DatabaseError):
    pass

class IntegrityError(DatabaseError):
    pass

class DataError(DatabaseError):
    pass

class NotSupportedError(DatabaseError):
    pass


class CodeAggregatorMeta(type):
    exc_classes = None

    def __new__(meta, name, bases, nmspc):
         Cls = super().__new__(meta, name, bases, nmspc)
         meta.exc_classes[Cls.code] = Cls
         return Cls

