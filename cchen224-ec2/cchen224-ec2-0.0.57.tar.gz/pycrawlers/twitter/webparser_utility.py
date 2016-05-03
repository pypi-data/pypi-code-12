import re


def parse_text(js_tweet_text_container,
                is_remove_url=True,
                is_remove_mentions=False,
                is_remove_hashtags=False,
                is_remove_cashtags=False,
                is_remove_emojis=True
               ):

    hashtags = []
    cashtags = []
    mentions = []
    emojis = []

    try:
        a_hrefs = js_tweet_text_container.p(['a', 'img'])
        for s in a_hrefs:
            if s.has_attr('data-expanded-url'):
                if is_remove_url:
                    s.extract()
            elif s.has_attr('data-query-source'):
                if s.attrs['data-query-source'] == 'cashtag_click':
                    cashtags.append(s.text.strip())
                    if is_remove_cashtags:
                        s.extract()
                elif s.attrs['data-query-source'] == 'hashtag_click':
                    hashtags.append(s.text.strip())
                    if is_remove_hashtags:
                        s.extract()
            elif s.has_attr('data-mentioned-user-id'):
                mentions.append(s.attrs['data-mentioned-user-id'])
                if is_remove_mentions:
                    s.extract()
            elif s.has_attr('class') and 'Emoji--forText' in s.attrs['class']:
                emojis.append('_'.join(s.attrs['title'].split()))
                if is_remove_emojis:
                    s.extract()
    except TypeError:
        pass

    text = js_tweet_text_container.text
    text = re.sub(',|\n', ' ', text)
    text = '"' + re.sub(' +', ' ', text).strip() + '"'

    hashtags = '|'.join(hashtags)
    cashtags = '|'.join(cashtags)
    mentions = '|'.join(mentions)
    emojis   = '|'.join(emojis)

    return {'text': text, 'hashtags': hashtags, 'cashtags': cashtags, 'mentions': mentions, 'emojis': emojis}



def parse_footer(stream_item_footer):
    retweets = stream_item_footer.find('div', attrs={'title': 'Retweet'}).text
    retweets = re.sub('[^0-9]', '', retweets)
    if retweets == '': retweets = u'0'

    likes = stream_item_footer.find('div', attrs={'title': 'Like'}).text
    likes = re.sub('[^0-9]', '', likes)
    if likes == '': likes = u'0'


    return {'retweets': retweets, 'likes': likes}


def parse_fixer(js_tweet_details_fixer):
    time = js_tweet_details_fixer.find('div', class_='client-and-actions').text.strip()

    stats = js_tweet_details_fixer.find('div', class_='js-tweet-stats-container tweet-stats-container ')
    try:
        retweets = stats.find('a', class_='request-retweeted-popup').text
        retweets = re.sub('[^0-9]', '', retweets)
    except AttributeError:
        retweets = '0'

    try:
        likes = stats.find('a', class_='request-favorited-popup').text
        likes = re.sub('[^0-9]', '', likes)
    except AttributeError:
        likes = '0'

    return {'time': time, 'retweets': retweets, 'likes': likes}


