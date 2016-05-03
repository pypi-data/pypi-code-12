import hashlib
import zlib


###
# Returns MD5 checksum of argument data encoded in UTF-8
#
def md5_checksum(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


###
# Returns SHA-256 checksum of argument data encoded in UTF-8
#
def sha256_checksum(data):
    sha = hashlib.sha256()
    sha.update(data)
    return sha.hexdigest()


def sha512_checksum(data):
    sha = hashlib.sha512()
    sha.update(data)
    return sha.hex

###
# Returns CRC32 checksum of data
#
def crc32_checksum(data):
    return zlib.crc32(data) & 0xFFFFFFFF
