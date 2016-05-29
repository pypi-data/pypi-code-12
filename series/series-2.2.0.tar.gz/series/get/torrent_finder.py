import re
import itertools
from datetime import datetime

import requests

import lxml

from series.get.handler import ReleaseHandler

from tek.config import configurable
from tek import logger

from tek_utils.sharehoster.torrent import SearchResultFactory
from tek_utils.sharehoster.kickass import NoResultsError

from tryp import List


@configurable(torrent=['pirate_bay_url', 'search_engine'],
              get=['torrent_recheck_interval'])
class TorrentFinder(ReleaseHandler):

    def __init__(self, releases, *a, **kw):
        super().__init__(releases, 5, 'torrent finder',
                                            **kw)
        self._search = (self._search_tpb if self._search_engine == 'piratebay'
                        else self._search_kickass)
        self._limit = 10

    def _handle(self, monitor):
        logger.debug('Searching for torrent for "{}"'.format(monitor.release))
        monitor.last_torrent_search = datetime.now()
        release = monitor.release
        query = '{} s{:0>2}e{:0>2} 720p'.format(
            release.name.replace('_', ' ').replace('\'', ''),
            release.season,
            release.episode,
        )
        if (not self._handle_query(monitor, query, release.search_string) and
                release.has_airdate):
            logger.debug('Searching for date enumeration')
            query = '{} {} 720p'.format(
                release.name.replace('_', ' '),
                release.airdate.strftime('%Y-%m-%d')
            )
            self._handle_query(monitor, query, release.date_search_string)

    def _handle_query(self, monitor, query, search_string):
        logger.debug('Torrent search query: {}'.format(query))
        try:
            results = self._search(query)
        except NoResultsError as e:
            logger.debug('Error searching for torrent: {}'.format(e))
        except requests.RequestException as e:
            logger.warn(
                'Connection failure in {} search'.format(self._search_engine))
        except lxml.etree.XMLSyntaxError as e:
            logger.warn('Parse error in kickass results: {}'.format(e))
        else:
            return self._process_results(monitor, results, search_string)

    def _process_results(self, monitor, results, search_string):
        release = monitor.release
        matcher = re.compile(search_string, re.I)
        matches = [r for r in results if matcher.search(r.title)]
        valid = [m for m in matches if m.magnet_link]
        new = [m for m in valid if not monitor.contains_link(m.magnet_link)]
        if new:
            link = new[0].magnet_link
            logger.info('Added torrent to release "{}"'.format(release))
            self._releases.add_link_by_id(monitor.id, link)
            return True
        else:
            logger.debug('None of the results match the release.')
            logger.debug('Search string: {}'.format(search_string))
            logger.debug('\n'.join([r.title for r in results]))

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

    def _qualify(self, monitor):
        return (not monitor.downloaded and
                not monitor.has_cachable_torrents and
                monitor.can_recheck(self._torrent_recheck_interval))

__all__ = ['TorrentFinder']
