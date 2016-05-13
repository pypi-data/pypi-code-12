import re
import time
import logging
import requests
from collections import namedtuple
from itertools import chain, islice

from vminspect.filesystem import FileSystem


VT_REPORT_URL = 'https://www.virustotal.com/vtapi/v2/file/report'

VTReport = namedtuple('VTReport', ('name', 'hash', 'detections'))


class VTScanner:
    """VirusTotal scanner.

    Allows to scan the given disk content and query VirusTotal.

    disk must contain the path of a valid disk image.
    apikey must be a valid VT API key.

    The attribute batchsize controls the amount of object per VT query.

    """
    def __init__(self, disk, apikey):
        self._disk = disk
        self._apikey = apikey
        self._filesystem = None
        self.batchsize = 1
        self.logger = logging.getLogger(
            "%s.%s" % (self.__module__, self.__class__.__name__))

    def __enter__(self):
        self._filesystem = FileSystem(self._disk)
        self._filesystem.mount()

        return self

    def __exit__(self, *_):
        self._filesystem.umount()

    @property
    def apikey(self):
        return self._apikey

    def scan(self, filetypes=None):
        """Iterates over the content of the disk and queries VirusTotal
        to determine whether it's malicious or not.

        filetypes is a list containing regular expression patterns.
        If given, only the files which type will match with one or more of
        the given patterns will be queried against VirusTotal.

        For each file which is unknown by VT or positive to any of its engines,
        the method yields a namedtuple:

        VTReport(path        -> C:\\Windows\\System32\\infected.dll
                 hash        -> ab231...
                 detections) -> list engine -> detection

        Files unknown by VirusTotal will contain the string 'UNKNOWN'
        in the detections field.

        """
        self.logger.debug("Scanning FS content.")
        checksums = self.filetype_filter(self._filesystem.checksums('/'),
                                         filetypes=filetypes)

        self.logger.debug("Querying %d objects to VTotal.", len(checksums))
        for files in chunks(checksums, size=self.batchsize):
            files = dict((reversed(e) for e in files))
            response = vtquery(self._apikey, files.keys())

            yield from self.parse_response(files, response)

    def filetype_filter(self, files, filetypes=None):
        if filetypes is not None:
            pattern = '|'.join('(?:{0})'.format(t) for t in filetypes)

            return [f for f in files
                    if re.match(pattern, self._filesystem.file(f[0]))]
        else:
            return files

    def parse_response(self, files, response):
        for result in response:
            sha1 = result['resource']
            path = files[sha1]

            if result['response_code'] > 0:
                self.logger.debug("%s - %d positives.",
                                  path, result['positives'])

                if result['positives'] > 0:
                    yield VTReport(path, sha1,
                                   [(e, d) for e, d in result['scans'].items()
                                    if d['detected']])
            else:
                self.logger.debug("%s - Unknown file.", path)

                yield VTReport(path, sha1, 'UNKNOWN')


def vtquery(apikey, checksums):
    """Performs the query dealing with errors and throttling requests."""
    data = {'apikey': apikey,
            'resource': isinstance(checksums, str) and checksums
                        or ', '.join(checksums)}

    while 1:
        response = requests.post(VT_REPORT_URL, data=data)
        response.raise_for_status()

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            logging.debug("API key request rate limit reached, throttling.")
            time.sleep(60)
        else:
            raise RuntimeError("Response status code %s" % response.status_code)


def chunks(iterable, size=1):
    """Splits iterator in chunks."""
    iterator = iter(iterable)

    for element in iterator:
        yield chain([element], islice(iterator, size - 1))
