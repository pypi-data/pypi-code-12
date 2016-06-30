import hashlib
import zlib


###
# Returns MD5 checksum of argument data encoded in UTF-8
#
def md5Checksum(data):
    """
    >>> file = open('tmp.txt', 'w')
    >>> file.close()
    >>> data = open('tmp.txt', 'r').read()
    >>> md5Checksum(data.encode())
    'd41d8cd98f00b204e9800998ecf8427e'
    """
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


###
# Returns SHA-256 checksum of argument data encoded in UTF-8
#
def sha256Checksum(data):
    """
    >>> file = open('tmp.txt', 'w')
    >>> file.close()
    >>> data = open('tmp.txt', 'r').read()
    >>> sha256Checksum(data.encode())
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    """
    sha = hashlib.sha256()
    sha.update(data)
    return sha.hexdigest()


def sha512Checksum(data):
    """
    >>> file = open('tmp.txt', 'w')
    >>> file.close()
    >>> data = open('tmp.txt', 'r').read()
    >>> sha512Checksum(data.encode())
    'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e'
    """
    sha = hashlib.sha512()
    sha.update(data)
    return sha.hexdigest()


###
# Returns CRC32 checksum of data
#
def crc32Checksum(data):
    """
    >>> file = open('tmp.txt', 'w')
    >>> file.close()
    >>> data = open('tmp.txt', 'r').read()
    >>> crc32Checksum(data.encode())
    '0'
    """
    return str(zlib.crc32(data) & 0xFFFFFFFF)
