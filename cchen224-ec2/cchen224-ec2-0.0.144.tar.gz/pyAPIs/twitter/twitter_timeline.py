import time

import tweepy


def get_followers_ids(user_id, account):

    auth = tweepy.OAuthHandler(account['consumer_key'], account['consumer_secret'])
    auth.set_access_token(account['access_key'], account['access_secret'])
    api = tweepy.API(auth)

    # f = open(user_id + '_followings.txt', 'w+')
    current_page = 1
    user_timeline = tweepy.Cursor(api.user_timeline, user_id=user_id, since_id=696163960001679361, max_id=None, lang='en').pages()
    # print 'Starting collect ' + screen_name
    while True:
        try:
            print '\tGetting page ' + str(current_page)
            ids = user_timeline.next()
            # for i in ids:
                # f.write(str(i) + '\n')
            current_page += 1
            time.sleep(60)
        except tweepy.TweepError:
            print '\tWaiting on rate limit.'
            time.sleep(60)
        except StopIteration:
            # print screen_name + ' Done!\n\n\n'
            break
    f.close()


import json
f = open('/Users/cchen224/Downloads/tweets_07.json')
file = json.load(f)



user_id=2634592777