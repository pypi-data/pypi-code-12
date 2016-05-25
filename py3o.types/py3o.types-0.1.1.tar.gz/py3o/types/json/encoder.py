# -*- encoding: utf-8 -*-

import datetime
import json
import six

from py3o.types import Py3oInteger


class Py3oJSONEncoder(json.JSONEncoder):
    """A JSON encoder intended to be used alongside :class:`.Py3oJSONDecoder`.

    .. seealso:: :class:`json.JSONEncoder`
    """

    def iterencode(self, o, _one_shot=False):

        # In Python 2, JSONEncoder uses str to encode ANY integer, even from
        # subclasses. We have to hack around this by temporarily replacing our
        # custom __str__ method with the int type's __repr__.
        if six.PY2:  # pragma: no cover
            old_str_method = Py3oInteger.__str__
            Py3oInteger.__str__ = int.__repr__

        try:
            res = super(Py3oJSONEncoder, self).iterencode(
                o, _one_shot=_one_shot
            )
        finally:
            if six.PY2:  # pragma: no cover
                Py3oInteger.__str__ = old_str_method

        return res

    def default(self, o):
        if isinstance(o, datetime.datetime):
            res = {'_py3o': 'dt', 'val': o.strftime('%Y%m%d%H%M%S')}
        elif isinstance(o, datetime.date):
            res = {'_py3o': 'date', 'val': o.strftime('%Y%m%d')}
        elif isinstance(o, datetime.time):
            res = {'_py3o': 'time', 'val': o.strftime('%H%M%S')}
        else:
            res = super(Py3oJSONEncoder, self).default(o)
        return res
