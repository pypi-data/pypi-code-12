import json

from bs4 import BeautifulSoup
from cutils import Gmail
import traceback
from time import sleep
from random import random
from sys import stdout
import requests

from webparser_utility import *

HEADERS = {'authority': 'twitter.com',
           'method': 'GET',
           # 'path': '/i/trends?k=&lang=en&pc=true&query=from%3ATomaasNavarrete+since%3A2016-02-05+until%3A2016-02-10&show_context=true&src=module',
           'scheme': 'https',
           'accept': 'application/json, text/javascript, */*; q=0.01',
           'accept-encoding': 'gzip, deflate, sdch',
           'accept-language': 'en-US,en;q=0.8',
           # 'cookie': 'guest_id=v1%3A143633553636973156; kdt=Nfw6w4LLnEdRrKgUxa9S6RkhBi5EjifOYjYEjUT7; remember_checked_on=1; auth_token=9b88cbfd12b890a7ef12bcae0e2880a633e411fa; pid="v3:1437887547279707935822773"; lang=en; _gat=1; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0; _ga=GA1.2.1819401238.1437630704; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCDW3U%252BlUAToMY3NyZl9p%250AZCIlYjY5MGMyOTM2MzExODJhY2NlNTA1NjdlOWNiZWY3ODc6B2lkIiUxY2Q5%250AM2UzZTc1M2Q4M2QzODE4MzJmNGYyYTgyZjIzMA%253D%253D--23984f61b0a5266b27251a0a36095331c54d8ba2',
           # 'referer': 'https://twitter.com/search?q=from%3ATomaasNavarrete%20since%3A2016-02-05%20until%3A2016-02-10&src=typd&lang=en',
           'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest'}


def parse_user_timeline(screen_name, **kwargs):
    adv_search = kwargs.get('adv_search', dict())
    date_since = adv_search.get('date_since', '')
    date_until = adv_search.get('date_until', '')

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=10)
    session.mount('https://', adapter)

    out = []
    tid_start = ''

    cur_page = 0
    has_next = True
    while has_next:
        cur_page += 1
        if adv_search:
            if cur_page == 1:
                url = 'https://twitter.com/search?q=from%3A' + screen_name + \
                      '%20since%3A' + date_since + \
                      '%20until%3A' + date_until + '&src=typd&lang=en'
                html = session.get(url, headers=HEADERS)._content
            else:
                stdout.write(str(cur_page) + '\r')
                stdout.flush()
                url = 'https://twitter.com/i/search/timeline?vertical=default&q=from%3A' + screen_name + \
                      '%20since%3A' + date_since + \
                      '%20until%3A' + date_until + \
                      '&src=typd&include_available_features=1&include_entities=1&' + \
                      'max_position=TWEET-' + tid + '-' + tid_start + '-' + \
                      'BD1UO2FFu9QAAAAAAAAETAAAAAcAAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                      '&reset_error_state=false'
                for counter in range(5):
                    html_json = json.loads(session.get(url, headers=HEADERS)._content)
                    if html_json.get('errors', ''):
                        sleep(random() * 10)
                    else:
                        break
                html = html_json['items_html'].strip()
                has_next = html_json['has_more_items']
                    # Gmail().set_subject('AWS Twitter.timeline Error').set_from_to()\
                    #     .send_message(screen_name + '\n' + str(html_json) + '\n' + has_next.__str__() + '\n\n\n' + traceback.format_exc()).close()
        else:
            if cur_page == 1:
                url = 'https://twitter.com/' + re.sub('\@', '', screen_name)
                html = session.get(url)._content
            else:
                stdout.write(str(cur_page) + '\r')
                stdout.flush()
                url = 'https://twitter.com/i/profiles/show/' \
                      + re.sub('\@', '', screen_name) \
                      + '/timeline/tweets?include_available_features=1&include_entities=1&max_position=' \
                      + tid \
                      + '&reset_error_state=false'
                html_json = json.loads(session.get(url, headers=HEADERS)._content)
                html = html_json['items_html'].strip()
                has_next = html_json['has_more_items']
        soup = BeautifulSoup(html, 'html.parser')

        tweet_cardwraps = soup.find_all('li', class_='js-stream-item stream-item stream-item expanding-stream-item ')
        if len(tweet_cardwraps) == 0:
            break

        # tweet_cardwrap = tweet_cardwraps[0]
        for tweet_cardwrap in tweet_cardwraps:
            uid, screen_name, tid, rid = parse_properties(tweet_cardwrap)
            # if not uid:
            #     return out
            if not tid_start:
                tid_start = rid if rid else tid

            [timestamp] = parse_header(tweet_cardwrap)
            text, hashtags, cashtags, mentions, emojis = \
                parse_text(tweet_cardwrap.find('div', class_='js-tweet-text-container'))
            retweets, likes = parse_footer(tweet_cardwrap.find('div', class_='stream-item-footer'))

            out.append([uid, screen_name, tid, timestamp, text, hashtags, cashtags, mentions, emojis, retweets, likes])

        if len(tweet_cardwraps) < 20:
            break

    return out


# with open('/Users/cchen224/Downloads/testadvsearch.csv', 'w') as i:
#     csvwriter = csv.writer(i)
#     for out in parse_user_timeline('Go_diego_go801', adv_search={'date_since':'2016-02-05', 'date_until': '2016-02-09'}):
#         csvwriter.writerow(out)
    #
    # with open('/Users/cchen224/Downloads/testadvsearch', 'w') as i:
    #     # i.write(html.encode('utf-8'))
    #     i.write(json.loads(session.get(url, headers=HEADERS)._content)['module_html'])
