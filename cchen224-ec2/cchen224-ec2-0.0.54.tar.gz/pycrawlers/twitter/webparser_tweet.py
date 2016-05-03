import time
import random

import requests
from bs4 import BeautifulSoup

from webparser_utility import parse_text, parse_fixer


def parse_tweet(uid, tid):
    out = {'n_uid': '', 'n_tid': '', 'has_result': True}
    url = 'https://twitter.com/' + uid + '/status/' + tid
    html = None

    for _ in xrange(5):
        try:
            html = requests.request('GET', url).text.encode('ascii', 'ignore')
        except requests.ConnectionError:
            time.sleep(60)
            print 'Connection error, sleeping'

    if html is None:
        out['has_result'] = 'ConnectionError'
        return out

    soup = BeautifulSoup(html, 'html.parser')
    for fnc in [is_account_not_suspended(soup), is_content_not_protected(soup), is_page_exists(soup)]:
        out['has_result'] = fnc
        if out['has_result'] is False:
            return out


    # PermalinkOverlay
    tweet_inner_soup = soup.find('div', attrs={"data-tweet-id": tid})
    if tweet_inner_soup is None:
        try:
            tweet_inner_soup = soup.find('div', class_='permalink-inner permalink-tweet-container')
            out['n_uid'] = tweet_inner_soup.div.attrs['data-user-id']
            out['n_tid'] = tweet_inner_soup.div.attrs['data-tweet-id']
        except AttributeError:
            print '404, sleeping'
            from cutils import Gmail
            Gmail(0).set_from_to().set_subject('AWS_TweetContent').send_message(' '.join([uid, tid]) + soup.__str__())
            time.sleep(random.uniform(7, 13))
            return parse_tweet(uid, tid)
    out.update(parse_text(tweet_inner_soup.find('div', class_="js-tweet-text-container")))
    out.update(parse_fixer(tweet_inner_soup.find('div', class_='js-tweet-details-fixer tweet-details-fixer')))

    return out


def is_page_exists(soup):
    try:
        content = soup.find('div', class_='body-content').h1.text.strip()
        if content == 'Sorry, that page doesnt exist!':
            return False
    except AttributeError:
        return True


def is_content_not_protected(soup):
    try:
        content = soup.find('div', class_='message-inside').span.text.strip()
        if content == 'Sorry, you are not authorized to see this status.':
            return False
    except AttributeError:
        return True


def is_account_not_suspended(soup):
    try:
        content = soup.find('div', class_='flex-module error-page clearfix').h1.text.strip()
        if content == 'Account suspended':
            return False
    except AttributeError:
        return True
