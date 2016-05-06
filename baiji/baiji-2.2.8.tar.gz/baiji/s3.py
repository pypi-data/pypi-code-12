"""
Tools for interacting with Amazon S3.

This module seeks to be higher-level and easier to use than the boto library
provided by Amazon. It abstracts away whether you are writing to S3 or to a
local file, which is important for running code locally, or in an environment
where there is no connection to S3. It also adds some functionality that we
like, such as progress bars, "exclusive create", and context handlers (`with`)
for reading and writing.

The functionality provided by boto is relatively low level: it allows, for
example, setting an S3 key's contents from a string or local file, or pulling
a file from S3 into a local file.

"""
import os
import shutil
import re
from baiji.exceptions import InvalidSchemeException, S3Exception, KeyNotFound, KeyExists, get_transient_error_class
from baiji.util.parallel import ParallelWorker

# FIXME pylint: disable=too-many-lines

S3_MAX_UPLOAD_SIZE = 1024*1024*1024*5 # 5gb

# Path components in our s3 URIs are separated by slashes. Constant included not
# because it should ever change, but for semantic use in code. Remember that os.sep
# is '/' on MacOS and Linux and '\' on Windows.
sep = '/'

# The following convinence functions create a connection to s3 and execute the command

def cp(*args, **kwargs):
    return S3Connection().cp(*args, **kwargs)

def cp_r(*args, **kwargs):
    return S3Connection().cp_r(*args, **kwargs)

def rm(*args, **kwargs):
    return S3Connection().rm(*args, **kwargs)

def rm_r(*args, **kwargs):
    return S3Connection().rm_r(*args, **kwargs)

def ls(*args, **kwargs):
    return S3Connection().ls(*args, **kwargs)

def glob(*args, **kwargs):
    return S3Connection().glob(*args, **kwargs)

def info(*args, **kwargs):
    return S3Connection().info(*args, **kwargs)

def exists(*args, **kwargs):
    return S3Connection().exists(*args, **kwargs)

def size(*args, **kwargs):
    return S3Connection().size(*args, **kwargs)

def etag(*args, **kwargs):
    return S3Connection().etag(*args, **kwargs)

def md5(*args, **kwargs):
    return S3Connection().md5(*args, **kwargs)

def encrypt_at_rest(*args, **kwargs):
    return S3Connection().encrypt_at_rest(*args, **kwargs)

def mv(*args, **kwargs):
    return S3Connection().mv(*args, **kwargs)

def touch(*args, **kwargs):
    return S3Connection().touch(*args, **kwargs)

def sync_file(*args, **kwargs):
    return S3Connection().sync_file(*args, **kwargs)

def sync(*args, **kwargs):
    return S3Connection().sync(*args, **kwargs)

def get_url(*args, **kwargs):
    return S3Connection().get_url(*args, **kwargs)

def put_string(*args, **kwargs):
    return S3Connection().put_string(*args, **kwargs)

def get_string(*args, **kwargs):
    return S3Connection().get_string(*args, **kwargs)

def list_buckets(*args, **kwargs):
    return S3Connection().list_buckets(*args, **kwargs)

def bucket_info(*args, **kwargs):
    return S3Connection().bucket_info(*args, **kwargs)

def create_bucket(*args, **kwargs):
    return S3Connection().create_bucket(*args, **kwargs)

def open(key, mode='rb'): # pylint: disable=redefined-builtin
    '''
    Acts like open(key, mode), opening a file.

    If the file is on S3, it is downloaded and a NamedTemporaryFile is returned.

    The caller is responsible for closing the file descriptor, please try to
    use it in a with block.

    Like os.open, after stripping 'U' from the mode, the first character must
    be 'r' or 'w'. open also accepts 'x' for exclusive creation: it raises an
    exception if the file already exists. This is meant as a convenience and
    sanity check when you know the original file isn't supposed to exist.

    Note that 'x' is not suitable for preventing concurrent creation. This is
    due to the "eventually consistent" nature of s3, and also the CachedFile
    design. If two processes simultaneously write to the same file, there's a
    race condition. One or both will appear to succeed, and one will win out.
    Using 'x' doesn't -- can't -- prevent this.

    Raises s3.KeyNotFound when attempting to open a local or remote file that
    doesn't exist, s3.KeyExists when attempting exclusive create on an
    existing file or key, ValueError for an invalid key, and IOError for an
    underlying local file-system failure.

    '''
    return CachedFile(key, mode)


def _strip_initial_slashes(key):
    '''
    Keys going into boto need to not have initial slashes.
    '''
    return re.sub(r'^/*', '', key)


