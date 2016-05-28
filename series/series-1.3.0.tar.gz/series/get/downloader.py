import os
import socket

import requests

from tek import logger
from tek.config import configurable
from tek.errors import NotEnoughDiskSpace
from tek.tools import sizeof_fmt

from tek_utils.sharehoster import DownloaderFactory
from tek_utils.sharehoster.errors import ShareHosterError

from series.get.handler import ReleaseHandler


@configurable(get=['download_dir', 'min_size'])
class Downloader(ReleaseHandler):

    def __init__(self, releases, *a, **kw):
        super(Downloader, self).__init__(releases, 5, 'download manager')
        self._min_failed = 0
        self._downloader_fact = DownloaderFactory()

    def _handle(self, monitor):
        logger.info('Downloading {!s}.'.format(monitor.release))
        monitor.downloading = True
        link = monitor.link
        if not os.path.exists(self._download_dir):
            os.makedirs(self._download_dir)
        try:
            dl = self._downloader_fact(link.download_url,
                                       download_dir=self._download_dir)
            dl.retrieve()
        except NotEnoughDiskSpace as e:
            logger.error('Downloader: {}'.format(e))
        except (requests.RequestException, ShareHosterError,
                ConnectionError, socket.timeout) as e:
            link.check_failed()
            monitor.failed_downloads += 1
            logger.error('Downloader: {}'.format(e))
        else:
            self._check_download(monitor, link, dl)
        monitor.downloading = False

    def _check_download(self, monitor, link, dl):
        ''' Verify the downloaded file's size by means of two criteria:
        The content-length header sent from the hoster must match
        exactly.
        The config parameter min_size defines what is considered to be a
        faulty file, i.e. the link checker didn't detect the file to be
        invalid, but it is small enough to just be the hoster's error
        page.
        '''
        size = dl.outfile_size
        if size < self._min_size:
            link.check_failed()
            monitor.failed_downloads += 1
            msg = 'File smaller than required ({}): {!s}'
            logger.error(msg.format(sizeof_fmt(size), monitor.release))
        elif size != dl.file_size and dl.file_size != -1:
            link.check_failed()
            monitor.failed_downloads += 1
            msg = 'Filesize mismatch in download of {!s}:'
            logger.error(msg.format(monitor.release))
            msg = 'Got {}, expected {}.'
            logger.error(msg.format(size, dl.file_size))
            try:
                os.unlink(dl.file_path)
            except IOError:
                msg = 'Couldn\'t delete broken download of {}.'
                logger.warn(msg.format(monitor.release))
        else:
            monitor.download_path = dl.file_path
            self._releases.mark_episode_downloaded(monitor)
            self._commit()

    @property
    def _candidates(self):
        candidates = self._releases.downloadable
        counts = [r.failed_downloads for r in candidates]
        self._min_failed = min(counts or [0])
        return candidates

    def _qualify(self, release):
        return release.failed_downloads == self._min_failed

__all__ = ['Downloader']
