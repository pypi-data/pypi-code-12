from setproctitle import getproctitle
from setproctitle import setproctitle

import logging


class ArgvHandler(logging.Handler):
    requests = {}
    original = ''

    def __init__(self):
        self.original = getproctitle()
        super(ArgvHandler, self).__init__()

    def emit(self, record):
        record_data = record.msg.split(' ')
        if record_data[0] == 'B':
            self.requests[record_data[1]] = record_data[-1]
        elif record.msg.startswith('A'):
            self.requests.pop(record_data[1])
        else:
            pass
        setproctitle(self.original + ' ' + ' '.join(self.requests.values()))


logging.getLogger('trace').addHandler(ArgvHandler())
