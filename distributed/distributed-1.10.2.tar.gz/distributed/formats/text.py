
def read_text(fn, keyname=None, encoding='utf-8', errors='strict', lineterminator='\n',
               executor=None, fs=None, lazy=True, collection=True,
               blocksize=2**27, compression=None):
    """ Read text lines from S3

    Parameters
    ----------
    path: string
        Path of files on S3, including both bucket, key, or globstring
    keyname: string, optional
        If path is only the bucket name, provide key name as second argument
    collection: boolean, optional
        Whether or not to return a high level collection
    lazy: boolean, optional
        Whether or not to start reading immediately
    blocksize: int, optional
        Number of bytes per partition.  Use ``None`` for no blocking.
        Silently ignored if data is compressed with a non-splittable format like gzip.
    lineterminator: str, optional
        The endline string used to deliniate line breaks
    compression: str, optional
        Compression to use options include: gzip
        The use of compression will suppress blocking

    Examples
    --------

    Provide bucket and keyname joined by slash.
    >>> b = read_text('bucket/key-directory/')  # doctest: +SKIP

    Alternatively use support globstrings
    >>> b = read_text('bucket/key-directory/2015-*.json').map(json.loads)  # doctest: +SKIP

    Or separate bucket and keyname
    >>> b = read_text('bucket', 'key-directory/2015-*.json').map(json.loads)  # doctest: +SKIP

    Optionally provide blocksizes and delimiter to chunk up large files
    >>> b = read_text('bucket', 'key-directory/2015-*.json',
    ...               linedelimiter='\\n', blocksize=2**25)  # doctest: +SKIP

    Specify compression, blocksizes not allowed
    >>> b = read_text('bucket/my-data.*.json.gz',
    ...               compression='gzip', blocksize=None)  # doctest: +SKIP

    Returns
    -------
    Dask bag if collection=True or Futures or dask values otherwise
    """
    if keyname is not None:
        if not keyname.startswith('/'):
            keyname = '/' + keyname
        fn = fn + keyname
    fs = fs or S3FileSystem()
    executor = default_executor(executor)

    if compression:
        blocksize=None
        decompress = decompressors[compression]

    filenames = sorted(fs.glob(fn))
    blocks = [block for fn in filenames
                    for block in read_bytes(fn, executor, fs, lazy=True,
                                            delimiter=lineterminator.encode(),
                                            blocksize=blocksize)]
    if compression:
        blocks = [do(decompress)(b) for b in blocks]
    strings = [do(bytes.decode)(b, encoding, errors) for b in blocks]
    lines = [do(unicode.split)(s, lineterminator) for s in strings]

    ensure_default_get(executor)
    from dask.bag import from_imperative
    if collection:
        result = from_imperative(lines).filter(None)
    else:
        result = lines

    if not lazy:
        if collection:
            result = executor.persist(result)
        else:
            result = executor.compute(result)

    return result
