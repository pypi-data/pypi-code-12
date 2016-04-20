'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
__all__ = ['SXFileDownloader']

import os
import hashlib
import uuid
import sys
import fcntl
try:
    import queue as Queue
except ImportError:
    import Queue
from threading import Event

from sxclient.tools.thread_pool import ThreadPool


HASH_FN = hashlib.sha1
DEFAULT_TMP_DIRECTORY = os.path.join(
    os.path.abspath(os.sep), 'tmp', 'python-sxclient'
)
DEFAULT_NUMBER_OF_THREADS = 20
DEFAULT_NUMBER_OF_CONNECTIONS = 20

# The value below is supposed to fit a maximum limit accepted by sx cluster
DEFAULT_MAX_BLOCK_BATCH_SIZE = 30


class Context(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


class LockedFile(object):
    def __init__(self, path, mode, lock_mode):
        self.path = path
        self.mode = mode
        self.lock_mode = lock_mode
        self.fo = None

    def __enter__(self):
        self.fo = open(self.path, self.mode)
        fcntl.flock(self.fo, self.lock_mode)
        return self.fo

    def __exit__(self, type, value, traceback):
        fcntl.flock(self.fo, fcntl.LOCK_UN)
        self.fo.close()


class SXFileDownloader(object):
    '''
    Responsible for file streaming from SX server. It is time efficient at the
    cost of memory and disk space. Perfect when dealing with big files that
    have to be streamed fast.

    Example usage:

        >>> import sxclient
        >>>
        >>> # initialize sx
        >>> cluster = sxclient.Cluster('my.cluster.example.com')
        >>> user_data = sxclient.UserData.from_key_path(
        ...    '/path/to/my/keyfile')
        >>> sxcontroller = sxclient.SXController(cluster, user_data)
        >>> downloader = sxclient.SXFileDownloader(sxcontroller)
        >>>
        >>> downloader.initialize()
        >>> try:
        ...     blocks = downloader.get_blocks_iterator(
        ...         'my_volume', 'my_file')
        ...     for block_content in blocks:
        ...         print block_content
        ... finally:
        ...     downloader.close()

    Be sure to call .initialize() and .close() methods. Especially .close()
    has to be called so you should wrap the code in try...except block.
    However you may want to reuse SXFileDownloader between threads for example.
    You can safely do that but remember to call .close() afterwards.

    If you wish to use it as a one-time download then you can use it as
    a context manager as well:

    >>> with sxclient.SXFileDownloader(sxcontroller) as downloader:
    ...    blocks = downloader.get_blocks_iterator('my_volume', 'my_file')

    Note that since SXFileDownloader uses temporary files under the hood,
    further calls to .get_blocks_content_iterator() will return the cached
    version of the file (assuming it was initialized with cache_files=True).
    This means a significant speed up in consecutive calls.

    Also be warned that SXFileDownloader uses multiple threads and
    HTTP connections under the hood. Be sure to tune these resources
    to your needs (see the documentation for __init__ method).

    SXFileDownloader creates temporary files on disk. These files are used
    in order to parallelize download and to cache results. The default
    directory for temporary files is /tmp/python-sxclient and can be changed
    when initializing SXFileDownloader. If you wish to clean all the cached
    files, do:

        >>> tmp = '/my/tmp/files'
        >>> with sxclient.SXFileDownloader(sxcontroller, tmp_dir=tmp) as fd:
        ...     ...
        ...     fd.clean_cached_files()
    '''

    def __init__(
        self,
        sxcontroller,
        threads_no=DEFAULT_NUMBER_OF_THREADS,
        number_of_connections=DEFAULT_NUMBER_OF_CONNECTIONS,
        tmp_dir=DEFAULT_TMP_DIRECTORY,
        cache_files=True
    ):
        '''
        Arguments:
          - sxcontroller -- SXController instance.
          - threads_no -- Number of threads to be used with downloads
            (defaults to 20)
          - number_of_connections -- Pool of HTTP sessions (i.e. connections)
            to SX Cluster (defaults to 20)
          - tmp_dir -- Root directory to store temporary files
            (defaults to /tmp/python-sxclient)
          - cache_files -- If set to True downloader will cache files
            previously downloaded from SX Cluster and reuse them in
            consecutive calls (defaults to True)
        '''
        self._sxcontroller = sxcontroller
        self._connections = Queue.Queue()
        self._tmp_dir = os.path.join(
            tmp_dir, sxcontroller.get_cluster_uuid()
        )
        self._threads_no = threads_no
        self._thread_pool = ThreadPool(self._threads_no)
        self._connections_no = number_of_connections
        self._cache_files = cache_files
        self._initialized = False

    def _get_sxcontroller(self):
        # It just rotates connections
        conn = self._connections.get()
        self._connections.put(conn)
        return conn

    def _get_file_name(self, volume=None, path=None, rev=None):
        name = []
        if volume is not None:
            name.append(HASH_FN(volume).hexdigest())
        if path is not None:
            name.append(HASH_FN(path).hexdigest())
        if rev is not None:
            name.append(HASH_FN(rev).hexdigest())
        return '.'.join(name)

    def _create_tmp_dir_if_not_exists(self):
        if os.path.exists(self._tmp_dir):
            return
        os.makedirs(self._tmp_dir)

    def _create_tmp_file(self, size):
        self._create_tmp_dir_if_not_exists()
        file_name = '%s.tmp' % uuid.uuid4()
        full_name = os.path.join(self._tmp_dir, file_name)
        with LockedFile(full_name, 'wb', fcntl.LOCK_EX | fcntl.LOCK_NB) as fo:
            if size > 0:
                fo.seek(size - 1)
                fo.write('\0')
        return file_name

    def _stream_blocks_to_file(self, file_name, file_size, block_batch):
        # Simply downloads given blocks and puts them into a temporary
        # file exactly where they are supposed to be.
        sxcontroller = self._get_sxcontroller()
        node = block_batch[0]['node']
        size = block_batch[0]['size']
        block_batch = sorted(block_batch, key=lambda x: x['hash'])
        response = sxcontroller.getBlocks.call_on_node(
            node,
            size,
            [block['hash'] for block in block_batch]
        )

        with LockedFile(file_name, 'r+b', fcntl.LOCK_SH) as fo:
            for idx, block in enumerate(block_batch):
                offset = block['offset']
                block_size = block['size']
                lower = idx * size
                upper = (idx + 1) * size
                diff = file_size - offset - block_size
                if diff < 0:
                    upper += diff
                content = response.content[lower:upper]
                fo.seek(offset)
                fo.write(content)
                block['event'].set()

    def _unlock_block_batch(self, block_batch):
        for block in block_batch:
            block['event'].set()

    def _download_block(self, file_name, file_size, block_batch, context):
        if context.exception is not None:
            # Some other thread encountered an error. There's no point in
            # further download due to data corruption.
            self._unlock_block_batch(block_batch)
            return

        try:
            self._stream_blocks_to_file(file_name, file_size, block_batch)
        except Exception:
            exc_info = sys.exc_info()
            context.exception = (exc_info[1], None, exc_info[2])
            self._unlock_block_batch(block_batch)
            raise

    def _get_cached_iterator(self, full_name, batch_size):
        with LockedFile(full_name, 'rb', fcntl.LOCK_SH) as fo:
            data = fo.read(batch_size)
            while data:
                yield data
                data = fo.read(batch_size)

    def _get_blocks_data(self, file_data, block_size):
        blocks = []
        offset = 0
        while file_data:
            block = file_data.pop(0)
            for key, nodes in block.iteritems():
                # We assume that nodes are randomized anyway, so
                # nodes[0] should give a good granularity.
                node = nodes[0]
                blocks.append({
                    'hash': key,
                    'size': block_size,
                    'node': node,
                    'offset': offset,
                    'event': Event(),
                })
                offset += block_size
        return blocks

    def _put_tp_jobs(self, full_name, file_size, blocks, context):
        # Combine blocks that share common node.
        blocks_by_node = {}
        for block in blocks:
            nodes_per_block = blocks_by_node.setdefault(block['node'], [])
            nodes_per_block.append(block)

        block_batch = []
        for node, blocks in blocks_by_node.iteritems():
            for block in blocks:
                block_batch.append(block)
                if len(block_batch) >= DEFAULT_MAX_BLOCK_BATCH_SIZE:
                    self._thread_pool.process_task(
                        self._download_block, full_name, file_size,
                        block_batch, context
                    )
                    block_batch = []
            if block_batch:
                self._thread_pool.process_task(
                    self._download_block, full_name, file_size, block_batch,
                    context
                )
                block_batch = []

    def _get_sx_tmp_file_stream(
        self, path, file_size, file_data, block_size
    ):
        blocks = self._get_blocks_data(file_data, block_size)
        context = Context(exception=None, path=path)
        self._put_tp_jobs(path, file_size, blocks, context)

        last_block = None
        with LockedFile(path, 'rb', fcntl.LOCK_SH) as fo:
            while blocks:
                if last_block is None:
                    last_block = blocks.pop(0)
                timeout = not last_block['event'].wait(timeout=0.5)
                if timeout:
                    continue

                if context.exception:
                    raise context.exception

                # Since blocks are ordered anyway we don't have
                # to worry with seeks. Just read block-by-block.
                yield fo.read(block_size)
                last_block = None

    def _get_sx_iterator(
        self, file_name, file_size, file_data, block_size
    ):
        # What happens here is we create a 'random' temporary file and
        # then we stream data into it and yield from that file. Once we
        # do this we move that temporary file into other temporary file
        # which is uniquely identified by (cluster, volume, path) triple
        # (assuming cache_files is set to True). We do that so we can cache
        # the download and read from the saved file next time the downloader
        # is called.
        #
        # We don't stream directly to the target temporary file because
        # of race conditions. Note that we assume here that .rename()
        # operation is atomic (generally OS should guarantee that).
        #
        # Of course when downloading the same file parallelly we still
        # do heavy calls/streaming parallelly which is not necessary
        # (only one thread should do that). So this could be further
        # improved by using FS level locks (allowing only one download
        # per file) but that would increase complexity (possible deadlocks)
        # while cases of parallel download of the same file will probably be
        # rare anyway.
        tmp_fn = self._create_tmp_file(file_size)
        tmp_full = os.path.join(self._tmp_dir, tmp_fn)
        try:
            iterator = self._get_sx_tmp_file_stream(
                tmp_full, file_size, file_data, block_size
            )
            for chunk in iterator:
                yield chunk
        except Exception:
            os.remove(tmp_full)
            raise
        else:
            if self._cache_files:
                target_full = os.path.join(self._tmp_dir, file_name)
                os.rename(tmp_full, target_full)
            else:
                os.remove(tmp_full)

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def initialize(self):
        '''
        Creates a pool of connections and initializes underlying
        thread pool. Be sure to call .close() method after you're done
        working with the downloader.
        '''
        if self._initialized:
            raise RuntimeError('SXFileDownloader already initialized')

        from sxclient.controller import SXController
        for _ in xrange(self._connections_no):
            self._connections.put(
                SXController(
                    self._sxcontroller.cluster, self._sxcontroller._user_data
                )
            )
        self._thread_pool.start()
        self._initialized = True

    def close(self):
        '''
        Closes temporary connections used to download files and shutdowns
        underlying thread pool. This method is automatically called when
        using SXFileDownloader as a context manager (i.e. with statement).

        In case you use SXFileDownloader directly be sure to call this method
        after you're done.
        '''
        if not self._initialized:
            raise RuntimeError('SXFileDownloader not initialized')
        self._thread_pool.stop()
        while not self._connections.empty():
            try:
                conn = self._connections.get(timeout=0.1)
            except Queue.Empty:
                break
            conn.close()
        self._initialized = False

    def get_blocks_content_iterator(self, volume, path, revision=None):
        '''
        Parallelly downloads the file via a temporary file.

        Example usage:

            >>> import sxclient
            >>>
            >>> # initialize sx
            >>> cluster = sxclient.Cluster('my.cluster.example.com')
            >>> user_data = sxclient.UserData.from_key_path(
            ...    '/path/to/my/keyfile')
            >>> sxcontroller = sxclient.SXController(cluster, user_data)
            >>>
            >>> # download the file
            >>> with sxclient.SXFileDownloader(sxcontroller) as fd:
            ...     blocks = fd.get_blocks_iterator(
            ...         'my_volume', 'my_file')
            ...     for block_content in blocks:
            ...         print block_content
        '''

        volume_info = self._sxcontroller.locateVolume.json_call(
            volume, includeMeta=True
        )
        volume_filter = volume_info['volumeMeta'].get('filterActive')
        if volume_filter:
            raise NotImplementedError('Volume filters are not supported yet.')

        file_info = self._sxcontroller.getFile.json_call(
            volume, path, revision=revision
        )
        block_size = file_info['blockSize']
        file_size = file_info['fileSize']
        file_data = file_info['fileData']
        file_rev = file_info['fileRevision']

        self._create_tmp_dir_if_not_exists()
        tmp_file_name = self._get_file_name(volume, path, file_rev)
        tmp_full_name = os.path.join(self._tmp_dir, tmp_file_name)

        if os.path.exists(tmp_full_name):
            # simple case: the file is already cached on disk
            iterator = self._get_cached_iterator(tmp_full_name, block_size)
        else:
            # more difficult case, we have to download blocks first
            iterator = self._get_sx_iterator(
                tmp_file_name, file_size, file_data, block_size
            )

        for chunk in iterator:
            yield chunk

    def get_file_content(self, volume, path, revision=None):
        '''
        Downloads the file as a whole.

        WARNING: the entire file will be kept in memory so if you are
        dealing with big files use .get_blocks_content_iterator method instead.

        Example usage:

            >>> import sxclient
            >>>
            >>> # initialize sx
            >>> cluster = sxclient.Cluster('my.cluster.example.com')
            >>> user_data = sxclient.UserData.from_key_path(
            ...   '/path/to/my/keyfile')
            >>> sxcontroller = sxclient.SXController(cluster, user_data)
            >>>
            >>> # download the file
            >>> with sxclient.SXFileDownloader(sxcontroller) as fd:
            ...     content = fd.get_file_content(
            ...         'my_volume', 'my_file')
            >>> print content

        For more info see the class docs.
        '''
        return ''.join(
            self.get_blocks_content_iterator(volume, path, revision=revision)
        )

    def clean_cached_files(
        self, volume=None, file_name=None, revision=None
    ):
        '''
        Cleans cached files. By defining volume, file_name and/or revision
        you can create a pattern for file deletion, e.g.

            >>> downloader.clean_cached_files(volume='v')

        will delete all cached files for volume 'v', while:

            >>> downloader.clean_cached_files(volume='v', file_name='xyz')

        will delete all revisions of file 'v/xyz'.

        Note that some combinations, e.g.

            >>> downloader.clean_cached_files(file_name='xyz')

        are invalid. In the case above volume was not specified.
        '''
        args = (bool(volume), bool(file_name), bool(revision))
        if args not in (
            (False, False, False),
            (True, False, False),
            (True, True, False),
            (True, True, True),
        ):
            raise ValueError('Incorrect params')

        stats = {
            'found': 0,
            'deleted': 0
        }

        pattern = self._get_file_name(volume, file_name, revision)
        for file_name in os.listdir(self._tmp_dir):
            if file_name.startswith(pattern):
                stats['found'] += 1
                path = os.path.join(self._tmp_dir, file_name)
                lock_flag = fcntl.LOCK_EX | fcntl.LOCK_NB
                try:
                    with LockedFile(path, 'r+b', lock_flag):
                        os.remove(path)
                    stats['deleted'] += 1
                except IOError:
                    continue

        return stats
