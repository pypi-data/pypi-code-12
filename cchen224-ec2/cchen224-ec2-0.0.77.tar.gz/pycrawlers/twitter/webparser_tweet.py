from bs4 import BeautifulSoup

from webparser_error import *
from webparser_utility import *


def parse_tweet(tiduid):
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

    text, hashtags, cashtags, mentions, emojis = parse_text(cardwrap.find('div', class_="js-tweet-text-container"))
    retweets, likes = parse_fixer(cardwrap.find('div', class_='js-tweet-details-fixer tweet-details-fixer'))
    timestamp = parse_header(cardwrap.find('div', class_='permalink-header'))


    #
    # if tweet_inner_soup is None:
    #     try:
    #         tweet_inner_soup = soup.find('div', class_='permalink-inner permalink-tweet-container')
    #         n_uid = tweet_inner_soup.div.attrs['data-user-id']
    #         n_tid = tweet_inner_soup.div.attrs['data-tweet-id']
    #     except AttributeError:
    #         print '404, sleeping'
    #         from cutils import Gmail
    #         Gmail(0).set_from_to().set_subject('AWS_TweetContent').send_message(' '.join([uid, tid]) + soup.__str__())
    #         time.sleep(random.uniform(7, 13))
    #         return parse_tweet(uid, tid)
    # text, hashtags, cashtags, mentions, emojis = parse_text(tweet_inner_soup.find('div', class_="js-tweet-text-container"))
    # time, retweets, likes = parse_fixer(tweet_inner_soup.find('div', class_='js-tweet-details-fixer tweet-details-fixer'))

    return [uid,
            screen_name,
            tid,
            timestamp,
            text,
            hashtags,
            cashtags,
            mentions,
            emojis,
            retweets,
            likes]