class S3CopyOperation(object):
    class CopyableKey(object):
        def __init__(self, key, connection):
            self.raw = key
            self.connection = connection
            self.parsed = path.parse(key)
            self.remote_path = None # value here will be set by the path setting, this just satisfies lint
            self.path = self.parsed.path
            if not (self.path.startswith(sep) or re.match(r'^[a-zA-Z]:', self.path)):
                self.path = sep + self.path
            self.bucket_name = self.parsed.netloc
            self.scheme = self.parsed.scheme
            if self.scheme not in ['file', 's3']:
                raise InvalidSchemeException("URI Scheme %s is not implemented" % self.scheme)
        @property
        def path(self):
            return self._path
        @path.setter
        def path(self, val):
            self._path = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init
            # For remote operations, we need a path without initial slashes
            self.remote_path = _strip_initial_slashes(self.path)
        @property
        def bucket(self):
            return self.connection._bucket(self.bucket_name) # pylint: disable=protected-access
        @property
        def uri(self):
            if self.is_file:
                return self.path
            else:
                return "s3://" + self.bucket_name + self.path
        @property
        def is_file(self):
            return self.scheme == 'file'
        @property
        def is_s3(self):
            return self.scheme == 's3'
        def exists(self):
            return self.connection.exists(self.uri)
        def etag(self):
            return self.connection.etag(self.uri)
        def rm(self):
            return self.connection.rm(self.uri)
        def lookup(self):
            if self.is_file:
                raise ValueError("S3CopyOperation.CopyableKey.lookup called for local file")
            key = self.bucket.lookup(self.remote_path)
            if not key:
                raise KeyNotFound("Error finding %s on s3: doesn't exist" % (self.uri))
            return key
        def create(self):
            if self.is_file:
                raise ValueError("S3CopyOperation.CopyableKey.create called for local file")
            from boto.s3.key import Key
            key = Key(self.bucket)
            key.key = self.remote_path
            return key

    def __init__(self, src, dst, connection):
        '''
        Both src and dst may be files or s3 keys
        '''
        self.connection = connection
        self.src = self.CopyableKey(src, connection)
        self.dst = self.CopyableKey(dst, connection)
        self.task = (self.src.scheme, self.dst.scheme)

        if path.isdirlike(self.dst.path):
            self.dst.path = os.path.join(self.dst.path, os.path.basename(self.src.path))

        # DEFAULTS:
        self.progress = False
        self.force = False
        self.policy = None
        self.preserve_acl = False
        self.encrypt = False
        self.encoding = None
        self.gzip = False
        self.content_type = None
        self.metadata = {}
        self.skip = False

        self.retries_allowed = 1
        self._retries = 0

        self.file_size = None

    @property # read only
    def retries_made(self):
        return self._retries

    @property
    def policy(self):
        return self._policy
    @policy.setter
    def policy(self, val):
        if val and self.dst.is_file:
            raise ValueError("Policy only allowed when copying to s3")
        self._policy = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def preserve_acl(self):
        return self._preserve_acl
    @preserve_acl.setter
    def preserve_acl(self, val):
        val = bool(val)
        if val and self.task != ('s3', 's3'):
            raise ValueError("Preserve ACL only allowed when copying from s3 to s3")
        self._preserve_acl = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def progress(self):
        return self._progress
    @progress.setter
    def progress(self, val):
        val = bool(val)
        self._progress = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def force(self):
        return self._force
    @force.setter
    def force(self, val):
        val = bool(val)
        self._force = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def skip(self):
        return self._skip_exist
    @skip.setter
    def skip(self, val):
        val = bool(val)
        self._skip_exist = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def encrypt(self):
        return self._encrypt
    @encrypt.setter
    def encrypt(self, val):
        val = bool(val) and self.dst.is_s3
        self._encrypt = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def validate(self):
        return self._validate
    @validate.setter
    def validate(self, val):
        self._validate = bool(val) # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def encoding(self):
        return self._encoding
    @encoding.setter
    def encoding(self, val):
        if val is not None and self.dst.is_file:
            raise ValueError("Encoding can only be specified when copying to s3")
        if val is not None and self.gzip and val != 'gzip':
            raise ValueError("gzip overrides explicit encoding")
        self._encoding = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def gzip(self):
        return self._gzip
    @gzip.setter
    def gzip(self, val):
        val = bool(val)
        if val and self.task != ('file', 's3'):
            raise ValueError("gzip can only be specified when uploading to s3")
        if val and self.encoding is not None and self.encoding != 'gzip':
            raise ValueError("gzip overrides explicit encoding")
        self._gzip = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def content_type(self):
        return self._content_type
    @content_type.setter
    def content_type(self, val):
        if val is not None and self.dst.is_file:
            raise ValueError("Content Type can only be specified when copying to s3")
        self._content_type = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init
    def guess_content_type(self):
        import mimetypes
        content_type, _ = mimetypes.guess_type(self.src.path)
        if not content_type and self.is_extensionless_html():
            content_type = 'text/html'
        elif not content_type:
            content_type = 'application/octet-stream'
        self.content_type = content_type
    def is_extensionless_html(self):
        # test if file has no extension and html5 doctype in first 100 bytes
        if os.path.splitext(self.src.path)[-1] == '':
            if self.encoding == 'gzip':
                import gzip
                with gzip.open(self.src.path, 'rb') as f:
                    return '<!DOCTYPE html>' in f.read(100)
            else:
                with open(self.src.path, 'r') as f:
                    return '<!DOCTYPE html>' in f.read(100)
        else:
            return False


    @property
    def metadata(self):
        meta = self._metadata
        if self.encoding is not None:
            meta['Content-Encoding'] = self.encoding
        if self.content_type is not None:
            meta['Content-Type'] = self.content_type
        return meta
    @metadata.setter
    def metadata(self, val):
        if not (val is None or val == {}) and self.dst.is_file:
            raise ValueError("Metadata can only be specified when copying to s3")
        if val is None:
            val = {}
        self._metadata = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    def execute(self):
        from boto.s3.connection import S3ResponseError
        if not self.force and self.dst.exists():
            if self.skip:
                import warnings
                warnings.warn("Skipping existing destination copying %s to %s: Destinaton exists" % (self.src.uri, self.dst.uri))
                return
            else:
                raise KeyExists("Error copying %s to %s: Destinaton exists" % (self.src.uri, self.dst.uri))

        if self.dst.is_file:
            self.prep_local_destination()

        try:
            if self.task == ('file', 'file'):
                self.local_copy()
            elif self.task == ('file', 's3'):
                self.upload()
            elif self.task == ('s3', 'file'):
                self.download()
            elif self.task == ('s3', 's3'):
                self.remote_copy()
            else:
                raise InvalidSchemeException("Copy for URI Scheme %s to %s is not implemented" % self.task)

        except (IOError, KeyNotFound):
            raise KeyNotFound("Error copying %s to %s: Source doesn't exist" % (self.src.uri, self.dst.uri))
        except S3ResponseError as e:
            if e.status == 403:
                raise S3Exception("HTTP Error 403: Permission Denied on {}".format(" or ".join([x.uri for x in [self.src, self.dst] if x.is_s3])))
            else:
                raise

    def local_copy(self):
        shutil.copy(self.src.path, self.dst.path)

    def upload(self):
        if self.gzip:
            import gzip
            from baiji.util import tempfile
            with tempfile.NamedTemporaryFile() as compressed_src:
                with open(self.src.path, 'rb') as f:
                    with gzip.open(compressed_src.name, 'wb') as tf:
                        tf.writelines(f)
                self.src.path = compressed_src.name
                self.encoding = 'gzip'
                self._upload()
        else:
            self._upload()

    def _upload(self):
        self.file_size = os.path.getsize(self.src.path)
        if self.file_size > S3_MAX_UPLOAD_SIZE:
            self.upload_multipart()
        else:
            self.upload_direct()

    def upload_multipart(self):
        import math
        from baiji.util.with_progressbar import FileTransferProgressbar
        with FileTransferProgressbar(supress=(not self.progress), maxval=self.file_size) as cb:
            mp = self.dst.bucket.initiate_multipart_upload(self.dst.remote_path, encrypt_key=self.encrypt, metadata=self.metadata)
            n_parts = int(math.ceil(float(self.file_size) / S3_MAX_UPLOAD_SIZE))
            try:
                for ii in range(n_parts):
                    with open(self.src.path, 'r') as fp:
                        fp.seek(S3_MAX_UPLOAD_SIZE*ii)
                        part_size = self.file_size - S3_MAX_UPLOAD_SIZE*ii if ii+1 == n_parts else S3_MAX_UPLOAD_SIZE
                        cb.minval = S3_MAX_UPLOAD_SIZE*ii
                        num_cb = part_size / (1024*1024)
                        mp.upload_part_from_file(fp=fp, part_num=ii+1, size=part_size, cb=cb, num_cb=num_cb)
                mp.complete_upload()
            except:
                mp.cancel_upload()
                raise

    def upload_direct(self):
        import math
        from baiji.util.with_progressbar import FileTransferProgressbar
        key = self.dst.create()
        for k, v in self.metadata.items():
            key.set_metadata(k, v)
        with FileTransferProgressbar(supress=(not self.progress)) as cb:
            num_cb = max([10, int(math.ceil(float(self.file_size) / (1024*1024)))])
            key.set_contents_from_filename(self.src.path, cb=cb, policy=self.policy, encrypt_key=self.encrypt, num_cb=num_cb)

    def download(self):
        '''
        Download to local file

        If `validate` is set, check etags and retry once if not match.
        Raise TransientError when download is corrupted again after retry

        '''
        from baiji.util import tempfile
        from baiji.util.with_progressbar import FileTransferProgressbar
        # We create, close, and delete explicitly rather than using
        # a `with` block, since on windows we can't have a file open
        # twice by the same process.
        tf = tempfile.NamedTemporaryFile(delete=False)
        try:
            key = self.src.lookup()

            with FileTransferProgressbar(supress=(not self.progress)) as cb:
                key.get_contents_to_file(tf, cb=cb)
            tf.close()

            if self.validate:
                self.ensure_integrity(tf.name)

            # We only actually write to dst.path if the download succeeds and
            # if necessary is validated. This avoids leaving partially
            # downloaded files if something goes wrong.
            shutil.copy(tf.name, self.dst.path)

        except (get_transient_error_class(), KeyNotFound) as retryable_error:
            # Printed here so that papertrail can alert us when this occurs
            print retryable_error

            # retry once or raise
            if self.retries_made < self.retries_allowed:
                self._retries += 1
                self.download()
            else:
                raise

        finally:
            self.connection.rm(tf.name)

    def ensure_integrity(self, filename):
        '''
        Ensure integrity of downloaded file; raise TransientError if there's a mismatch
        '''
        if self.connection.etag(filename) != self.src.etag():
            raise get_transient_error_class()('Destinaton file for ({}) is corrupted, retry count {}'.format(self.src.uri, self.retries_made))

    def remote_copy(self):
        '''
        With copy_key, if metadata is None, it will be copied from the existing key
        '''
        src = self.src.remote_path
        headers = {}
        if self.policy:
            headers['x-amz-acl'] = self.policy
        key = self.src.lookup()
        meta = key.metadata
        meta['Content-Encoding'] = key.content_encoding
        meta['Content-Type'] = key.content_type
        meta = dict(meta.items() + self.metadata.items())
        self.dst.bucket.copy_key(self.dst.remote_path, self.src.bucket_name, src, preserve_acl=self.preserve_acl, metadata=meta, headers=headers, encrypt_key=self.encrypt)
        if self.progress:
            print 'Copied %s to %s' % (self.src.uri, self.dst.uri)

    def prep_local_destination(self):
        from baiji.util.shutillib import mkdir_p
        mkdir_p(os.path.dirname(self.dst.path))


