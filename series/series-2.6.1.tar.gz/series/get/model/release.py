from datetime import datetime
import re

from sqlpharmacy.core import Database

from sqlalchemy import Column, String, Integer, Boolean

from toolz import merge

from tek.tools import camelcaseify, unix_to_datetime, find, datetime_to_unix
from tek.util.decorator import generated_list
from tek.config import configurable
from tek.errors import ParseError
from tek import logger

from tryp.lazy import lazy
from tryp import List

from series import episode_enumeration, make_series_name, is_date_enum
from series.get.model.link import Link, HttpLink, TorrentLink
from series.etvdb import ETVDBFacade


class Release(object, metaclass=Database.DefaultMeta):
    title = Column(String)
    name = Column(String)
    group = Column(String)
    season = Column(Integer)
    episode = Column(Integer)
    is_series = Column(Boolean)
    resolution = Column(String)
    is_fix = Column(Boolean)
    airdate_stamp = Column(Integer)

    @property
    def is_hd(self):
        return self.resolution in ['720p', '1080p']

    @property
    def hd_series(self):
        return self.is_series and self.is_hd

    def __repr__(self):
        from tek.tools import repr_params
        params = repr_params(self.title, self.name, self.group,
                             (self.season, self.episode), self.is_series,
                             self.resolution)
        return '{}{}'.format(self.__class__.__name__, params)

    def __str__(self):
        return '{} {}x{}'.format(
            camelcaseify(self.name, sep=' '), self.season, self.episode,
        )

    def __eq__(self, other):
        return self.is_same_release(other)

    def is_same_episode(self, other):
        return (isinstance(other, Release) and self.name == other.name and
                self.season == other.season and self.episode == other.episode)

    def is_same_release(self, other):
        return self.is_same_episode(other) and self.group == other.group

    @property
    def search_string(self):
        return self.search_string_with_res(self.resolution)

    def search_string_with_res(self, resolution):
        sep = '[._ -]+'
        name = sep.join(self.name.replace('\'', '').split('_'))
        enum_format = lambda n: ('0?{}' if n < 10 else '{}').format(n)
        enum = '{}s?{}e?{}'.format(sep, enum_format(self.season),
                                   enum_format(self.episode))
        res = '.*{}'.format(resolution) if resolution else ''
        return '{}{}{}'.format(name, enum, res)

    @property
    def date_search_string(self):
        zeropad = lambda i: ('0?' if len(str(i)) == 1 else '') + str(i)
        sep = '[._ -]+'
        name = sep.join(self.name.split('_'))
        enum = sep.join(map(zeropad, self.airdate.timetuple()[:3]))
        res = '.*{}'.format(self.resolution) if self.resolution else ''
        return '{}{}{}{}'.format(name, sep, enum, res)

    @property
    def info(self):
        return dict(
            series=self.name,
            season=self.season,
            episode=self.episode,
            group=self.group,
        )

    @property
    def enum(self):
        return (self.season, self.episode)

    @property
    def airdate(self):
        return unix_to_datetime(self.airdate_stamp or 0)

    @airdate.setter
    def airdate(self, date):
        self.airdate_stamp = datetime_to_unix(date)

    @property
    def has_airdate(self):
        return self.airdate_stamp is not None


@configurable(get=['subtitle_retry_coefficient', 'prefer_hosters',
                   'only_torrent'])
