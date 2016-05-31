from ubackup.bucket.base import Bucket
from ubackup import settings, utils
from ubackup.utils import filesizeformat, stream_shell
from datetime import datetime
from dateutil import parser

import requests
import sys

import logging
logger = logging.getLogger(__name__)


class DropboxBucket(Bucket):
    TYPE = 'dropbox'
    BASE_URL = 'https://api.dropbox.com/1'
    CONTENT_URL = 'https://api-content.dropbox.com/1'

    def __init__(self, token=None):
        self.token = token or self.conf['token']

    def sign(self):
        return {"Authorization": "Bearer %s" % self.token}

    def request(self, method, url, base_url=None, *args, **kwargs):
        r = requests.request(
            method,
            "%s/%s" % (base_url or self.BASE_URL, url),
            *args,
            **dict(kwargs, headers=self.sign()))
        if r.status_code != 200:
            raise self.BucketError("The bucket returned an error.", r)
        return r

    def content_request(self, *args, **kwargs):
        return self.request(base_url=self.CONTENT_URL, *args, **kwargs)

    def log(self, file_name, message, level='debug'):
        getattr(logger, level)('%(type)s(%(file_name)s): %(message)s' % {
            'type': self.TYPE,
            'file_name': file_name,
            'message': message
        })

    def push(self, stream, file_name, versioning=False):
        self.log(file_name, 'start')
        start = datetime.now()

        chunk = stream.read(settings.CHUNK_SIZE)
        r = self.content_request(
            method="put",
            url="chunked_upload",
            data=chunk)
        data = r.json()
        upload_id = data.get("upload_id")
        offset = data.get("offset")
        self.log(file_name, 'pushed %s' % filesizeformat(sys.getsizeof(chunk)))

        while True:
            chunk = stream.read(settings.CHUNK_SIZE)
            if not chunk:
                break

            r = self.content_request(
                method="put",
                url="chunked_upload",
                params={
                    "upload_id": upload_id,
                    "offset": offset
                },
                data=chunk)
            data = r.json()
            offset = data.get("offset")

            self.log(file_name, 'pushed %s' % filesizeformat(sys.getsizeof(chunk)))

        r = self.content_request(
            method="post",
            url="commit_chunked_upload/sandbox/%s" % file_name,
            params={
                "upload_id": upload_id,
                "overwrite": True,
            })

        self.log(
            file_name,
            'pushed in %ss' % utils.total_seconds(datetime.now() - start),
            level='info')

    def pull(self, file_name, rev=None):
        header = 'Authorization: %s' % self.sign()['Authorization']
        get_params = ''
        if rev is not None:
            get_params = '?rev=%s' % rev
        return stream_shell(
            cmd='wget -qO- --header="%s" %s/files/sandbox/%s%s' % (header, self.CONTENT_URL, file_name, get_params))

    def exists(self, file_name):
        r = self.request(
            method="get",
            url="search/auto",
            params={
                "query": file_name,
            })
        return len(r.json()) > 0

    def get_revisions(self, file_name):
        r = self.request(
            method="get",
            url="revisions/auto/%s" % file_name,
            params={
                'rev_limit': 100,
            })

        def revision(rev):
            return {
                'id': rev['rev'],
                'size': rev['bytes'],
                'date': parser.parse(rev['modified'])
            }

        return [revision(data) for data in r.json()]
