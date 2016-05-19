'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
import hashlib

__all__ = ['generate_blocks']


def generate_blocks(block_size, cluster_uuid, content):
    '''
    Generate blocks based on block_size, cluster_uuid and content.

    It's a generator of (hash, chunk) pairs ready to be uploaded.
    '''

    cursor = 0
    chunk = content[cursor:cursor+block_size]
    while chunk:
        size_diff = block_size - len(chunk)
        if size_diff > 0:
            chunk += '\0'*size_diff
        chunk_name = hashlib.sha1(cluster_uuid + chunk).hexdigest()
        yield chunk_name, chunk
        cursor += block_size
        chunk = content[cursor:cursor+block_size]
