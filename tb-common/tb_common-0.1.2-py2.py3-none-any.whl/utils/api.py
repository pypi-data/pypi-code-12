__author__ = 'hiepsimu'


def failed(message=None, **kwargs):
    kwargs['ok'] = False
    if message:
        kwargs['message'] = message
    return kwargs


def success(message=None, **kwargs):
    kwargs['ok'] = True
    if message:
        kwargs['message'] = message
    return kwargs
