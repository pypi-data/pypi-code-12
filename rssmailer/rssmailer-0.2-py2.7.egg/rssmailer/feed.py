import calendar
import time

import logging
import sys
log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)


class Feed(object):
    def __init__(self, feed):
        self.feed = feed  # raw contents of feed
        self.title = feed['feed']['title']
        self.entries_to_mail = []

    def get_latest_posts(self):
        if not self.feed:
            log.debug('No entries here, so need to filter the latest ones')
            return None
        entries = self.feed['entries']
        for entry in entries:
            updated_timestamp = entry['updated_parsed']
            then = (calendar.timegm(updated_timestamp))
            log.debug('{} has timestamp {}'.format(entry['title'], then))
            now = time.time()
            log.debug('.. and the current time is {}'.format(now))
            diff = now - then
            if diff < 86400:  # 1 day in seconds
                log.info('{}: adding:\t{} '.format(self.title,
                                                   entry['title']))
                self.entries_to_mail.append(entry)
            else:
                log.debug('{}: skipping:\t{}'.format(self.title,
                                                     entry['title']))
                
