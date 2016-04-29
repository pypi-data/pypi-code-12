import re
import sys
import traceback

import requests
from bs4 import BeautifulSoup

from gmail import Gmail


def get_user_info(user_id):

    url = 'https://twitter.com/' + str(user_id)
    html = requests.request('GET', url).text.encode('ascii', 'ignore')
    soup = BeautifulSoup(html, 'html.parser')
    out = dict()

    profile_navigation_soup = soup.find('div', class_='ProfileNav')
    try:
        out['tweets'] = profile_navigation_soup.find('li', class_='ProfileNav-item ProfileNav-item--tweets is-active').a.attrs['title']
    except AttributeError:
        out['tweets'] = str(0)
    try:
        out['following'] = profile_navigation_soup.find('li', class_='ProfileNav-item ProfileNav-item--following').a.attrs['title']
    except AttributeError:
        out['following'] = str(0)
    try:
        out['followers'] = profile_navigation_soup.find('li', class_='ProfileNav-item ProfileNav-item--followers').a.attrs['title']
    except AttributeError:
        out['followers'] = str(0)
    try:
        out['likes'] = profile_navigation_soup.find('li', class_='ProfileNav-item ProfileNav-item--favorites').a.attrs['title']
    except AttributeError:
        out['likes'] = str(0)

    out['tweets'] = re.sub(' Tweets| Tweet|,', '', out['tweets'])
    out['following'] = re.sub(' Following|,', '', out['following'])
    out['followers'] = re.sub(' Followers| Follower|,', '', out['followers'])
    out['likes'] = re.sub(' Likes| Like|,', '', out['likes'])


    profile_header_soup = soup.find('div', class_='ProfileHeaderCard')
    try:
        out['bio'] = profile_header_soup.find('p', class_='ProfileHeaderCard-bio u-dir').text.strip()
        out['bio'] = re.sub('"|\n', '', out['bio'])
    except AttributeError:
        out['bio'] = ''
    try:
        out['location'] = profile_header_soup.find('div', class_='ProfileHeaderCard-location').text.strip()
    except AttributeError:
        out['location'] = ''
    try:
        out['join_date'] = profile_header_soup.find('div', class_='ProfileHeaderCard-joinDate').text.strip()
    except AttributeError:
        out['join_date'] = ''
    try:
        out['is_verified'] = profile_header_soup.h1.span.text.strip()
        if out['is_verified'] == 'Verified account':
            out['is_verified'] = 'yes'
        else:
            out['is_verified'] = 'no'
    except AttributeError:
        out['is_verified'] = 'no'

    return out

if __name__ == '__main__':
    argvs = sys.argv[1:]
    input = argvs[0]
    output = input + '.csv'
    gmail = Gmail(0).set_from_to().set_subject('AWS_CustomerNameClean')
    print 'Starting...'
    f = open(input, 'r')
    o = open(output, 'a')
    i = 0
    for line in f:
        i += 1
        if i % 1000 == 0:
            print i,
        user = line.strip()
        info = get_user_info(user)
        try:
            # screen_name,is_verified,bio,location,join_date,tweets,following,followers,likes
            o.write(','.join([user, info['is_verified'],
                          '"' + info['bio'] + '"', '"' + info['location'] + '"', '"' + info['join_date'] + '"',
                          info['tweets'], info['following'], info['followers'], info['likes']]).encode('ascii', 'ignore'))
            o.write('\n')
        except:
            gmail = gmail.send_message(input + ': user ' + user + '\n' + traceback.format_exc())
    f.close()
    o.close()
    gmail = gmail.send_message(input + '\nDone')


