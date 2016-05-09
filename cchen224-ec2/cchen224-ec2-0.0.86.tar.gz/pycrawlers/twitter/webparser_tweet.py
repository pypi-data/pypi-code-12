from bs4 import BeautifulSoup

from webparser_error import *
from webparser_utility import *


def parse_tweet(tiduid):
    """
    :param tiduid: tid@uid
    :return: uid, screen_name, tid, timestamp, text, hashtags, cashtags, mentions, emojis, retweets, likes
    """
    tokens = tiduid.split('@')
    tid = tokens[0]
    uid = tokens[1]
    url = 'https://twitter.com/' + uid + '/status/' + tid
    html = get_html(url)

    if html is None:
        return False

    soup = BeautifulSoup(html, 'html.parser')
    for fnc in [is_account_not_suspended(soup), is_content_not_protected(soup), is_page_exists(soup)]:
        if not fnc:
            return []

    # PermalinkOverlay
    cardwrap = soup.find('div', class_='permalink-inner permalink-tweet-container')

    properties = cardwrap.find('div', class_=re.compile('^permalink-tweet')).attrs
    tid = properties['data-item-id']
    uid = properties['data-user-id']
    screen_name = properties['data-screen-name']

    out = [uid, screen_name, tid]
    out.extend(parse_header(cardwrap.find('div', class_='permalink-header')))
    out.extend(parse_text(cardwrap.find('div', class_="js-tweet-text-container")))
    out.extend(parse_fixer(cardwrap.find('div', class_='js-tweet-details-fixer tweet-details-fixer')))

    return out
