from functools import wraps
import re

from series.get.model.show import Show
from series import canonicalize
from series.get.tvdb import Tvdb

from tek import logger


class ShowsFacade(Tvdb):

    @property
    def lock(self):
        return self._db.lock

    def exclusive(func):
        @wraps(func)
        def wrapper(self, *a, **kw):
            return func(self, *a, **kw)
        return wrapper

    def commit(func):
        @wraps(func)
        def wrapper(self, *a, **kw):
            result = func(self, *a, **kw)
            self._db.commit()
            return result
        return wrapper

    def __init__(self, db):
        self._db = db

    @exclusive
    def name_exists(self, name):
        return self.query(canonical_name=canonicalize(name)).count() > 0

    def query(self, **filters):
        q = self._db.query(Show)
        return q.filter_by(**filters).order_by(Show.id)

    def id_param(self, showid):
        return (dict(etvdb_id=showid) if self.use_etvdb else
                dict(rage_id=showid))

    @exclusive
    def add(self, name, show):
        data = dict(
            name=show.name,
            canonical_name=canonicalize(name)
        )
        data.update(**self.id_param(show.showid))
        if show.latest_episode is not None:
            data.update(latest_episode=show.latest_episode.number,
                        latest_season=show.latest_episode.season)
        self._db.add(Show(**data))

    @exclusive
    @commit
    def update(self, id_, data):
        query = self.query(id=id_)
        if query.count() > 0:
            show = query.first()
            for key, value in data.items():
                setattr(show, key, value)
            return show
        else:
            logger.debug(
                'Tried to update nonexistent show with id {}'.format(id_)
            )

    @exclusive
    @commit
    def delete_by_sid(self, showid):
        query = self.query(**self.id_param(showid))
        if query.count() > 0:
            show = query.first()
            self._db.delete(show)
        else:
            logger.debug(
                'Tried to delete nonexistent show with id {}'.format(showid)
            )

    @exclusive
    @commit
    def delete(self, showid):
        query = self.query(id=showid)
        if query.count() > 0:
            show = query.first()
            self._db.delete(show)
        else:
            logger.debug(
                'Tried to delete nonexistent show with id {}'.format(showid)
            )

    @property
    @exclusive
    def all(self):
        return self.query().all()

    def filter_by_regex(self, regex):
        r = re.compile(regex)
        return filter(lambda s: r.search(s.canonical_name), self.all)

__all__ = ['ShowsFacade']
