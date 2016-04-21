import time


class CustomTimer(object):
    def __init__(self, transaction, name):
        if not hasattr(transaction, 'custom_timers'):
            transaction.custom_timers = {}
        self.transaction = transaction
        self.name = name
        self.start = None

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):
        self.transaction.custom_timers[self.name] = time.time() - self.start
