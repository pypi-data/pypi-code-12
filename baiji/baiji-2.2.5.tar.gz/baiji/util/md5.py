def md5_for_file(filename, block_size=8192, start=0, end=None):
    '''
    Simple little md5 hash algorithm.
    '''
    import hashlib
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        f.seek(start)
        if end:
            while f.tell() + block_size <= end:
                md5.update(f.read(block_size))
            if f.tell() < end:
                md5.update(f.read(end-f.tell()))
        else:
            for chunk in iter(lambda: f.read(block_size), b''):
                md5.update(chunk)
    return md5.hexdigest()
