import functools


class Signal(object):

    def __init__(self):
        self.receivers = []

    def connect(self, receiver):
        self.receivers.append(receiver)

    def disconnect(self, receiver):
        self.receivers.remove(receiver)

    def send(self, *args, **kwargs):
        for receiver in self.receivers:
            receiver(*args, **kwargs)


pre_message = Signal()
post_message = Signal()


def message_handler(handler):
    '''Decorator for message handler which makes sure that a pre_message
    and post_message signal is sent before and after the message. This
    provides a hook for the application to open/close database connections
    and perform other clean up tasks required on a per request basis.'''
    @functools.wraps(handler)
    def wrapper():
        pre_message.send()
        try:
            handler()
        finally:
            post_message.send()
    return wrapper