@Database.foreign_key(Release)
@Database.foreign_key('ReleaseMonitor', ref_name='_fix', backref_name='_nuke')
class ReleaseMonitor(object, metaclass=Database.DefaultMeta):
    downloaded = Column(Boolean)
    download_path = Column(String)
    archived = Column(Boolean)
    nuked = Column(Boolean)
    watched = Column(Boolean)
    unknown = Column(Boolean)
    archiver_error = Column(Boolean)
    failed_downloads = Column(Integer)
    downloading = Column(Boolean)
    subtitles_downloaded = Column(Boolean)
    subtitle_failures = Column(Integer)
    last_subtitle_failure = Column(Integer)
    added_to_library = Column(Boolean)
    last_torrent_search_stamp = Column(Integer)
    _resolutions = Column(String)

    def __init__(self, release, **kw):
        super().__init__(**kw)
        self.release = release

    @property
    def resolutions(self):
        if self._resolutions is None:
            if self.release.resolution is None:
                return List('')
            else:
                return List(self.release.resolution)
        else:
            return List.wrap(self._resolutions.split(','))

    @resolutions.setter
    def resolutions(self, res):
        if isinstance(res, str):
            self._resolutions = res
        else:
            self._resolutions = ','.join(res)

    @property
    def enum(self):
        return self.release.enum

    def nuke(self, fix):
        self.nuked = True
        self._fix = fix

    @property
    def http_links(self):
        return [l for l in self.links if isinstance(l, HttpLink)]

    @property
    def link(self):
        links = self.fewest_failures
        if links:
            preferred = [l for l in links if l.domain in self._prefer_hosters]
            return preferred[0] if preferred else links[0]

    @property
    def fewest_failures(self):
        links = self.allowed_links
        best = min([l.failures for l in links] or [0])
        return [l for l in links if l.failures == best]

    @property
    def allowed_links(self):
        return (self.good_links or ([] if self._only_torrent else
                                    self.acceptable_links))

    @property
    def good_links(self):
        return [l for l in self.links if l.valid]

    @property
    def acceptable_links(self):
        return [l for l in self.http_links if l.potential]

    @property
    def explain_downloadable(self):
        text = '{:s} is {}downloadable{}.{}'
        links = ''
        if self.downloadable:
            nope = ''
            suffix = ''
        else:
            nope = 'not '
            suffix = ' because it {}'

            @generated_list
            def list_reasons():
                _reasons = (
                    ('is already downloaded', self.downloaded),
                    ('is nuked', self.nuked),
                    ('is a download in progress', self.downloading),
                    ('has no valid links', self.no_valid_links),
                )
                for message, condition in _reasons:
                    if condition:
                        yield message
            reasons = list_reasons()
            if len(reasons) > 1:
                reasons[-2:] = [' and '.join(reasons[-2:])]
            reason = ', '.join(reasons)
            suffix = suffix.format(reason)
        if self.links.count() > 0:
            status = '\n\t'.join(self._link_status)
            links = '\n\t{}'.format(status)
        return text.format(str(self.release), nope, suffix, links)

    @property
    def downloadable(self):
        return not (self.downloaded or self.nuked or self.downloading or
                    self.no_valid_links)

    def add_link(self, url):
        if url is None:
            raise ValueError('Tried to add None as link to {}'.format(self))
        self.links.append(Link.create(url))

    def add_links(self, urls):
        for url in urls:
            self.add_link(url)

    def has_url(self, url):
        return any(link.url == url for link in self.links)

    @property
    def valid_links(self):
        return any(link.valid for link in self.links)

    @property
    def potential_links(self):
        return any(link.potential for link in self.http_links)

    @property
    def no_valid_links(self):
        return not self.valid_links

    @property
    def _link_status(self):
        return [l.status_str for l in self.links]

    @property
    def retry_subtitle_download(self):
        time = unix_to_datetime(self.last_subtitle_failure)
        return (
            self.subtitle_failures == 0 or
            (datetime.now() - time).total_seconds() > self._next_subtitle_try
        )

    @property
    def _next_subtitle_try(self):
        return (self._subtitle_retry_coefficient * 60 *
                (2 ** (self.subtitle_failures - 1)))

    def __repr__(self):
        rep = ('<ReleaseMonitor {} downloaded: {} downloadable: {} nuked: {}'
               ' archived: {} valid links: {} added: {}>')
        return rep.format(self.release, self.downloaded, self.downloadable,
                          self.nuked, self.archived, self.valid_links,
                          self.added_to_library)

    @property
    def checkable_links(self):
        return [l for l in self.http_links if l.checkable]

    @property
    def recheckable_links(self):
        return [l for l in self.http_links if l.recheckable]

    def is_same_episode(self, monitor):
        return self.release.is_same_episode(monitor.release)

    @property
    def torrent(self):
        torrent = self.torrent_link
        if torrent:
            return torrent.torrent

    def torrent_valid(self):
        self.torrent is not None and self.torrent.valid

    @property
    def torrent_link(self):
        return find(lambda l: isinstance(l, TorrentLink), self.links)

    @property
    def torrent_links(self):
        return filter(lambda l: isinstance(l, TorrentLink), self.links)

    @property
    def info(self):
        return dict(
            release=self.release.info,
            downloaded=self.downloaded,
            archived=self.archived,
            links=[l.info for l in self.links]
        )

    @property
    def last_torrent_search(self):
        return unix_to_datetime(self.last_torrent_search_stamp or 0)

    @last_torrent_search.setter
    def last_torrent_search(self, date):
        self.last_torrent_search_stamp = datetime_to_unix(date)

    def can_recheck(self, threshold):
        return ((datetime.now() - self.last_torrent_search).total_seconds() >
                threshold)

    @property
    def has_cachable_torrents(self):
        return len(self.cachable_torrents) > 0

    @property
    def cachable_torrents(self):
        return [l.torrent for l in self.torrent_links if l.cachable]

    def contains_link(self, link):
        return find(lambda l: l.url == link, self.links)


@configurable(get=['full_hd'])
class ReleaseFactory(object):

    def __init__(self):
        self._etvdb = ETVDBFacade()

    def __call__(self, title, name, flags, group, enum=None, res=None,
                 is_fix=False):
        is_series = bool(enum)
        enum = episode_enumeration(enum)
        name = make_series_name(name)
        group = group or ''
        return Release(title=title, name=name, group=group.lower(),
                       season=enum[0], episode=enum[1], is_series=is_series,
                       resolution=res, is_fix=is_fix)

    def from_title_match(self, title, match):
        name = match.group('name')
        flags = re.split('[. ]', match.group('flags'))
        enum = match.group('enum')
        if is_date_enum(enum):
            year, month, day = re.split('[. _]', enum)
            try:
                enum = self._etvdb.convert_date_enum(name, year, month, day)
            except ParseError as e:
                logger.error('Error while processing "{}":'.format(title))
                logger.error(e)
        group = match.group('group')
        res = find(lambda f: re.match('\d{3,4}p$', f, re.I), flags) or 'sd'
        fix = any(term in flags for term in ['proper', 'repack'])
        return self(title, name, flags, group, enum, res, fix)

    def monitor_from_entry(self, entry):
        entry.resolve_redirects()
        return self.monitor(entry.release, entry.links)

    def monitor(self, release, links, **kw):
        links = [Link.create(link) for link in links]
        args = merge(self._monitor_defaults, kw)
        return ReleaseMonitor(release, links=links, **args)

    @property
    def _monitor_defaults(self):
        return dict(
            downloaded=False,
            download_path='',
            archived=False,
            nuked=False,
            unknown=False,
            archiver_error=False,
            failed_downloads=0,
            downloading=False,
            subtitles_downloaded=False,
            subtitle_failures=0,
            last_subtitle_failure=0,
            added_to_library=False,
            _resolutions=self._resolutions,
        )

    @property
    def _resolutions(self):
        res = self._full_hd.maybe('1080p').to_list + List('720p')
        return ','.join(res)

__all__ = ['Release', 'ReleaseMonitor', 'ReleaseFactory']
