from cutils import Gmail, ProgressBar
from webparser_tweet import parse_tweet
import random
import re
import sys
import time
import traceback

class TwitterCrawler:

    def __init__(self):
        self._gmail = Gmail().set_from_to().set_subject('AWS TweetContent Status')


    def crawl(self, input, output):
        total = 0
        f_scan = open(input, 'r')
        for _ in f_scan:
            total += 1
        f_scan.close()
        self._bar = ProgressBar(total=total)

        f = open(input, 'r')
        o = open(output, 'a')
        i = 0
        for line in f:
            tokens = line.split(',')
            tid = tokens[0]
            uid = tokens[1]
            screen_name = re.sub('\'', '"', tokens[3])
            time_date = re.sub('\'', '"', tokens[2])
            try:
                i += 1
                if i % 10000 == 0:
                    print i, 'sleeping for a sec.'
                    time.sleep(random.uniform(4, 9))

                info = parse_tweet(uid, tid)
                if info['has_result'] is True:
                    o.write(','.join([uid, screen_name.strip(), tid, time_date, info['text'],
                                      info['hashtags'], info['cashtags'], info['mentions'], info['emojis'],
                                      info['retweets'], info['likes'],
                                      info['n_uid'], info['n_tid']]))
                    o.write('\n')
                elif info['has_result'] == 'ConnectionError':
                    self._gmail = self._gmail.send_message(output + '\n' + uid + ' ' + tid + ' Connection Error.')
                    break
            except:
                self._gmail = self._gmail.send_message(input + '\n' + uid + ' ' + tid + '\n' + traceback.format_exc())

            self._bar.move()
            self._bar.log()
        f.close()
        o.close()
        self._bar.close()