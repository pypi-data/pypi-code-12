import abc
from typing import Callable, Any
from functools import wraps

from tryp import List

from series.logging import Logging


def exclusive(f: Callable[..., Any]):
    @wraps(f)
    def wrapper(self: 'DbFacade', *a, **kw):
        with self.lock:
            return f(self, *a, **kw)
    return wrapper


def commit(f: Callable[..., Any]):
    @wraps(f)
    def wrapper(self: 'DbFacade', *a, **kw):
        value = f(self, *a, **kw)
        self._commit()
        return value
    return exclusive(wrapper)


class DbFacade(Logging, metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def main_type(self) -> type:
        ...

    def __init__(self, db):
        self._db = db

    @property
    def lock(self):
        return self._db.lock

    @exclusive
    def _commit(self):
        self._db.commit()
        self.log.debug('Committed transactions to db.')

    @property
    def all_query(self):
        return self._db.query(self.main_type).order_by(self.main_type.id)

    def filter_by(self, **filters):
        return self.all_query.filter_by(**filters)

    @property  # type: ignore
    @exclusive
    def all(self):
        return List.wrap(self.all_query.all())

    @exclusive
    def find_by_id(self, id):
        return self.filter_by(id=id).first()

__all__ = ('DbFacade', 'exclusive', 'commit')
