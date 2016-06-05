import time


def epoc_timestamp():
    return '-{0}'.format(time.time())


def str_timestamp():
    return '-{0}'.format(time.strftime('%m-%d-%y_%H.%M.%S'))