class MultifileCopyWorker(ParallelWorker):
    '''
    This is a pickleable worker used for parallel copy operations.
    '''
    def __init__(self, kwargs_for_cp):
        self.connection = S3Connection(cache_buckets=True)
        self.kwargs_for_cp = kwargs_for_cp
        self.verbose = self.kwargs_for_cp.get('progress', False)
        if 'progress' in self.kwargs_for_cp:
            self.kwargs_for_cp['progress'] = False
        super(MultifileCopyWorker, self).__init__()

    def on_run(self, file_from, file_to):
        try:
            self.connection.cp(file_from, file_to, **self.kwargs_for_cp)
            if self.verbose:
                print "Finished transfering {} to {}".format(file_from, file_to)
        except KeyExists as e:
            # Note here that the correct behavior would probably be to roll back
            # if we encounter an error, but that's not practical, so we copy
            # what we can and show an error about the rest.
            print str(e)


class S3Connection(object):
    def __init__(self, cache_buckets=False):
        self._connected = False
        self._conn = None
        self.cache_buckets = cache_buckets
        self._known_valid_buckets = set()

    @property
    def conn(self):
        from boto.s3.connection import S3Connection as BotoS3Connection
        from boto.s3.connection import OrdinaryCallingFormat
        from baiji.config import credentials
        if not self._connected:
            self._conn = BotoS3Connection(credentials.key, credentials.secret,
                                          calling_format=OrdinaryCallingFormat(),
                                          suppress_consec_slashes=False)
            self._connected = True
        return self._conn

    def _bucket(self, name, cache_buckets=None):
        '''
        The call to `get_bucket` will make a HEAD request to S3 and raise S3ResponseError if the bucket doesn't exist.
        If we pass `validate=False` then it won't make the request, but it's behavor will be undefined if the bucket doesn't
        exist. So we don't want to not validate buckets in general, because that'd break things, but if we've seen the bucket
        before, then it's very likely that we'll see it again.

        We support an object wide cache_buckets, or we can pass cache_buckets just to this call, which will override the
        object wide value.
        '''
        from boto.s3.connection import S3ResponseError
        if cache_buckets is None:
            cache_buckets = self.cache_buckets
        try:
            if cache_buckets:
                if name in self._known_valid_buckets:
                    return self.conn.get_bucket(name, validate=False)
                else:
                    bucket = self.conn.get_bucket(name) # this will raise if the bucket isn't valid
                    self._known_valid_buckets.add(name)
                    return bucket
            else:
                return self.conn.get_bucket(name)
        except S3ResponseError as e:
            if e.status == 403:
                raise S3Exception("HTTP Error 403: Permission Denied on s3://{}/".format(name))
            else:
                raise

    def _lookup(self, bucket_name, key, cache_buckets=None):
        '''
        See _bucket for the details on cache_buckets
        '''
        key = _strip_initial_slashes(key)
        return self._bucket(bucket_name, cache_buckets=cache_buckets).lookup(key)

    def cp(self, key_or_file_from, key_or_file_to, force=False, progress=False, policy=None, preserve_acl=False, encoding=None, encrypt=True, gzip=False, content_type=None, guess_content_type=False, metadata=None, skip=False, validate=True):
        """
        Copy file to or from AWS S3

        Both the from and to arguments can be either local paths or s3 urls (e.g. ``s3://bucketname/path/in/bucket``).

        If the target exists, the an exception is raised unless ``force=True`` is given.

        When copying from file to s3, you can optionally specify a canned acl policy,
        e.g. `policy='public-read'`. For possible values, see boto.s3.acl.CannedACLStrings.

        When copying from s3 to s3, you can specify preserve_acl=True to copy the
        existing ACL to the new file. With preserve_acl=False it will inherit the
        new bucket's policy.
        """

        op = S3CopyOperation(key_or_file_from, key_or_file_to, connection=self)
        op.progress = progress
        op.force = force
        op.policy = policy
        op.preserve_acl = preserve_acl
        op.encrypt = encrypt
        op.encoding = encoding
        op.gzip = gzip
        op.metadata = metadata
        op.skip = skip
        op.validate = validate

        if guess_content_type:
            op.guess_content_type()
        else:
            op.content_type = content_type

        op.execute()

    def cp_r(self, dir_from, dir_to, parallel=False, **kwargs):
        '''
        kwargs are passed on directly to s3.cp; see defaults there.
        '''
        (from_scheme, _, from_path, _, _, _) = path.parse(dir_from)
        if from_scheme == 'file':
            files_to_copy = [(path.join(dir_from, f), path.join(dir_to, f))
                             for f in ls(dir_from, return_full_urls=False)]
        else:
            if from_path.endswith(sep):
                # Emulate `cp`, which copies the contents of the path.
                # Get path relative to from_path
                files_to_copy = [(f, path.join(dir_to, os.path.relpath(path.parse(f).path, from_path)))
                                 for f in ls(dir_from, return_full_urls=True)]
            else:
                # Get path relative to from_path's parent
                # Since from_path has no '/', we can get this with os.path.dirname()
                files_to_copy = [(f, path.join(dir_to, os.path.relpath(path.parse(f).path, os.path.dirname(from_path))))
                                 for f in ls(dir_from, return_full_urls=True)]

        if 'force' not in kwargs or not kwargs['force']:
            # we're not supposed to overwrite. Locally this is easy, since `exists` checks are cheap, but
            # on s3, it's more expensive, so we avoid it if possible:
            if path.isremote(dir_to):
                def common_prefix(a, b):
                    try:
                        ind = [x == y for x, y in zip(a, b)].index(False)
                    except ValueError:
                        return a
                    return a[:ind]
                destinations = [y for _, y in files_to_copy]
                prefix = reduce(common_prefix, destinations[1:], destinations[0])
                try:
                    # note that we can't use `exists` here, as it only works for full keys
                    self.ls(prefix).next()
                except StopIteration:
                    # There's nothing in the iterator, so there are no files to be found, so
                    # we set force for the copy so that we don't have to check each one:
                    kwargs['force'] = True

        if parallel:
            from baiji.util.parallel import parallel_for
            parallel_for(files_to_copy, MultifileCopyWorker, args=[kwargs], num_processes=12)
        else:
            for file_from, file_to in files_to_copy:
                try:
                    # Note here that the correct behavior would probably be to roll back
                    # if we encounter an error, but that's not practical, so we copy
                    # what we can and show an error about the rest.
                    self.cp(file_from, file_to, **kwargs)
                except KeyExists as e:
                    print str(e)

    def rm(self, key_or_file):
        '''
        Remove a key from AWS S3
        '''
        k = path.parse(key_or_file)
        if k.scheme == 'file':
            if os.path.isdir(k.path):
                shutil.rmtree(k.path)
            elif os.path.exists(k.path):
                return os.remove(k.path)
            else:
                raise KeyNotFound("%s does not exist" % key_or_file)
        elif k.scheme == 's3':
            if not exists(key_or_file):
                raise KeyNotFound("%s does not exist" % key_or_file)
            return self._bucket(k.netloc).delete_key(_strip_initial_slashes(k.path))
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def rm_r(self, key_or_file, force=False, quiet=False):
        '''
        Prompts for confirmation on each file when force is False.

        Raises an exception when not using AWS.
        '''
        k = path.parse(key_or_file)
        if not k.scheme == 's3':
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)
        bucket = k.netloc
        keys_to_delete = self.ls(key_or_file)
        for key_to_delete in keys_to_delete:
            url = "s3://%s%s" % (bucket, key_to_delete)
            if not force:
                from baiji.util.console import confirm
                if not confirm("Remove %s" % url):
                    continue
            self.rm(url)
            if not quiet:
                print "[deleted] %s" % url

    def ls(self, s3prefix, return_full_urls=False, require_s3_scheme=False, shallow=False, followlinks=False):
        '''
        List files on AWS S3
        prefix is given as an S3 url: ``s3://bucket-name/path/to/dir``.
        It will return all values in the bucket that have that prefix.

        Note that ``/dir/filename.ext`` is found by ``ls('s3://bucket-name/dir/fil')``; it's really a prefix and not a directory name.

        A local prefix generally is acceptable, but if require_s3_scheme
        is True, the prefix must be an s3 URL.

        If `shallow` is `True`, the key names are processed hierarchically
        using '/' as a delimiter, and only the immediate "children" are
        returned.

        '''
        import itertools
        k = path.parse(s3prefix)
        if k.scheme == 's3':
            prefix = k.path
            if prefix.startswith(sep):
                prefix = prefix[len(sep):]
            delimiter = shallow and sep or ''
            if return_full_urls:
                clean_paths = lambda x: "s3://" + k.netloc + sep + x.name
            else:
                clean_paths = lambda x: sep + x.name
            return itertools.imap(clean_paths, self._bucket(k.netloc).list(prefix=prefix, delimiter=delimiter))
        elif k.scheme == 'file':
            if require_s3_scheme:
                raise InvalidSchemeException('URI should begin with s3://')
            paths = []
            remove = ''
            if not return_full_urls:
                remove = k.path
                if not remove.endswith(os.sep):
                    remove += os.sep
            for root, _, files in os.walk(k.path, followlinks=followlinks):
                for f in files:
                    # On Windows, results of os.abspath() and os.walk() have '\',
                    # so we replace them with '/'
                    paths.append(path.join(root, f).replace(remove, '').replace(os.sep, sep))
                if shallow:
                    break
            return paths
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def glob(self, prefix, pattern):
        '''
        Given a path prefix and a pattern, iterate over matching paths.

        e.g.

        paths = list(s3.glob(
            prefix='s3://bodylabs-ants-go-marching/output/feet_on_floor/eff2a0e/',
            pattern='*_alignment.ply'
        ))

        '''
        import fnmatch
        import functools
        import itertools
        predicate = functools.partial(fnmatch.fnmatch, pat=prefix + pattern)
        listing = ls(prefix, return_full_urls=True)
        return itertools.ifilter(predicate, listing)

    def info(self, key_or_file):
        '''
        Get info about a file
        '''
        from datetime import datetime
        k = path.parse(key_or_file)
        result = {
            'uri': '%s://%s%s' % (k.scheme, k.netloc, k.path),
        }
        if k.scheme == 'file':
            if not os.path.exists(k.path):
                raise KeyNotFound("Error getting info on %s: File doesn't exist" % (key_or_file, ))
            stat = os.stat(k.path)
            result['size'] = stat.st_size
            result['last_modified'] = datetime.fromtimestamp(stat.st_mtime)
        elif k.scheme == 's3':
            remote_object = self._lookup(k.netloc, k.path)
            if remote_object is None:
                raise KeyNotFound("Error getting info on %s: Key doesn't exist" % (key_or_file, ))
            result['size'] = remote_object.size
            result['last_modified'] = datetime.strptime(remote_object.last_modified, "%a, %d %b %Y %H:%M:%S GMT")
            result['content_type'] = remote_object.content_type
            result['content_encoding'] = remote_object.content_encoding
            result['encrypted'] = bool(remote_object.encrypted)
            result['acl'] = remote_object.get_acl()
            result['owner'] = remote_object.owner
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)
        return result

    def exists(self, key_or_file, retries_allowed=3):
        '''
        Check if a file exists on AWS S3

        Returns a boolean.

        If the key is not found then we recheck up to `retries_allowed` times. We only do this
        on s3. We've had some observations of what appears to be eventual consistency, so this
        makes it a bit more reliable. This does slow down the call in the case where the key
        does not exist.

        On a relatively slow, high latency connection a test of 100 tests retreiving a
        non-existant file gives:

        With retries_allowed=1: median=457.587 ms, mean=707.12387 ms
        With retries_allowed=3: median=722.969 ms, mean=1185.86299 ms
        with retries_allowed=10: median=2489.767 ms, mean=2995.34233 ms
        With retries_allowed=100: median=24694.0815 ms, mean=26754.64137 ms

        So assume that letting retries_allowed=3 will cost you a bit less than double the time.
        '''
        k = path.parse(key_or_file)
        if k.scheme == 'file':
            return os.path.exists(k.path)
        elif k.scheme == 's3':
            retry_attempts = 0
            while retry_attempts < retries_allowed:
                key_exists = self._lookup(k.netloc, k.path, cache_buckets=True) is not None
                if key_exists:
                    if retry_attempts > 0: # only if we find it after failing at least once
                        import warnings
                        from baiji.exceptions import EventualConsistencyWarning
                        warnings.warn("S3 is behaving in an eventually consistent way in s3.exists({}) -- it took {} attempts to locate the key".format(key_or_file, retry_attempts+1), EventualConsistencyWarning)
                    return True
                retry_attempts += 1
            return False
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def size(self, key_or_file):
        '''
        Return the size of a file. If it's on s3, don't download it.
        '''
        k = path.parse(key_or_file)
        if k.scheme == 'file':
            return os.path.getsize(k.path)
        elif k.scheme == 's3':
            k = self._lookup(k.netloc, k.path)
            if k is None:
                raise KeyNotFound("s3://%s/%s not found on s3" % (k.netloc, k.path))
            return k.size
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def _get_etag(self, netloc, remote_path):
        k = self._lookup(netloc, remote_path)
        if k is None:
            raise KeyNotFound("s3://%s/%s not found on s3" % (netloc, remote_path))
        return k.etag.strip("\"") # because s3 seriously gives the md5sum back wrapped in an extra set of double quotes...

    def etag(self, key_or_file):
        '''
        Return the s3 etag of the file. For files less than 5gb, this is the same as md5.
        '''
        k = path.parse(key_or_file)
        if k.scheme == 'file':
            import math
            import struct
            import hashlib
            from baiji.util.md5 import md5_for_file
            file_size = os.path.getsize(k.path)
            if file_size > S3_MAX_UPLOAD_SIZE:
                n_parts = int(math.ceil(float(file_size) / S3_MAX_UPLOAD_SIZE))
                starts = [ii*S3_MAX_UPLOAD_SIZE for ii in range(n_parts)]
                ends = [(ii+1)*S3_MAX_UPLOAD_SIZE for ii in range(n_parts)]
                ends[-1] = None
                hashes = [md5_for_file(k.path, start=start, end=end) for start, end in zip(starts, ends)]
                md5_digester = hashlib.md5()
                for h in hashes:
                    md5_digester.update(struct.pack("!16B", *[int(h[x:x+2], 16) for x in range(0, len(h), 2)]))
                return md5_digester.hexdigest() + "-%d" % n_parts
            else:
                return md5_for_file(k.path)
        elif k.scheme == 's3':
            return self._get_etag(k.netloc, k.path)
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def md5(self, key_or_file):
        '''
        Return the MD5 checksum of a file. If it's on s3, don't download it.
        '''
        k = path.parse(key_or_file)
        if k.scheme == 'file':
            from baiji.util.md5 import md5_for_file
            return md5_for_file(k.path)
        elif k.scheme == 's3':
            res = self._get_etag(k.netloc, k.path)
            if "-" in res:
                raise Exception("md5 hashes not availiable from s3 for files over 5gb")
            return res
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def encrypt_at_rest(self, key):
        '''
        This method takes a key on s3 and encrypts it.
        Note that calling this method on a local file is an error
        and that calling it on an s3 key that is already encrypted,
        while allowed, is a no-op.
        '''
        k = path.parse(key)
        if k.scheme != 's3':
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)
        remote_object = self._lookup(k.netloc, k.path)
        if remote_object is None:
            raise KeyNotFound("Error encrypting %s: Key doesn't exist" % (key, ))
        if not bool(remote_object.encrypted):
            bucket = self._bucket(k.netloc)
            src = k.path
            if src.startswith(sep):
                src = src[len(sep):] # NB: copy_key is failing with absolute src keys...
            bucket.copy_key(src, k.netloc, src, preserve_acl=True, metadata=None, encrypt_key=True)

    def mv(self, key_or_file_from, key_or_file_to, **kwargs):
        """
        Move file to or from AWS S3

        Both the from and to arguments can be either local paths or s3 urls (e.g. ``s3://bucketname/path/in/bucket``).

        If the target exists, the an exception is raised unless ``force=True`` is given.
        kwargs are passed directly on to s3.cp; see there for defaults.
        """
        self.cp(key_or_file_from, key_or_file_to, **kwargs)
        self.rm(key_or_file_from)

    def touch(self, key, encrypt=True):
        """
        Touch a local file or a path on s3

        Locally, this is analagous to the unix touch command

        On s3, it creates an empty file if there is not one there already,
        but does not change the timestamps (not possible to do without
        actually moving the file)
        """
        if path.islocal(key):
            from bodylabs.util.shutillib import touch as _touch
            _touch(path.parse(key).path)
        else:
            # The replace=False here means that we only take action if
            # the file doesn't exist, so we don't accidentally truncate
            # files when we just mean to be touching them
            self.put_string(key, '', encrypt=encrypt, replace=False)

    def sync_file(self, src, dst, update=True, delete=False, progress=False, policy=None, encoding=None, encrypt=True, guess_content_type=False):
        '''
        Sync a file from src to dst.

        update: When True, update dst if it exists but contents do not match.
        delete: When True, remove dst if src does not exist. When False, raise
          an error if src does not exist.
        '''
        from baiji.util.console import create_conditional_print
        print_verbose = create_conditional_print(progress)

        src_exists = self.exists(src)
        if not delete and not src_exists:
            raise KeyNotFound(
                "Error syncing {} to {}: Source doesn't exist".format(src, dst))

        dst_exists = self.exists(dst)

        needs_delete = dst_exists and not src_exists
        needs_fresh_copy = src_exists and not dst_exists
        needs_update = dst_exists and src_exists and self.etag(src) != self.etag(dst)

        if not needs_delete and not needs_fresh_copy and not needs_update:
            print_verbose('{} is up to date'.format(dst))
            return

        # At this point, exactly one of these should be true.
        assert needs_delete ^ needs_fresh_copy ^ needs_update

        if needs_fresh_copy:
            print_verbose('copying {} to {}'.format(src, dst))
            self.cp(src, dst, force=False, progress=progress, policy=policy, encoding=encoding, encrypt=encrypt, guess_content_type=guess_content_type)
        elif needs_update:
            print_verbose('file is out of date: {}'.format(dst))
            if update:
                print_verbose('copying {} to {}'.format(src, dst))
                self.cp(src, dst, force=True, progress=progress, policy=policy, encoding=encoding, encrypt=encrypt, guess_content_type=guess_content_type)
        elif needs_delete:
            print_verbose('source file does not exist: {}'.format(src))
            if delete:
                print_verbose('removing {}'.format(dst))
                self.rm(dst)

    def sync(self, key_or_dir_from, key_or_dir_to, followlinks=True, do_not_delete=None, progress=False, policy=None, encoding=None, encrypt=True, guess_content_type=False):
        '''
        Sync a directory of files.

        Note these src and dst paths must be directories. Use `s3.sync_file`
        for files.

        do_not_delete: Paths not to delete during syncing, useful for syncing root
          content in a bucket when other apps are responsible for filling in
          subfolders.

        '''
        def clean_path(key_or_dir):
            if path.islocal(key_or_dir) and not os.path.isdir(key_or_dir):
                raise ValueError("s3 sync requires directories")
            if path.islocal(key_or_dir):
                key_or_dir = os.path.abspath(key_or_dir)
            if not key_or_dir.endswith('/'):
                key_or_dir += '/'
            return key_or_dir

        key_or_dir_from = clean_path(key_or_dir_from)
        key_or_dir_to = clean_path(key_or_dir_to)

        src_files = [x.replace(key_or_dir_from, '') for x in self.ls(key_or_dir_from, return_full_urls=True, followlinks=followlinks)]
        dst_files = [x.replace(key_or_dir_to, '') for x in self.ls(key_or_dir_to, return_full_urls=True, followlinks=followlinks)]
        for f in src_files:
            src = key_or_dir_from + f
            dst = key_or_dir_to + f
            self.sync_file(src, dst, progress=progress, policy=policy, encoding=encoding, encrypt=encrypt, guess_content_type=guess_content_type)

        do_not_delete = [] if do_not_delete is None else do_not_delete
        do_not_delete = [x if x.endswith('/') else x + '/' for x in do_not_delete]
        for f in set(dst_files) - set(src_files):
            removed_file = key_or_dir_to + f
            if any([f.startswith(x) for x in do_not_delete]):
                if progress:
                    print "leaving alone", removed_file
            else:
                if progress:
                    print "removing", removed_file
                self.rm(removed_file)

    def get_url(self, key, ttl):
        """
        Get a temporary https url for a file on AWS S3

        Returns the url as a string.
        The url will timeout and return an error after ``ttl`` seconds.
        """
        k = path.parse(key)
        return self._lookup(k.netloc, k.path).generate_url(ttl)

    def put_string(self, key, s, encrypt=True, replace=True):
        '''
        Save string ``s`` to S3 as ``key``.

        If ``replace=True``, this will overwrite an existing key.
        If ``replace=false``, this will be a no-op when the key already exists.

        '''
        from boto.s3.key import Key
        key = path.parse(key)
        b = self._bucket(key.netloc)
        k = Key(b)
        k.key = _strip_initial_slashes(key.path)
        k.set_contents_from_string(s, encrypt_key=encrypt, replace=replace)

    def get_string(self, key):
        '''
        Get string stored in S3 ``key``.
        '''
        k = path.parse(key)
        return self._lookup(k.netloc, k.path).get_contents_as_string()

    def open(self, key, mode='rb'): # pylint: disable=redefined-builtin
        '''
        Acts like open(key, mode), opening a file.

        If the file is on S3, it is downloaded and a NamedTemporaryFile is returned.

        The caller is responsible for closing the file descriptor, please try to
        use it in a with block.

        Like os.open, after stripping 'U' from the mode, the first character must
        be 'r' or 'w'. open also accepts 'x' for exclusive creation: it raises an
        exception if the file already exists. This is meant as a convenience and
        sanity check when you know the original file isn't supposed to exist.

        Note that 'x' is not suitable for preventing concurrent creation. This is
        due to the "eventually consistent" nature of s3, and also the CachedFile
        design. If two processes simultaneously write to the same file, there's a
        race condition. One or both will appear to succeed, and one will win out.
        Using 'x' doesn't -- can't -- prevent this.

        Raises s3.KeyNotFound when attempting to open a local or remote file that
        doesn't exist, s3.KeyExists when attempting exclusive create on an
        existing file or key, ValueError for an invalid key, and IOError for an
        underlying local file-system failure.

        '''
        return CachedFile(key, mode, connection=self)

    def list_buckets(self):
        '''
        List all the buckets availiable on AWS S3 for the credentialed account.
        '''
        return [x.name for x in self.conn.get_all_buckets()]

    def bucket_info(self, name):
        '''
        Get info about a bucket
        '''
        bucket = self._bucket(name)
        def safe_get(method):
            from boto import exception
            try:
                return getattr(bucket, method)()
            except exception.S3ResponseError:
                return None
        return {
            'name': name,
            'lifecycle': safe_get('get_lifecycle_config'),
            'cors': safe_get('get_cors'),
            'location': safe_get('get_location'),
            'logging_status': safe_get('get_logging_status'),
            'policy': safe_get('get_policy'),
            'versioning_status': safe_get('get_versioning_status'),
            'website_configuration': safe_get('get_website_configuration'),
            'website_endpoint': safe_get('get_website_endpoint'),
        }

    def create_bucket(self, name):
        return self.conn.create_bucket(name)


