VERSION = (1, 3, 'b2')


def get_version(tail=''):
    return ".".join(map(str, VERSION)) + tail
