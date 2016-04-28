VERSION = (1, 3, 'b3')


def get_version(tail=''):
    return ".".join(map(str, VERSION)) + tail
