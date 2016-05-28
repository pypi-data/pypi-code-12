import re
import threading
from functools import wraps

from tek.tools import find
from tek import logger

from series.get.model.release import ReleaseFactory, ReleaseMonitor, Release


class ReleasesFacade(object):

    @property
    def lock(self):
        return self._db.lock

    def exclusive(func):
        @wraps(func)
        def wrapper(self, *a, **kw):
            return func(self, *a, **kw)
        return wrapper

    def __init__(self, db, sync=False):
        self._db = db
        self._sync = sync
        self._releases = None
        self._need_commit = False
        self._additions = []
        self._deletions = []
        self._link_additions = []
        self._release_lock = threading.Event()
        self._release_lock.set()

    def check_commit(self):
        if self._additions:
            self._flush_additions()
        if self._deletions:
            self._flush_deletions()
        if self._link_additions:
            self._flush_links()
        if self._need_commit:
            self._xcommit()
            self._need_commit = False
            self._release_lock.set()

    @exclusive
    def _xcommit(self):
        self._db.commit()
        logger.debug('Committed transactions to db.')

    def commit(self):
        self._need_commit = True
        if self._sync:
            self.check_commit()

    def query(self, **filters):
        q = self._db.query(ReleaseMonitor)
        return q.filter_by(**filters).order_by(ReleaseMonitor.id)

    def query_release(self, order=True, **filters):
        q = self._db.query(Release)
        if order:
            q = q.order_by(Release.id)
        return q.filter_by(**filters)

    @property
    def all(self):
        return self._protected_releases()

    @exclusive
    def _protected_releases(self, wait=True):
        if self._releases is None:
            self._releases = self.query().all()
        if wait:
            self._release_lock.wait(timeout=2)
        return self._releases

    def _filter(self, matcher):
        return [r for r in self.all if matcher(r)]

    def _find(self, matcher):
        return find(matcher, self.all)

    def find_by_id(self, _id):
        return self._find(lambda r: r.id == _id)

    def find_by_metadata(self, series=None, season=None, episode=None):
        def matcher(monitor):
            release = monitor.release
            return (
                (not(series) or release.name == series) and
                (not(season) or int(release.season) == int(season)) and
                (not(episode) or int(release.episode) == int(episode))
            )
        return self._find(matcher)

    def filter_episode_repr(self, regex):
        rex = re.compile(regex, re.I)
        matcher = lambda m: rex.search(str(m.release))
        return list(self._filter(matcher))

    def __getitem__(self, slice):
        return self.all[slice]

    def _schedule(self):
        self._release_lock.clear()
        if self._sync:
            self.check_commit()

    def create(self, series, season, episode, airdate=None):
        fact = ReleaseFactory()
        enum = '{:0>2}x{:0>2}'.format(season, episode)
        title = '{}_{}'.format(series, enum)
        release = fact(title, series, '', '', enum=enum, res='720p')
        if airdate:
            release.airdate = airdate
        monitor = fact.monitor(release, [])
        self.add(monitor)

    def delete(self, series, season, episode):
        release = self.find_by_metadata(series, season, episode)
        if release:
            self._schedule_deletion(release)

    def update(self, series, season, episode, data):
        release = self.find_by_metadata(series, season, episode)
        if release:
            for key, value in data.items():
                setattr(release, key, value)
        self.commit()
        return release

    def update_by_id(self, _id, data):
        release = self.find_by_id(_id)
        if release:
            for key, value in data.items():
                setattr(release, key, value)
            self.commit()
            return release.info

    def _schedule_deletion(self, release):
        self._deletions.append(release)
        self._schedule()

    def _flush_deletions(self):
        for release in self._deletions:
            self._db.session.delete_then_commit(release)
            self._protected_releases(wait=False).remove(release)
        self._deletions = []
        self.commit()

    @property
    def pending_downloads(self):
        qualify = lambda r: not r.downloaded and not r.nuked
        return list(filter(qualify, self.all))

    def add_link_by_id(self, _id, url):
        release = self.find_by_id(_id)
        if release:
            self.add_link(release, url)
            return True

    def add_links_from_feed_entry(self, release, feed_entry):
        new = [l for l in feed_entry.links if not release.has_url(l)]
        if new:
            self._schedule_links(release, new)
            text = 'Added new links to release {}: {}'
            logger.info(text.format(release.release, ', '.join(new)))

    def add_link(self, release, url):
        if release.has_url(url):
            text = 'Release {rel} already contains link "{link}"'
        else:
            self._schedule_links(release, [url])
            text = 'Adding link "{link}" to release {rel}'
        logger.info(text.format(link=url, rel=release.release))

    def _schedule_links(self, release, urls):
        self._link_additions.append([release, urls])
        self._schedule()

    def _flush_links(self):
        for release, urls in self._link_additions:
            release.add_links(urls)
        self._link_additions = []
        self.commit()

    @property
    def count(self):
        return len(self.all)

    @property
    def downloadable(self):
        return self.download_candidates(extra=lambda r: r.downloadable)

    def download_candidates(self, extra=lambda r: True):
        def matcher(release):
            return not (
                release.downloaded or
                release.nuked or
                release.archived or
                release.downloading
            ) and extra(release)
        return self._filter(matcher)

    def add(self, release):
        self._schedule_addition(release)

    def add_season(self, name, season, count):
        for episode in range(1, count + 1):
            if not self._release_exists(name, season, episode):
                self.create(name, season, episode)

    def _release_exists(self, name, season, episode):
        return (self.query_release(name=name, season=season,
                                   episode=episode).count() > 0)

    def _schedule_addition(self, release):
        self._additions.append(release)
        self._schedule()

    def _flush_additions(self):
        for release in self._additions:
            self._protected_releases(wait=False).append(release)
            self._db.session.add_then_commit(release)
        self._additions = []
        self.commit()

    def reset(self):
        self._releases = None

    def mark_episode_downloaded(self, monitor):
        self._mark_episode(monitor, 'downloaded')

    def mark_episode_archived(self, monitor):
        self._mark_episode(monitor, 'archived')

    def _mark_episode(self, monitor, attr):
        matcher = lambda m: m.is_same_episode(monitor)
        for other in self._filter(matcher):
            other.downloaded = True
            setattr(other, attr, True)

    def latest_for_season(self, name, season):
        q = self.query_release(name=name, season=season, order=False)
        return q.order_by(Release.episode.desc()).first()

    def one(self, name, season, episode):
        rel = self.query_release(name=name, season=season,
                                 episode=episode).first()
        if rel:
            return self.query(release_id = rel.id).first()


__all__ = ['ReleasesFacade']
