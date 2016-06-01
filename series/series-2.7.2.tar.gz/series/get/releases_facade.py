from typing import Callable, Any
import re
from functools import wraps

from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.elements import not_

from tryp import List, Maybe, _, __
from series.logging import Logging

from series.get.model.release import ReleaseFactory, ReleaseMonitor, Release
from series.get.model.link import Link


def exclusive(f: Callable[..., Any]):
    @wraps(f)
    def wrapper(self, *a, **kw):
        with self.lock:
            return f(self, *a, **kw)
    return wrapper


def commit(f: Callable[..., Any]):
    @wraps(f)
    def wrapper(self, *a, **kw):
        value = f(self, *a, **kw)
        self._commit()
        return value
    return exclusive(wrapper)


class ReleasesFacade(Logging):

    @property
    def lock(self):
        return self._db.lock

    def __init__(self, db, sync=False):
        self._db = db
        self._releases = None

    @exclusive
    def _commit(self):
        self._db.commit()
        self.log.debug('Committed transactions to db.')

    @property
    def monitors(self):
        return self._db.query(ReleaseMonitor)

    def filter_by(self, **filters):
        return self.monitors.filter_by(**filters).order_by(ReleaseMonitor.id)

    def filter_release(self, *filters):
        return (self.monitors
                .join(Release)
                .filter(*filters)
                .order_by(ReleaseMonitor.id))

    def filter_by_release(self, **filters):
        return (self.monitors
                .join(Release)
                .filter_by(**filters)
                .order_by(ReleaseMonitor.id))

    def query_release(self, order=True, **filters):
        q = self._db.query(Release)
        if order:
            q = q.order_by(Release.id)
        return q.filter_by(**filters)

    @property  # type: ignore
    @exclusive
    def all(self):
        return List.wrap(self.monitors.all())

    @exclusive
    def find_by_id(self, id):
        return self._db.query(ReleaseMonitor).filter_by(id=id).first()

    def filter_by_metadata(self, series=None, season=None, episode=None):
        filters = List(
            Maybe(series) / (lambda a: Release.name == a),
            Maybe(season) / str / (lambda a: Release.season == a),
            Maybe(episode) / str / (lambda a: Release.episode == a),
        )
        return self.filter_release(*filters.flatten)

    @exclusive
    def find_by_metadata(self, series=None, season=None, episode=None):
        return self.filter_by_metadata(series, season, episode).first()

    def filter_episode_repr(self, regex):
        rex = re.compile(regex, re.I)
        matcher = lambda m: rex.search(str(m.release))
        return self.all.filter(matcher)

    def __getitem__(self, slice):
        return self.all[slice]

    def create(self, series, season, episode, airdate=None):
        fact = ReleaseFactory()
        enum = '{:0>2}x{:0>2}'.format(season, episode)
        title = '{}_{}'.format(series, enum)
        release = fact(title, series, '', '', enum=enum)
        if airdate:
            release.airdate = airdate
        monitor = fact.monitor(release, [])
        self.add(monitor)
        return monitor

    def delete(self, series, season, episode):
        self._delete(self.find_by_metadata(series, season, episode))

    @exclusive
    def _delete(self, record):
        if record:
            self._db.session.delete_then_commit(record)

    @commit
    def _update(self, record, data):
        if record:
            for key, value in data.items():
                setattr(record, key, value)
        return record

    def update(self, series, season, episode, data):
        release = self.find_by_metadata(series, season, episode)
        return self._update(release, data)

    def update_by_id(self, _id, **data):
        release = self.find_by_id(_id)
        return self._update(release, data)

    def update_link(self, _id, data):
        link = self.find_link_by_id(_id)
        return self._update(link, data)

    @property
    def pending_downloads(self):
        qualify = lambda r: not r.downloaded and not r.nuked
        return list(filter(qualify, self.all))

    def add_link_by_id(self, _id, url):
        release = self.find_by_id(_id)
        if release:
            self._add_links(release, List(url))
            return True

    @commit
    def _add_links(self, release, urls):
        release.add_links(urls)

    def add_links_from_feed_entry(self, release, feed_entry):
        new = [l for l in feed_entry.links if not release.has_url(l)]
        if new:
            self._add_links(release, new)
            text = 'Added new links to release {}: {}'
            self.log.info(text.format(release.release, ', '.join(new)))

    def add_link(self, release, url):
        if release.has_url(url):
            text = 'Release {rel} already contains link "{link}"'
        else:
            self._add_links(release, List(url))
            text = 'Adding link "{link}" to release {rel}'
        self.log.info(text.format(link=url, rel=release.release))

    @property  # type: ignore
    @exclusive
    def count(self):
        return self.monitors.count()

    @property  # type: ignore
    @exclusive
    def downloadable(self):
        return List.wrap(self.download_candidates.all()).filter(_.downloadable)

    @property
    def download_candidates(self):
        return self._db\
            .query(ReleaseMonitor)\
            .filter(not_(or_(ReleaseMonitor.downloaded, ReleaseMonitor.nuked,
                         ReleaseMonitor.archived, ReleaseMonitor.downloading)))

    @commit
    def add(self, release):
        self._db.session.add_then_commit(release)

    def add_season(self, name, season, count):
        for episode in range(1, count + 1):
            if not self._release_exists(name, season, episode):
                self.create(name, season, episode)

    def _release_exists(self, name, season, episode):
        return (self.query_release(name=name, season=season,
                                   episode=episode).count() > 0)

    def mark_episode_downloaded(self, monitor):
        self._mark_episode(monitor, 'downloaded')

    def mark_episode_archived(self, monitor):
        self._mark_episode(monitor, 'archived')

    @commit
    def _mark_episode(self, monitor, attr):
        r = self.query_release(id=monitor.release_id).first()
        if r:
            matches = self.filter_by_release(name=r.name, season=r.season,
                                             episode=r.episode)
        for m in matches:
            setattr(m, attr, True)

    def latest_for_season(self, name, season):
        q = self.query_release(name=name, season=season, order=False)
        return q.order_by(Release.episode.desc()).first()

    def one(self, name, season, episode):
        rel = self.query_release(name=name, season=season,
                                 episode=episode).first()
        if rel:
            return self.filter_by(release_id=rel.id).first()

    @exclusive
    def reset_torrent(self, id):
        release = self.filter_by(id=id).first()
        if release:
            self._reset_torrent(release)

    @commit
    def _reset_torrent(self, release):
        for link in release.links.all():
            link.dead = True
        release.downloaded = False
        release.archived = False
        release.last_torrent_search_stamp = 0

    def link_by_id(self, id):
        return Maybe(self._db.query(Link).filter_by(id=id).first())

    @commit
    def torrent_cached(self, id):
        def set(l):
            l.cached = True
        self.link_by_id(id).foreach(set)

    def fail_link(self, id):
        self.link_by_id(id).foreach(__.check_failed())

__all__ = ('ReleasesFacade',)
