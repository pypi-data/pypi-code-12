from __future__ import print_function
from contextlib import contextmanager
import sys
import traceback

__version__ = '1.3'

class DebugContext(object):
    def __init__(self, fields):
        self._fields = fields
        for field in fields:
            setattr(self, field, None)

    def _to_prose(self):
        prose = ', '.join(
            field + ' ' + repr(getattr(self, field))
            for field in self._fields
            if getattr(self, field) is not None
        )
        if prose == "": # all fields are None
            prose = "(null state)"
        return prose

    def __setattr__(self, key, value):
        if not key.startswith('_') and key not in self._fields:
            raise RuntimeError("Tried to set non existent field in "
                               "DebugContext: %s" % key)

        object.__setattr__(self, key, value)

def print_tb(context, tb_info):
    """
    Default print traceback function. Prints the traceback, then the context.
    """
    traceback.print_exception(*tb_info)
    print('The exception was caught on %s.' % context._to_prose(),
          file=sys.stderr)

@contextmanager
def contextualized_tracebacks(fields, print_tb=print_tb):
    """
    Creates and returns a new DebugContext.

    When used within a ``with`` block, it will catch any unhandled exception
    and call ``print_tb``, which will print both the debug context and the
    traceback.

    The argument ``fields`` is required and must contain a list of the valid
    field names that may be used in the context. Any field may have a value of
    None, but assigning to non-existent fields will raise a RuntimeError.

    In the default ``print_fn`` function, context fields will be print in the
    same order they are specified here.
    """
    context = DebugContext(fields)
    try:
        yield context
    except SystemExit as ex:
        # Don't catch SystemExit
        raise ex
    except:
        _type, _value, _traceback = sys.exc_info()
        # remove the outermost call, that corresponds to "yield context" inside
        # this function.
        _traceback = _traceback.tb_next

        # Print the traceback
        print_tb(context, (_type, _value, _traceback))
        del _traceback
