from croniter import croniter
from threading import Thread
import datetime
import logging
import time

from komodo.timezone import utc

log = logging.getLogger(__name__)


class Scheduler(Thread):
    daemon = True

    def __init__(self, datastore):
        super(Scheduler, self).__init__()
        self.check_times = {}
        self.checks = []
        self.finisher = {"finished": False}
        self.datastore = datastore
        self.errors = {}
        self.datastore.set('_internal', 'errors', self.errors)

    def run(self):
        self.twitch()
        while True:
            if self.finisher['finished']:
                break

            try:
                self.twitch()
                time.sleep(1)
            except Exception:
                log.exception("Scheduler failed an iteration!")

    def register(self, checker, name):
        for cron, func in checker.register_checks():
            self.checks.append((cron, func, checker, name))

    def twitch(self):
        now = datetime.datetime.now(utc)
        for cron, func, _, name in self.checks:
            cron_key = "{0}.{1}".format(name, func.__name__)
            iterable = croniter(cron, self.check_times.get(cron_key, now))
            nxt = iterable.get_next(datetime.datetime)
            if nxt > now and cron_key in self.check_times:
                continue

            log.info("Triggering check: %s.%s '%s'", name, func.__name__, cron)
            try:
                for key, value in func(now - self.check_times.get(cron_key, now)):
                    self.datastore.set(name, key, value)
                    self.datastore.set(name, '_{0}_time'.format(key), now.isoformat())

                # Clear any errors from previous runs
                if cron_key in self.errors:
                    del self.errors[cron_key]
                    self.datastore.set('_internal', 'errors', self.errors)

            except Exception as e:
                log.exception("Error running a check %s.%s", name, func.__name__)
                # Store the errors so the frontend can show them
                self.errors[cron_key] = '{0}: {1}'.format(e.__class__.__name__, str(e))
                self.datastore.set('_internal', 'errors', self.errors)

            finally:
                self.check_times[cron_key] = now
