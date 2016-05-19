import time

import tweepy


def get_followers_ids(screen_name, account):

    auth = tweepy.OAuthHandler(account['consumer_key'], account['consumer_secret'])
    auth.set_access_token(account['access_key'], account['access_secret'])
    api = tweepy.API(auth)

    f = open(screen_name + '_followings.txt', 'w+')
    current_page = 1
    followings = tweepy.Cursor(api.friends_ids, screen_name=screen_name).pages()
    print 'Starting collect ' + screen_name
    while True:
        try:
            print '\tGetting page ' + str(current_page)
            ids = followings.next()
            for i in ids:
                f.write(str(i) + '\n')
            current_page += 1
            time.sleep(60)
        except tweepy.TweepError:
            print '\tWaiting on rate limit.'
            time.sleep(60)
        except StopIteration:
            print screen_name + ' Done!\n\n\n'
            break
    f.close()