class FileMode(object):
    def __init__(self, mode, allowed_modes=None):
        self.mode = mode
        self._modes = set(mode)
        if self._modes - set('arwxb+tU') or len(self.mode) > len(self._modes):
            raise ValueError('Invalid mode')
        if allowed_modes:
            if self._modes - set(allowed_modes):
                raise NotImplementedError('CachedFile does not support mode %s' % "".join(self._modes - set(allowed_modes)))

        if 'U' in self._modes:
            raise NotImplementedError('s3.open does not support universal newline mode')
        self.reading = 'r' in self._modes
        self.writing = 'w' in self._modes
        self.creating_exclusively = 'x' in self._modes
        self.appending = 'a' in self._modes
        self.updating = '+' in self._modes
        self.text = 't' in self._modes
        self.binary = 'b' in self._modes
        if self.text and self.binary:
            raise ValueError("can't have text and binary mode at once")
        if self.reading + self.writing + self.appending + self.creating_exclusively > 1:
            raise ValueError("can't have read/write/append/exclusive create mode at once")
        if not (self.reading or self.writing or self.appending or self.creating_exclusively):
            raise ValueError("must have exactly one of read/write/append/exclusive create mode")

    @property
    def is_output(self):
        return self.writing or self.appending or self.creating_exclusively

    @property
    def flags(self):
        '''
        Adapted from http://hg.python.org/cpython/file/84cf25da86e8/Lib/_pyio.py#l154

        See also open(2) which explains the modes

        os.O_BINARY and os.O_TEXT are only available on Windows.
        '''
        return (
            ((self.reading and not self.updating) and os.O_RDONLY or 0) |
            ((self.writing and not self.updating) and os.O_WRONLY or 0) |
            ((self.creating_exclusively and not self.updating) and os.O_EXCL or 0) |
            (self.updating and os.O_RDWR or 0) |
            (self.appending and os.O_APPEND or 0) |
            ((self.writing or self.creating_exclusively) and os.O_CREAT or 0) |
            (self.writing and os.O_TRUNC or 0) |
            ((self.binary and hasattr(os, 'O_BINARY')) and os.O_BINARY or 0) |
            ((self.text and hasattr(os, 'O_TEXT')) and os.O_TEXT or 0)
        )

