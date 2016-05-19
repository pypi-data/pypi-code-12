import random
import re
import sys
import time
import traceback
from os import listdir

from cutils import Gmail
from cutils import ProgressBar

from webparser_tweet import parse_tweet


# pip install --upgrade google-api-python-client
# pip install beautifulsoup4

def crawl(fp, outputFile):
    gmail = Gmail(minDuration=0).set_from_to().set_subject('AWS TweetContent Status')

    total = 0
    f_scan = open(fp, 'r')
    for _ in f_scan:
        total += 1
    f_scan.close()
    bar = ProgressBar(total=total)

    print fp, '...'
    f = open(fp, 'r')
    o = open(outputFile, 'a')
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
                gmail = gmail.send_message(fp + '\n' + uid + ' ' + tid + ' Connection Error.')
                break
        except:
            gmail = gmail.send_message(fp + '\n' + uid + ' ' + tid + '\n' + traceback.format_exc())

        bar.move()
        bar.log()
    f.close()
    o.close()
    bar.close()


if __name__ == '__main__':
    argvs = sys.argv[1:]
    target_folder = 'docs/'
    docs = listdir(target_folder)
    gmail = Gmail().set_from_to().set_subject('AWS TweetContent Status')
    for doc in docs:
        if doc.endswith('.sample') and doc.startswith(argvs[0]):
            crawl(target_folder + doc,
                  target_folder + re.sub('sample', 'csv', doc))
            gmail = gmail.send_message(doc + ' Done!')
    gmail = gmail.send_message('\nYear' + argvs[0] + ' Done!')
    gmail = gmail.close()
