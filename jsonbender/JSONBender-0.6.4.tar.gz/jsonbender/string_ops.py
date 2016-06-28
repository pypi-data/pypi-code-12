from jsonbender.core import Bender, Transport
from jsonbender._compat import iteritems


class Format(Bender):
    """
    Return a formatted string just like `str.format()`.
    However, the values to be formatted are given by benders as positional or
    named parameters.

    `format_string` is a template with the same syntax as `str.format()`

    Example:
    ```
    fmt = Format('{} {} {last}', S('first'), S('second'), last=S('last'))
    source = {'first': 'Edsger', 'second': 'W.', 'last': 'Dijkstra'}
    fmt.execute(source)  # -> 'Edsger W. Dijkstra'
    ```
    """
    def __init__(self, format_string, *args, **kwargs):
        self._format_str = format_string
        self._positional_benders = args
        self._named_benders = kwargs

    def raw_execute(self, source):
        transport = Transport.from_source(source)
        args = [bender(source) for bender in self._positional_benders]
        kwargs = {k: bender(source)
                  for k, bender in iteritems(self._named_benders)}
        value = self._format_str.format(*args, **kwargs)
        return Transport(value, transport.context)

