"""
Network helper functions.
"""

import base64
import contextlib
import http.client
import os
import os.path
import pathlib
import urllib.request
import zlib

from .log import LOG

def _decompress_stream(input_stream, output_stream):
    """
    Decompress the contents of input_stream to output_stream (assumes GZip format).
    """
    if not isinstance(input_stream, http.client.HTTPResponse):
        assert "b" in input_stream.mode
    assert "b" in output_stream.mode

    BLOCK_SIZE = 4096
    dc = zlib.decompressobj(16+zlib.MAX_WBITS)
    while True:
        data = input_stream.read(BLOCK_SIZE)
        if not data:
            break
        output_stream.write(dc.decompress(data))

def download(url, decompress=False, expire=None):
    """
    Download a file over HTTP or FTP, cache it locally, and return a path to it.

    Arguments
    ---------
    url : str
        The URL to download and cache.
    decompress : bool
        Whether to decompress the file before saving it (assumes gzip format).
    expire : numeric or None
        Expire the cache and redownload the file after this many days, 
        or if this parameter is None, never expire.

    Returns
    -------
    A :class:`pathlib.Path` object representing the path to the downloaded file
    on the file system.
    """
    # TODO: add "expire" parameter
    cache = os.path.join(os.path.expanduser("~/.cache/wrenlab/download/"))
    os.makedirs(cache, exist_ok=True)

    target_ascii = url.lower()
    if decompress:
        target_ascii += "-dc"
    target = base64.b64encode(target_ascii.encode("utf-8")).decode("utf-8")
    path = os.path.join(cache, target)

    if not os.path.exists(path):
        LOG.info("Downloading URL: {}".format(url))
        try:
            if decompress:
                LOG.debug("Decompressing stream (decompress = True)")
                with open(path, "wb") as o:
                    with contextlib.closing(urllib.request.urlopen(url)) as h:
                        _decompress_stream(h, o)
            else:
                urllib.request.urlretrieve(url, path)
            LOG.debug("URL successfully saved to: {}".format(path))
        except:
            if os.path.exists(path):
                os.unlink(path)
            LOG.debug("Failed to download URL: {}".format(url))
            raise
    return pathlib.Path(path)
