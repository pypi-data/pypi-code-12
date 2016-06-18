"""Provides functional access to the UnityCloud Collaboration service.
"""
import os
import errno
import hashlib
import dateutil.parser

from logging import getLogger
from urllib import urlencode
from requests import HTTPError
from datetime import datetime
from send2trash import send2trash
from collabi.open_struct import OpenStruct
from collabi.rest import Rest

class Collab(object):
    CHUNK_BYTES = 32768

    class Revision(OpenStruct):
        def __init__(self, obj):
            super(Revision, self).__init__(obj)
            if hasattr(self, 'committed_date'):
                self.committed_date = dateutil.parser.parse(self.committed_date)
            else:
                self.committed_date = datetime.utcfromtimestamp(0)

    class FileEntry(OpenStruct):
        pass

    class DirectoryEntry(OpenStruct):
        pass

    class LocalEntry(object):
        def __init__(self, path, expected_md5=None):
            self._logger = getLogger('unity.collab.local_entry')
            self._md5 = None
            self.expected_md5 = expected_md5
            self.path = path
            self.transfer_seconds = None
            self.transfer_bytes = None

        def exists(self):
            return os.path.exists(self.path)

        def open(self, *args):
            return open(self.path, *args)

        def size(self):
            return os.path.getsize(self.path)

        def mtime(self):
            return os.path.getmtime(self.path)

        def md5(self):
            if not self._md5:
                hash_md5 = hashlib.md5()
                with self.open('rb') as f:
                    for chunk in iter(lambda: f.read(Collab.CHUNK_BYTES), b''):
                        hash_md5.update(chunk)
                self._md5 = hash_md5.hexdigest()
            return self._md5

        def isdiff(self, cloud_entry):
            return (
                (isinstance(cloud_entry, Collab.FileEntry) and
                 not os.path.isfile(self.path)) or
                (isinstance(cloud_entry, Collab.DirectoryEntry) and
                 not os.path.isdir(self.path)) or
                (cloud_entry.size != self.size()) or
                (cloud_entry.hash != self.md5())
            )

        def delete(self, overwrite=False):
            if overwrite:
                os.remove(self.path)
            else:
                self._logger.info('Sending to trash: '+self.path)
                send2trash(self.path)

        def __repr__(self):
            return str({
                'path': self.path,
                'md5': self.md5(),
                'mtime': self.mtime(),
                'size': self.size(),
            })

    class Download(object):
        def __init__(self, path_md5s, recursive=False):
            self._logger = getLogger('unity.collab.download')
            self.pathmap = {}
            self.filemap = {}
            for path, md5 in path_md5s.iteritems():
                fl = Collab.LocalEntry(path, expected_md5=md5)
                self.pathmap[path] = fl

    class Upload(object):
        def __init__(self, paths, recursive=False):
            self._logger = getLogger('unity.collab.upload')
            self.transaction_id = None
            self.md5map = {}
            self.pathmap = {}
            self.filemap = {}
            for path in paths:
                if isinstance(path, Collab.LocalEntry):
                    fl = path
                else:
                    if os.path.isdir(path):
                        if recursive:
                            paths.extend(os.path.join(path, e) for e in os.listdir(path))
                        else:
                            self._logger.warning('Skipping directory (recursive not enabled): ' +
                                                 path)
                        continue
                    fl = Collab.LocalEntry(path)
                self.md5map[fl.md5()] = fl # doesn't matter which one if multiple (same md5)
                self.pathmap[path] = fl

    ########################################

    def __init__(self, rest, project_id, revision_id):
        self._logger = getLogger('unity.collab')
        self._rest = rest
        self._project_id = project_id
        self._revision_id = revision_id
        self._project_path = 'projects/'+self._project_id+'/'
        self._revisions_path = self._project_path+'branches/master/revisions/'
        self._revision_path = self._revisions_path+revision_id+'/'

    def list(self, paths, recursive=False):
        options = '?recurse' if recursive else ''
        entries = []
        for path in paths:
            if path[0] != '/': path = '/'+path
            rpath = self._revision_path+'entries'+path+options
            resp = self._rest.request('get', rpath)
            json = resp.json()
            if 'name' in json:
                dirpath = path.replace(json['name'],'',1)
                self._process(dirpath, json, entries)
        return entries

    def revisions(self, **kwargs):
        if 'start_revision' not in kwargs:
            kwargs['start_revision'] = self._revision_id
        rpath = self._revisions_path+'?'+urlencode(kwargs)
        resp = self._rest.request('get', rpath)
        return resp.json()['revisions']

    def history(self, paths, limit=None):
        if paths == ['/']:
            return {'/': self.revisions(limit=limit)}
        bpath = self._revision_path+'/history'
        history = {}
        for path in paths:
            sep = '' if path[0] == '/' else '/'
            hpath = bpath+sep+path
            uri = hpath+'?limit='+limit if limit else hpath
            resp = self._rest.request('get', uri)
            history[path] = resp.json()['history']
        return history

    def download(self, paths_or_entries, dst, recursive=False, overwrite=False, concurrency=10):
        path_md5s = self._get_path_md5s(paths_or_entries, recursive)
        if len(path_md5s) > 1:
            self._logger.info('Starting to download '+str(len(path_md5s))+' files')

        download = Collab.Download(path_md5s, recursive=recursive)

        for fl in download.pathmap.values():
            if fl.path[0] != '/': path = '/'+fl.path
            if fl.expected_md5:
                rpath = self._project_path+'cache/source/'+fl.expected_md5
            else:
                rpath = self._revision_path+'download'+fl.path
            areq = self._rest.async_request('get', rpath)
            req_id = areq.kwargs['headers'][Rest.REQ_ID_HDR]
            download.filemap[req_id] = fl

        resps = self._rest.async_request_flush(concurrency)

        for resp in resps:
            resp.raise_for_status()
            req = resp.request
            req_id = req.headers[Rest.REQ_ID_HDR]
            fl = download.filemap[req_id]
            fldst = os.path.abspath(os.path.join(dst, './'+fl.path))
            self._save_file(resp, fldst, overwrite)
            fl.transfer_seconds = resp.elapsed.total_seconds()
            fl.transfer_bytes = int(resp.headers['Content-Length'])

        return download

    def upload(self, paths, upload=None, recursive=False, concurrency=10):
        if not upload: upload = Collab.Upload(paths, recursive=recursive)
        rpath = self._project_path+'uploads'
        if upload.transaction_id:
            method = 'put'
            rpath += '/'+transaction_id
        else:
            method = 'post'
        resp = self._rest.request(method, rpath, json={'files': upload.md5map.keys()})
        json = resp.json()
        upload.transaction_id = json['transaction_id']
        urls = json['signed_urls']
        if len(urls) > 1: self._logger.info('Starting to upload '+str(len(urls))+' files')

        for md5, url in urls.iteritems():
            fl = upload.md5map[md5]
            areq = self._rest.async_request_raw('put', url, data=fl.open('rb'))
            req_id = areq.kwargs['headers'][Rest.REQ_ID_HDR]
            upload.filemap[req_id] = fl

        resps = self._rest.async_request_flush(concurrency)

        for resp in resps:
            resp.raise_for_status()
            req = resp.request
            req.body.close()
            req_id = req.headers[Rest.REQ_ID_HDR]
            fl = upload.filemap[req_id]
            fl.transfer_seconds = resp.elapsed.total_seconds()
            fl.transfer_bytes = int(req.headers.get('Content-Length', 0))
            server = resp.headers.get('Server', '')
            if server == 'AmazonS3':
                etag = resp.headers['ETag']
                etag = etag.replace('"', '').strip()
                if fl.md5() != etag:
                    raise ValueError(fl.path + ' md5 mismatch: expected='+fl.md5()+ ' got='+etag)
            else:
                self._logger.warning('Not validating ETag for response from '+server)

        return upload

    def commit(self, message, upload=None, moves=[], deletes=[], strip_components=0):
        hr = 'NOT_IMPLEMENTED' if self._revision_id == 'HEAD' else self._revision_id
        aou = []
        action_info = {
            'action': 'commit',
            'transaction_id': (upload.transaction_id if upload else None),
            'data': {
                'head_revision': hr,
                'comment': message,
                'add_or_update': aou,
                'move': moves,
                'delete': deletes
            }
        }
        if upload:
            for fl in upload.pathmap.values():
                aou.append({
                    'path': self._collab_path(fl.path, strip_components),
                    'hash': fl.md5(),
                    'revision': self._revision_id
                })
        resp = self._rest.request('post', self._revisions_path, json={'action_info': action_info})
        return resp.json()

    def upload_sync(self, local_root, message, strip_components=0):
        upload_entries = []
        cloud_root = self._collab_path(local_root, strip_components)

        cloud_entries = self._get_cloud_entries(cloud_root)
        local_entries = self._get_local_entries(local_root)

        for local_entry in local_entries.values():
            cloud_path = self._collab_path(local_entry.path, strip_components)
            cloud_entry = cloud_entries.pop(cloud_path, None)
            if not cloud_entry or local_entry.isdiff(cloud_entry):
                upload_entries.append(local_entry)

        if len(upload_entries) > 0:
            upload = self.upload(upload_entries)
        else:
            upload = None

        deletes = []
        for cloud_entry in cloud_entries.values():
            self._logger.info('Deleting: '+cloud_entry.name)
            deletes.append({'path': cloud_entry.name, 'revision': self._revision_id})

        if upload or len(deletes) > 0:
            return self.commit(message, upload, deletes=deletes, strip_components=strip_components)

        return None

    def download_sync(self, local_root, strip_components=0, overwrite=False):
        download_entries = []
        cloud_root = self._collab_path(local_root, strip_components)

        cloud_entries = self._get_cloud_entries(cloud_root)
        local_entries = self._get_local_entries(local_root)

        for cloud_entry in cloud_entries.values():
            local_path = self._local_path_join(local_root, cloud_entry.name)
            local_entry = local_entries.pop(local_path, None)
            if not local_entry or local_entry.isdiff(cloud_entry):
                download_entries.append(cloud_entry)

        for local_entry in local_entries.values():
            local_entry.delete(overwrite)

        if len(download_entries) > 0:
            return self.download(download_entries, local_root, overwrite=overwrite)

        return None

    ######################################################################
    # private

    def _process(self, path, json, entries):
        if not path.endswith('/'): path += '/'
        if 'recursive' in json:
            del(json['recursive'])
            if 'entries' in json :
                dirpath = path + json['name']
                for entry_json in json['entries']:
                    self._process(dirpath, entry_json, entries)
                return
            else:
                entry = Collab.DirectoryEntry(json)
        else:
            entry = Collab.FileEntry(json)
        entry.name = path + entry.name
        entries.append(entry)

    def _get_path_md5s(self, paths_or_entries, recursive):
        if isinstance(paths_or_entries[0], str):
            entries = self.list(paths_or_entries, recursive)
        else:
            entries = paths_or_entries
        path_md5s = {}
        for entry in entries:
            if isinstance(entry, Collab.FileEntry):
                path_md5s[entry.name] = entry.hash
        return path_md5s

    def _save_file(self, resp, dst, overwrite):
        self._logger.info('Saving '+dst);
        self._mkpath_parent(dst)
        if (not overwrite and os.path.exists(dst)): send2trash(dst)
        with open(dst, 'wb') as fd:
            for chunk in resp.iter_content(Collab.CHUNK_BYTES):
                fd.write(chunk)

    def _get_cloud_entries(self, path):
        try:
            raw_entries = self.list([path], recursive=True)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                raw_entries = []
            else:
                raise
        entries = {}
        for entry in raw_entries:
            if not isinstance(entry, Collab.FileEntry): continue
            entries[entry.name] = entry
        return entries

    @staticmethod
    def _get_local_entries(path):
        entries = {}
        for root, dirnames, filenames in os.walk(path):
            for fn in filenames:
                entry = Collab.LocalEntry(os.path.join(root, fn))
                entries[entry.path] = entry
        return entries

    @staticmethod
    def _local_path_join(local_path, collab_path):
        components = local_path.split(os.sep) + collab_path.split('/')
        return os.sep.join([c for c in components if c != ''])

    @staticmethod
    def _collab_path(local_path, strip_components=0):
        # FIXME: this will break with '..' components (i.e. local_path='../../foo/bar')
        # split up by OS separator, but join with collab's
        components = [c for c in local_path.split(os.sep) if c != '' and c != '.']
        return '/'+Collab._collab_join(*components[strip_components:])

    @staticmethod
    def _collab_join(*components):
        return '/'.join(components)

    @staticmethod
    def _mkpath_parent(path):
        Collab._mkpath(os.path.dirname(path))

    @staticmethod
    def _mkpath(path):
        try:
            os.makedirs(path)
        except OSError as ex:  # Python >2.5
            if ex.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
