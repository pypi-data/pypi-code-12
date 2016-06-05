import time


class Timer:

    def __init__(self, timer_name):
        self.name = timer_name
        self.start = None
        self.stop = None
        self.total = None

    def start(self):
        self.start = time.time()

    def stop(self):
        self.stop = time.time()

    def _calc_time(self):
        self.total = self.stop - self.start

    def report(self, log=None):
        report_text = 'Timer {0} took {1} seconds to run.'.format(self.name, self.total)
        if log:
            log.info(report_text)
        else:
            print(report_text)
