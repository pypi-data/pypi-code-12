import json

from bs4 import BeautifulSoup
from sys import stdout

from webparser_utility import *


def parse_user_timeline(screen_name, **kwargs):
    cur_page = 0
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=10)
    session.mount('https://', adapter)

    out = []
    while True:
        cur_page += 1
        stdout.write(' Searching user ' + screen_name + ' page' + str(cur_page) + '\r')
        stdout.flush()
        if cur_page == 1:
            url = 'https://twitter.com/' + re.sub('\@', '', screen_name)
            html = session.get(url)._content
        else:
            url = 'https://twitter.com/i/profiles/show/' \
                  + re.sub('\@', '', screen_name) \
                  + '/timeline/tweets?include_available_features=1&include_entities=1&max_position=' \
                  + tid \
                  + '&reset_error_state=false'
            html = json.loads(session.get(url)._content)['items_html'].strip()
        soup = BeautifulSoup(html, 'html.parser')

        tweet_cardwraps = soup.find_all('li', class_='js-stream-item stream-item stream-item expanding-stream-item ')
        if len(tweet_cardwraps) == 0:
            break
        for tweet_cardwrap in tweet_cardwraps:
            uid, screen_name_1, tid = parse_properties(tweet_cardwrap)
            timestamp = parse_header(tweet_cardwrap)
            text, hashtags, cashtags, mentions, emojis = \
                parse_text(tweet_cardwrap.find('div', class_='js-tweet-text-container'))
            retweets, likes = parse_footer(tweet_cardwrap.find('div', class_='stream-item-footer'))
            out.append([uid, screen_name, tid, timestamp, text, hashtags, cashtags, mentions, emojis, retweets, likes])
    return out