from golgi.config import configurable
from series.logging import Logging
from tek.tools import find

from tek_utils.sharehoster.torrent import torrent_cacher_client
from tek_utils.sharehoster.errors import ShareHosterError

from tryp import List

from series.get.handler import ReleaseHandler, R, L
from series.get.errors import SeriesException
from series.condition import LambdaCondition, HandlerCondition, DynOr
from series.get.model.release import ReleaseMonitor
from series.get.model.link import TorrentLink


class CachableTorrent(HandlerCondition):

    def __init__(self, torrent: TorrentLink) -> None:
        self.torrent = torrent

    @property
    def cond(self):
        return ~(L('caching') | L('valid') | L('dead'))

    def ev(self, release: ReleaseMonitor):
        return self.cond.ev(self.torrent)

    def describe(self, item, target):
        d = self.cond.describe(self.torrent, target)
        m = self.torrent.url
        return '{} -> {}'.format(m, d)


class CachableTorrents(DynOr):

    @property
    def _sub_type(self):
        return CachableTorrent

    def _dyn_sub(self, item: ReleaseMonitor):
        return List.wrap(item.torrent_links)

    def describe(self, item, target):
        d = super().describe(item, target)
        return 'cachable torrents => {}'.format(d)


@configurable(torrent=['cacher'])
class TorrentHandler(ReleaseHandler):

    def __init__(self, releases, *a, **kw):
        self._pending = []
        super().__init__(releases, 5, 'torrent handler', **kw)
        self._client = torrent_cacher_client()

    def _check(self):
        super()._check()
        self._check_pending()
        self._check_error()

    def _handle(self, monitor):
        for torrent in monitor.cachable_torrents:
            msg = 'Requesting torrent download for {}…'.format(monitor.release)
            self.log.info(msg)
            self._pending.append([monitor, torrent])
            try:
                torrent.request()
            except ShareHosterError as e:
                msg = 'Error requesting torrent for {}: {}'
                self.log.error(msg.format(monitor.release, e))

    def _check_pending(self):
        done = []
        for monitor, torrent in self._pending:
            try:
                if torrent.cached:
                    self._releases.torrent_cached(torrent.record.id)
                    done.append([monitor, torrent])
                    msg = 'Flagging torrent as cached: {}'
                    self.log.info(msg.format(monitor.release))
            except ShareHosterError as e:
                msg = 'Error checking torrent status for {}: {}'
                self.log.error(msg.format(monitor.release, e))
        for item in done:
            self._pending.remove(item)

    def _check_error(self):
        errors = [t.get('id', 0) for t in self._client.transfers
                  if t.get('status') == 'ERROR']
        if errors:
            self.log.info('Canceling erroneous torrents.')
            self._client.cancel_transfers(errors)
            self._client.clean_transfers()

    @property
    def _conditions(self):
        return ~(
            R('downloaded') |
            LambdaCondition('in progress', self._requesting)
        ) & CachableTorrents()

    def _qualify(self, monitor):
        try:
            return super()._qualify(monitor)
        except ShareHosterError as e:
            msg = 'Error checking torrent status for {}: {}'
            self.log.error(msg.format(monitor.release, e))

    def _requesting(self, monitor) -> bool:
        return find(lambda item: item[0] == monitor, self._pending) is not None

    def _sanity_check(self):
        self._check_cacher_config()
        self._check_service_accessible()

    def _check_cacher_config(self):
        if not self._cacher:
            raise SeriesException('No torrent cacher configured!')

    def _check_service_accessible(self):
        cacher = torrent_cacher_client()
        if not cacher.account_info:
            raise SeriesException(
                'Couldn\'t access torrent cacher \'{}\'!'.format(self._cacher))

__all__ = ['TorrentHandler']
