from random import random
from datetime import datetime

from bs4 import BeautifulSoup
from time import sleep

from cutils import Gmail
from webparser_error import *
from webparser_utility import *


def parse_tweet(tiduid):
    """
    :param tiduid: tid@uid
    :return: uid, screen_name, tid, timestamp, text, hashtags, cashtags, mentions, emojis, retweets, likes
    """
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=10)
    session.mount('https://', adapter)

    tokens = tiduid.split('@')
    tid = tokens[0]
    uid = tokens[1]
    url = 'https://twitter.com/' + uid + '/status/' + tid
    res = session.get(url)
    html = res._content

    if html is None:
        return [[]]

    soup = BeautifulSoup(html, 'html.parser')
    error_functions = [is_not_account_suspended(soup),
                       is_not_content_protected(soup),
                       is_page_exists(soup),
                       is_not_tweet_withheld(soup)]
    for fnc in error_functions:
        if not fnc:
            return []

    if soup is None:
        # with open('/Users/cchen224/Downloads/web_error.html', 'w') as o:
        #     o.write(res.__str__() + '\n\n\n' + html)
        sleep(random()*10)
        # print 1
        # Gmail().set_from_to().set_credentials().set_subject('AWS Twitter.tweet PropertiesNotFound').send_message(tiduid + '\n\n' + soup.__str__()).close()
        return [[]]
    # PermalinkOverlay
    cardwrap = soup.find('div', class_='permalink-inner permalink-tweet-container')

    uid, screen_name, tid, rid = parse_properties(cardwrap)
    # try:
    #
    #     properties = cardwrap.find('div', class_=re.compile('^permalink-tweet')).attrs
    #     tid = properties['data-item-id']
    #     uid = properties['data-user-id']
    #     screen_name = properties['data-screen-name']
    # except TypeError:
    #     t = random() * 60
    #     print tiduid, 'sleeping', t, 'secs.', datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    #     Gmail().set_from_to().set_credentials().set_subject('AWS Twitter.tweet PropertiesNotFound').send_message(tiduid + '\n\n' + html.__str__()).close()
    #     sleep(t)
    #     return parse_tweet(tiduid)

    if uid:
        out = [uid, screen_name, tid]
        out.extend(parse_header(cardwrap.find('div', class_='permalink-header')))
        out.extend(parse_text(cardwrap.find('div', class_="js-tweet-text-container")))
        out.extend(parse_fixer(cardwrap.find('div', class_='js-tweet-details-fixer tweet-details-fixer')))
        return [out]
    else:
        return [[]]