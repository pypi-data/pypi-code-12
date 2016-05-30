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
        super().__init__(releases, 5, 'download manager')
        self._min_failed = 0
        self._downloader_fact = DownloaderFactory()

    def _update(self, monitor, **data):
        self._releases.update_by_id(monitor.id, **data)

    def _fail(self, monitor, link):
        f = monitor.failed_downloads + 1
        self._update(monitor, failed_downloads=f)
        self._releases.fail_link(link.id)

    def _handle(self, monitor):
        logger.info('Downloading {!s}.'.format(monitor.release))
        self._update(monitor, downloading=True)
        link = monitor.link
        self._download_dir.mkdir(parents=True, exist_ok=True)
        try:
            dl = self._downloader_fact(link.download_url,
                                       download_dir=str(self._download_dir))
            dl.retrieve()
        except NotEnoughDiskSpace as e:
            logger.error('Downloader: {}'.format(e))
        except (requests.RequestException, ShareHosterError,
                ConnectionError, socket.timeout) as e:
            self._fail(monitor, link)
            logger.error('Downloader: {}'.format(e))
        else:
            self._check_download(monitor, link, dl)
        finally:
            self._update(monitor, downloading=False)

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
            self._fail(monitor, link)
            msg = 'File smaller than required ({}): {!s}'
            logger.error(msg.format(sizeof_fmt(size), monitor.release))
        elif size != dl.file_size and dl.file_size != -1:
            self._fail(monitor, link)
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
            self._releases.update_by_id(monitor.id,
                                        download_path=str(dl.file_path))
            self._releases.mark_episode_downloaded(monitor)

    @property
    def _candidates(self):
        candidates = self._releases.downloadable
        counts = [r.failed_downloads for r in candidates]
        self._min_failed = min(counts or [0])
        return candidates

    def _qualify(self, release):
        return release.failed_downloads == self._min_failed

__all__ = ['Downloader']
