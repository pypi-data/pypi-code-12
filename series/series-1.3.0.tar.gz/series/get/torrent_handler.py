from tek.config import configurable
from tek import logger
from tek.tools import find

from tek_utils.sharehoster.torrent import torrent_cacher_client
from tek_utils.sharehoster.errors import ShareHosterError
from tek_utils.sharehoster.putio import PutIoClient

from series.get.handler import ReleaseHandler
from series.get.errors import SeriesDException


@configurable(torrent=['cacher'])
class TorrentHandler(ReleaseHandler):

    def __init__(self, releases, *a, **kw):
        self._pending = []
        super(TorrentHandler, self).__init__(releases, 5, 'torrent handler',
                                             **kw)
        self._client = PutIoClient()

    def _check(self):
        super(TorrentHandler, self)._check()
        self._check_pending()
        self._check_error()

    def _handle(self, monitor):
        msg = 'Requesting torrent download for {}…'.format(monitor.release)
        logger.info(msg)
        self._pending.append([monitor, monitor.torrent])
        try:
            monitor.torrent.request()
        except ShareHosterError as e:
            msg = 'Error requesting torrent for {}: {}'
            logger.error(msg.format(monitor.release, e))

    def _check_pending(self):
        done = []
        for monitor, torrent in self._pending:
            try:
                if torrent.cached:
                    monitor.torrent_link.cached = True
                    done.append([monitor, torrent])
                    msg = 'Flagging torrent as cached: {}'
                    logger.info(msg.format(monitor.release))
            except ShareHosterError as e:
                msg = 'Error checking torrent status for {}: {}'
                logger.error(msg.format(monitor.release, e))
        for item in done:
            self._pending.remove(item)
        if done:
            self._commit()

    def _check_error(self):
        errors = [t.get('id', 0) for t in self._client.transfers
                  if t.get('status') == 'ERROR']
        if errors:
            logger.info('Canceling erroneous torrents.')
            self._client.cancel_transfers(errors)
            self._client.clean_transfers()

    def _qualify(self, monitor):
        try:
            return (not monitor.downloaded and monitor.torrent is not None
                    and monitor.torrent_link.cachable
                    and not self._requesting(monitor))
        except ShareHosterError as e:
            msg = 'Error checking torrent status for {}: {}'
            logger.error(msg.format(monitor.release, e))

    def _requesting(self, monitor):
        return find(lambda item: item[0] == monitor, self._pending)

    def _sanity_check(self):
        self._check_cacher_config()
        self._check_service_accessible()

    def _check_cacher_config(self):
        if not self._cacher:
            raise SeriesDException('No torrent cacher configured!')

    def _check_service_accessible(self):
        cacher = torrent_cacher_client()
        if not cacher.account_info:
            raise SeriesDException(
                'Couldn\'t access torrent cacher \'{}\'!'.format(self._cacher))

__all__ = ['TorrentHandler']
