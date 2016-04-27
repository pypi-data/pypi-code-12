import hashlib

BUF_SIZE = 65536


def file_sha1sum(filename):
    """Calculate the SHA-1 checksum of a file"""

    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
                sha1.update(data)
    return sha1.hexdigest()
