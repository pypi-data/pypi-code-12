import re
import itertools
from datetime import datetime

import requests

import lxml

from series.get.handler import ReleaseHandler, R
from series.get.model.release import ReleaseMonitor
from series.condition import LambdaCondition

from golgi.config import configurable
from series.logging import Logging

from tek_utils.sharehoster.torrent import SearchResultFactory
from tek_utils.sharehoster.kickass import NoResultsError

from tryp import List, LazyList, _, F, __
from tryp.lazy import lazy


class SearchQuery:

    def __init__(self, monitor: ReleaseMonitor, res: str) -> None:
        self.monitor = monitor
        self.release = self.monitor.release
        self.res = res

    @property
    def _enum(self):
        return 's{:0>2}e{:0>2}'.format(self.release.season,
                                       self.release.episode)

    @property
    def _name(self):
        return self.release.name.replace('_', ' ').replace('\'', '')

    @property
    def query(self):
        return '{} {} {}'.format(
            self._name,
            self._enum,
            self.res,
        )

    @property
    def valid(self):
        return True

    @property
    def search_string(self):
        return self.release.search_string_with_res(self.res)

    @lazy
    def search_re(self):
        return re.compile(self.search_string, re.I)

    @property
    def desc(self):
        return 'torrent {} {}'.format(self.release, self.res)


class DateQuery(SearchQuery):

    @property
    def _enum(self):
        return self.release.airdate.strftime('%Y-%m-%d')

    @property
    def valid(self):
        return self.release.has_airdate


@configurable(torrent=['pirate_bay_url', 'search_engine'],
              get=['torrent_recheck_interval'])
class TorrentFinder(ReleaseHandler):

    def __init__(self, releases, *a, **kw):
        super().__init__(releases, 5, 'torrent finder',
                         cooldown=self._torrent_recheck_interval, **kw)
        self._search = (self._search_tpb if self._search_engine == 'piratebay'
                        else self._search_kickass)
        self._limit = 10

    def _queries(self, monitor):
        q = lambda r: List(SearchQuery(monitor, r), DateQuery(monitor, r))
        return monitor.resolutions // q

    def _handle(self, monitor):
        self.log.debug('Searching for torrent for "{}"'.format(monitor.release))
        self._update(monitor, last_torrent_search=datetime.now())
        return LazyList(self._queries(monitor))\
            .filter(_.valid)\
            .find(self._handle_query)

    def _handle_query(self, query):
        self.log.debug('Search {}: {}'.format(query.desc, query.query))
        try:
            results = List.wrap(self._search(query.query))
        except NoResultsError as e:
            self.log.debug('Error searching for torrent: {}'.format(e))
        except requests.RequestException as e:
            self.log.warn(
                'Connection failure in {} search'.format(self._search_engine))
        except lxml.etree.XMLSyntaxError as e:
            self.log.warn('Parse error in kickass results: {}'.format(e))
        else:
            return self._process_results(query, results)

    def _process_results(self, query, results: List):
        matcher = query.search_re
        return (
            results
            .filter(lambda a: matcher.search(a.title))
            .map(_.magnet_link)
            .filter(_)
            .filter_not(query.monitor.contains_link)
            .head
            .map(F(self._add_link, query))
            .replace(True)
            .get_or_else(F(self._no_result, query, results))
        )

    def _add_link(self, query, link):
        self.log.info('Added torrent to release "{}"'.format(query.release))
        self._releases.add_link_by_id(query.monitor.id, link)

    def _no_result(self, query, results):
        self.log.debug('None of the results match the release.')
        self.log.debug('Search string: {}'.format(query.search_string))
        self.log.debug('\n'.join([r.title for r in results]))

    def _search_tpb(self, query):
        import tpb
        bay = tpb.TPB(self._pirate_bay_url)
        search = bay.search(query).order(tpb.ORDERS.SEEDERS.DES)
        return [SearchResultFactory.from_tpb(res) for res in
                itertools.islice(search, self._limit)]

    def _search_kickass(self, query):
        from tek_utils.sharehoster import kickass
        search = kickass.Search(query).order(kickass.ORDER.SEED,
                                             kickass.ORDER.DESC)
        return [SearchResultFactory.from_kickass(res) for res in
                itertools.islice(search, self._limit)]

    @property
    def _conditions(self):
        return (
            ~R('downloaded') & ~R('has_cachable_torrents') &
            LambdaCondition('recheck interval',
                            __.can_recheck(self._torrent_recheck_interval))
        )

    def activate_id(self, id):
        super().activate_id(id)
        self._releases.update_by_id(id, last_torrent_search_stamp=0)

__all__ = ['TorrentFinder']
