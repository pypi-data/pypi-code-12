import csv
import random
import re
import sys
import time
from datetime import datetime
from sys import stdout

import requests
from bs4 import BeautifulSoup

from cutils import Gmail
from cutils import ProgressBar


def parse_tweet_card(uid, tid):
    # out = {'n_uid': '', 'n_tid': '', 'has_result': True}
    url = 'https://twitter.com/' + uid + '/status/' + tid
    html = None

    for count in xrange(5):
        try:
            html = requests.request('GET', url).text.encode('ascii', 'ignore')
            break
        except requests.ConnectionError:
            time.sleep(60)
            stdout.write(' Connection error, sleeping 1 min.', str(count + 1) + '\r')
            sys.stdout.flush()
            continue
    if html is None:
        return None, None

    # stdout.write(' ' + tid + '\r')
    # stdout.flush()
    soup = BeautifulSoup(html, 'html.parser')
    ancestors = soup.find('div', {'id': 'ancestors'})
    if ancestors is None:
        original = soup.find('div', class_='permalink-inner permalink-tweet-container')
        original = parse_tweet_cardwrap(original)
        out = []
        try:
            out.extend(parse_threads_sequentialTweets(soup))
            out.extend(parse_threads_loneTweet(soup))
        except AttributeError:
            out = []
    else:
        original = parse_tweet_cardwrap(ancestors)
        original, out = parse_tweet_card(original[2], original[1])

    return original, out



def parse_threads_sequentialTweets(soup):
    out = []
    for thread_soup in soup.find_all('li', class_='ThreadedConversation'):
        threads = dict()

        for tweet_soup in thread_soup.find_all('div', class_=re.compile('^ThreadedConversation-tweet')):
            parsed_tweet = parse_tweet_cardwrap(tweet_soup)
            threads[parsed_tweet[0] + '_' + parsed_tweet[1]] = parsed_tweet

        view_others = thread_soup.find_all('li', class_='ThreadedConversation-viewOther')
        if len(view_others) > 0:
            for view_other in view_others:
                view_other_url = 'https://twitter.com' + view_other.a.attrs['href']
                view_other_html = requests.request('GET', view_other_url).text.encode('ascii', 'ignore')
                view_other_soup = BeautifulSoup(view_other_html, 'html.parser')
                for view_other_tweet in parse_threads_loneTweet(view_other_soup):
                    threads[view_other_tweet[0] + '_' + view_other_tweet[1]] = view_other_tweet
        out.append([threads[key] for key in sorted(threads.keys())])
    return out


def parse_threads_loneTweet(soup):
    return [[parse_tweet_cardwrap(lone)] for lone in soup.find_all('div', class_='ThreadedConversation--loneTweet')]


def parse_tweet_cardwrap(tweet_soup):
    properties = tweet_soup.find('div', class_=re.compile('tweet')).attrs
    text_container = tweet_soup.find('div', class_='js-tweet-text-container')
    footer = tweet_soup.find('div', class_='stream-item-footer')

    timestamp = tweet_soup.find('span', class_=re.compile('js-short-timestamp')).attrs['data-time']
    timestamp = int(timestamp) + 6 * 60 * 60
    timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    text = re.sub('\n|\t', ' ', text_container.text.strip())
    text = re.sub('(http|pic)', ' \\1', text)
    text = re.sub(' +', ' ', text)

    retweet = footer.find('span', class_='ProfileTweet-action--retweet u-hiddenVisually').text.strip()
    retweet = re.sub('[^0-9]', '', retweet)
    likes = footer.find('span', class_='ProfileTweet-action--favorite u-hiddenVisually').text.strip()
    likes = re.sub('[^0-9]', '', likes)

    # datetime,tid,uscreenname,text,retweet,likes
    return [timestamp,
            properties['data-tweet-id'],
            properties['data-screen-name'],
            text.encode('ascii', 'ignore'),
            retweet, likes]


def writer(output, original, thread):
    with open(output, 'a') as o:
        csvwriter = csv.writer(o, delimiter='\t')
        if thread:
            # for items in out:
            csvwriter.writerow(original)
            for item in thread:
                csvwriter.writerow(item)
            o.write('\n')
        else:
            csvwriter.writerow(original)
            o.write('\n')


if __name__ == '__main__':
    argvs = sys.argv[1:]
    input = argvs[0]
    output = argvs[1]

    out = dict()
    with open(input, 'r') as i:
        csvreader = csv.reader(i, delimiter=',', quotechar='"')
        keys = [row[10] + '_' + row[1] for row in csvreader]

    counter = 0
    bar = ProgressBar(total=len(keys))
    print input, 'is being crawled.'
    for key in keys:
        bar.move().log()
        try:
            counter += 1
            n = len(out)
            out[key] = 1

            if counter % 100000 == 0:
                time.sleep(random.uniform(3,8))
            if len(out) > n:
                n = len(out)
                tokens = key.split('_')
                # print tokens
                original, parsed_tweet = parse_tweet_card(tokens[0], tokens[1])

                if original[2] + '_' + original[1] != key:  # make sure no duplicate
                    out[original[2] + '_' + original[1]] = 1
                    if len(out) == n:
                        continue
                if parsed_tweet:  # make sure target brand is crawled
                    for items in parsed_tweet:
                        total_text = original[3] + ' '
                        for item in items:
                            total_text += item[3]
                        if input.split('/')[-1].split('.')[0] in total_text:
                            writer(output, original, items)
                else:
                    writer(output, original, parsed_tweet)
        except Exception:
            pass

    mail= Gmail() \
        .set_from_to(receiver='wonderfulhoo@gmail.com') \
        .set_subject('AWS Status Brand') \
        .set_credentials('/Users/cchen224/Downloads/') \
        .send_message(input + ' Done!\n') \
        .close()
    bar.close()