class CachedFile(object):
    '''
    CachedFile('s3://bucket/path/to/file.ext', 'r') downloads the file and opens it for reading
    CachedFile('s3://bucket/path/to/file.ext', 'w') opens a temp file for writing and uploads it on close
    CachedFile('s3://bucket/path/to/file.ext', 'x') verifies that the file doesn't exist on s3, then behaves like 'w'
    '''
    def __init__(self, key, mode='r', connection=None, encrypt=True):
        self.encrypt = encrypt
        self.key = key
        if path.islocal(key):
            self.should_upload_on_close = False
            self.mode = FileMode(mode, allowed_modes='arwxb+t')
            import __builtin__
            local_path = path.parse(key).path
            if self.mode.is_output and not os.path.exists(os.path.dirname(local_path)):
                from baiji.util.shutillib import mkdir_p
                mkdir_p(os.path.dirname(local_path))
            try:
                # Use os.open to catch exclusive access to the file, but use open to get a nice, useful file object
                self.fd = os.open(local_path, self.mode.flags)
                self.f = __builtin__.open(local_path, self.mode.mode.replace('x', 'w'))
                os.close(self.fd)
            except OSError as e:
                import errno
                if e.errno is errno.EEXIST:
                    raise KeyExists("Local file exists: %s" % local_path)
                elif e.errno is errno.ENOENT:
                    raise KeyNotFound("Local file does not exist: %s" % local_path)
                else:
                    raise IOError(e.errno, "%s: %s" % (e.strerror, e.filename))
        else:
            if connection is None:
                connection = S3Connection()
            self.connection = connection

            self.mode = FileMode(mode, allowed_modes='rwxbt')
            self.should_upload_on_close = self.mode.is_output
            if self.mode.creating_exclusively:
                if self.connection.exists(self.key):
                    raise KeyExists("Key exists in bucket: %s" % self.key)
                else:
                    self.connection.touch(self.key, encrypt=self.encrypt)
            # Use w+ so we can read back the contents in upload()
            new_mode = (
                'w+' +
                (self.mode.binary and 'b' or '') +
                (self.mode.text and 't' or '')
            )
            from baiji.util import tempfile
            self.f = tempfile.NamedTemporaryFile(
                mode=new_mode,
                suffix=os.path.splitext(path.parse(self.key).path)[1]
            )
            self.name = self.f.name
            self.remotename = key # Used by some serialization code to find files which sit along side the file in question, like textures which sit next to a mesh file
            if self.mode.reading:
                self.connection.cp(self.key, self.name, force=True)
    def upload(self):
        self.connection.cp(self.name, self.key, encrypt=self.encrypt, force=True)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        # If an unhandled exception is bubbling up, don't write to s3!
        if exc_value:
            self.should_upload_on_close = False
        self.close()
    def __getattr__(self, attr):
        return getattr(self.f, attr)
    def __iter__(self):
        return iter(self.f)
    def flush(self):
        self.f.flush()
        if self.should_upload_on_close:
            self.upload()
    def close(self):
        self.flush()
        self.f.close()


