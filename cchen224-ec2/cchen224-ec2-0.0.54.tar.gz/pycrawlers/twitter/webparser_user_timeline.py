import re
import requests
import json
from bs4 import BeautifulSoup


def user_timeline(screen_name, output_file='nba.csv'):
    cur_page = 0

    # screen_name, tweet, time, hashtags, cashtags, mentions, emojis, retweet_count, favorite_count
    print 'Starting search user', screen_name
    f = open(output_file, 'a')

    while True:
        cur_page += 1
        # end_tweet_id = ''
        if cur_page == 1:
            url = 'https://twitter.com/' + re.sub('\@', '', screen_name)
            html = requests.request('GET', url).text.encode('ascii', 'ignore')
        else:
            url = 'https://twitter.com/i/profiles/show/' \
                  + re.sub('\@', '', screen_name) \
                  + '/timeline/tweets?include_available_features=1&include_entities=1&max_position='\
                  + end_tweet_id\
                  + '&reset_error_state=false'
            html = json.loads(requests.request('GET', url)._content)['items_html'].strip()
        soup = BeautifulSoup(html, 'html.parser')
        tweet_cardwraps = soup.find_all('li', class_='js-stream-item stream-item stream-item expanding-stream-item ')

        if len(tweet_cardwraps) == 0:
            print 'Done!'
            break

        else:
            print cur_page,
            if cur_page % 10 == 0:
                print '\n'

            for tweet_cardwrap in tweet_cardwraps:
                out = dict()
                hashtags = []
                cashtags = []
                mentions = []
                emojis = []
                try:
                    a_hrefs = tweet_cardwrap.find('div', class_='js-tweet-text-container').p(['a', 'img'])
                    for s in a_hrefs:
                        if s.has_attr('data-expanded-url'):
                            s.extract()
                        elif s.has_attr('data-query-source'):
                            if s.attrs['data-query-source'] == 'cashtag_click':
                                cashtags.append(s.text.strip())
                            elif s.attrs['data-query-source'] == 'hashtag_click':
                                hashtags.append(s.text.strip())
                            # s.extract()
                        elif s.has_attr('data-mentioned-user-id'):
                            mentions.append(s.attrs['data-mentioned-user-id'])
                            # s.extract()
                        elif 'Emoji--forText' in s.attrs['class']:
                            emojis.append('_'.join(s.attrs['title'].split()))
                            s.extract()
                except TypeError:
                    pass
                except AttributeError:
                    continue

                timestamp = tweet_cardwrap.find('a', class_='tweet-timestamp js-permalink js-nav js-tooltip')
                time = timestamp['title']

                text = tweet_cardwrap.find('div', class_='js-tweet-text-container').text
                text = re.sub('[^0-9a-zA-Z\[\]\#\@\$/\.\: ]', ' ', text)
                text = re.sub(' +', ' ', text).strip()

                out['tweet'] =  text
                out['hashtags'] = '|'.join(hashtags)
                out['cashtags'] = '|'.join(cashtags)
                out['mentions'] = '|'.join(mentions)
                out['emojis'] = '|'.join(emojis)
                out['time'] = time
                out['retweet'] = tweet_cardwrap.find('div', class_='ProfileTweet-action ProfileTweet-action--retweet js-toggleState js-toggleRt') \
                    .find('span', class_='ProfileTweet-actionCountForPresentation').text.strip()
                out['favorite'] = tweet_cardwrap.find('div', class_='ProfileTweet-action ProfileTweet-action--favorite js-toggleState') \
                    .find('span', class_='ProfileTweet-actionCountForPresentation').text.strip()

                # screen_name,tweet,time,hashtags,cashtags,mentions,emojis,retweet_count,favorite_count
                f.write(','.join([screen_name, out['tweet'], out['time'],
                                  out['hashtags'], out['cashtags'], out['mentions'], out['emojis'],
                                  out['retweet'], out['favorite']]))
                f.write('\n')

            end_tweet_id = tweet_cardwraps[-1].attrs['data-item-id']

    f.close()


# test
# user_timeline('LeBronJames')
# with open('/Users/cchen224/Downloads/target.html', 'a') as f:
#     f.write(html)