class path(object):
    def __init__(self):
        raise NotImplementedError("+++ Out of cheese error, redo from start +++")
    @classmethod
    def parse(cls, s):
        '''
        Parse a path given as a url. Accepts strings of the form:

           s3://bucket-name/path/to/key
           file:///path/to/file
           /absolution/path/to/file
           relative/path/to/file
           ~/path/from/home/dir/to/file

           To avoid surprises, s3:// and file:// URLs should not
           include ;, ? or #. You should URL-encode such paths.

        Return value is a ParseResult; one of the following:

           ('s3', bucketname, valid_s3_key, ...)
           ('file', '', absolute_path_for_current_filesystem, ...)

        '''
        from urlparse import urlparse, ParseResult

        if not isinstance(s, basestring):
            raise ValueError("An S3 path must be a string, got %s" % s.__class__.__name__)

        is_windows_path = (len(s) >= 2 and s[1] == ':')
        if is_windows_path:
            scheme, netloc, s3path = 'file', '', s
        else:
            scheme, netloc, s3path, params, query, fragment = urlparse(s)
            if any([params, query, fragment]):
                raise ValueError("Invalid URI: %s" % s)
            if any(char in ';?#' for char in s):
                raise ValueError("Invalid URI: %s" % s)
            try:
                s3path.encode('UTF-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                raise ValueError("Invalid URI (bad unicode): %s" % s)
                # If somehow something ever gets uploaded with binary in the
                # key, this seems to be the only way to fix it:
                # `s3cmd fixbucket s3://bodylabs-korper-assets`
        if re.match(r'/\w:', s3path): # urlparse, given file:///C:\foo parses us to /C:\foo, so on reconstruction (on windows) we get C:\C:\foo.
            s3path = s3path[1:]
            is_windows_path = True
        if scheme == '':
            scheme = 'file'
        if scheme == 'file' and not is_windows_path:
            if s3path.endswith(os.sep) or s3path.endswith('/'):
                # os.path.abspath strips the trailing '/' so we need to put it back
                s3path = os.path.join(os.path.abspath(os.path.expanduser(s3path)), '')
            else:
                s3path = os.path.abspath(os.path.expanduser(s3path))
        if scheme == 's3' and netloc == '':
            raise ValueError('s3 urls must specify the bucket')
        return ParseResult(scheme, netloc, s3path, params=None, query=None, fragment=None) # pylint: disable=too-many-function-args,unexpected-keyword-arg
    @classmethod
    def islocal(cls, s):
        '''
        Check if a path is local. Just parses and checks format, _does not_ check for existence of the file.
        '''
        return path.parse(s).scheme == 'file'
    @classmethod
    def isremote(cls, s):
        '''
        Check if a path is on S3. Just parses and checks format, _does not_ check for existence of the file.
        '''
        return path.parse(s).scheme == 's3'
    @classmethod
    def gettmpdir(cls, prefix='tmp/', suffix='', bucket='bodylabs-temp', uuid_generator=None):
        '''
        Make a directory on S3 with a known unique name. The prefix for the directory will be
        ``s3://<bucket>/<prefix><UUID><suffix>/``

        Note that there _is_ a race condition in this code; if two clients happen to be trying to create a tmpdir and
        somehow come up with the same uuid exactly simultaniously, they could both get the same dir. But in practice this
        is sufficiently one in a billion that we'll not worry about it for now.
        '''
        from boto.s3.key import Key
        if uuid_generator is None:
            from uuid import uuid4 as uuid_generator # pragma: no cover

        #s3.ls and s3.path.parse generated one with leading slash so remove it in case
        prefix = prefix.lstrip('/')
        b = S3Connection()._bucket(bucket) # pylint: disable=protected-access
        done = False
        while not done:
            tmppath = "%s%s%s" % (prefix, uuid_generator(), suffix)
            if len([x for x in b.list(prefix=tmppath)]) == 0:
                k = Key(b)
                k.key = "%s/.tempdir" % (tmppath)
                k.set_contents_from_string('')
                done = True
        return "s3://%s/%s/" % (bucket, tmppath)

    @classmethod
    def join(cls, base, *additions):
        '''
        Extends os.path.join so work with s3:// and file:// urls

        This inherits a quirk of os.path.join: if 'addition' is
        an absolute path, path components of base are thrown away.

        'addition' must be an absolute or relative path, not
        a URL.

        `base` and `addition` can use any path separator, but the
        result will always be normalized to os.sep.

        '''
        from urlparse import urlparse, urljoin, ParseResult

        addition = sep.join(additions)

        (scheme, netloc, _, params, query, fragment) = urlparse(addition)
        if any([scheme, netloc, params, query, fragment]):
            raise ValueError('Addition must be an absolute or relative path, not a URL')

        if cls.islocal(base):
            return os.path.join(cls.parse(base).path, addition.replace(sep, os.sep))
        k = cls.parse(base)

        # Call urljoin instead of os.path.join, since it uses '/' instead of
        # os.sep, which is '\' on Windows.
        #
        # Given disparity between os.path.join and urljoin, we prefer the
        # behavior of os.path.join:
        #
        #   >>> os.path.join('foo/bar', 'baz')
        #   'foo/bar/baz'
        #   >>> urlparse.urljoin('foo/bar', 'baz')
        #   'foo/baz'
        #
        # So we add a trailing slash if there is none
        if k.path.endswith(sep):
            s3path = urljoin(k.path, addition)
        else:
            s3path = urljoin(k.path + sep, addition)

        return ParseResult(k.scheme, k.netloc, s3path, k.params, k.query, k.fragment).geturl() # pylint: disable=too-many-function-args,unexpected-keyword-arg

    @classmethod
    def basename(cls, key):
        '''
        Finds the basename of a file on s3 or local. For local, it's equivalent to os.path.basename
        '''
        k = cls.parse(key)
        return os.path.basename(k.path)

    @classmethod
    def dirname(cls, key):
        '''
        Finds the dirname of a file on s3 or local. For local, it's equivalent to os.path.dirname
        '''
        # Oddly enough, os.path.dirname works correctly on URIs...
        return os.path.dirname(key)

    @classmethod
    def isdirlike(cls, key):
        """
        Returns True for any key that is either a local, existing directory or
        ends with `sep` or `os.sep`. Otherwise returns False.
        This preserves the old `isdir` behavior.
        """
        k = cls.parse(key)
        if cls.islocal(key) and os.path.isdir(k.path):
            return True
        else:
            return k.path.endswith(sep) or k.path.endswith(os.sep)

    @classmethod
    def isdir(cls, key):
        '''
        Return true if key is directory-ish. That is, it ends with a path
        separator, or is a local directory that actually exists.
        On S3 a "directory" is considered to exist if one or more files exist
        that have the "directory" (ending with sep) as a prefix.
        '''
        k = cls.parse(key)
        if cls.islocal(key): #This really only ensures that scheme == 'file'
            return os.path.isdir(k.path)
        if cls.isremote(key): # scheme == 'S3'
            if not k.path.endswith(sep):
                k = cls.parse(key + sep)
            try:
                next(ls(k.geturl()))
                return True
            except StopIteration:
                return False
        else:
            raise InvalidSchemeException("URI Scheme {} is not implemented".format(k.scheme))

    @classmethod
    def isfile(cls, key):
        '''
        Return true if key is file; local or s3.
        '''
        k = cls.parse(key)
        if cls.islocal(key): #This really only ensures that scheme == 'file'
            return os.path.isfile(k.path)
        if cls.isremote(key): # scheme == 'S3'
            # exists currently only works for files on s3 because
            # directories don't exist on s3, only files.
            return exists(key)
        else:
            raise InvalidSchemeException("URI Scheme {} is not implemented".format(k.scheme))

    @classmethod
    def bucket(cls, key):
        '''
        Extracts the bucket from a key.
        '''
        k = cls.parse(key)
        return k.netloc
