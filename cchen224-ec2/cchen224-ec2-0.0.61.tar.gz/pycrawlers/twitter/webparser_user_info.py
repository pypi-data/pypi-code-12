import re
import sys
import traceback
import csv

import requests
from bs4 import BeautifulSoup

from cutils import Gmail
from cutils import ProgressBar


def get_user_info(user_id):
    url = 'https://twitter.com/' + str(user_id)
    html = requests.request('GET', url).text
    soup = BeautifulSoup(html, 'html.parser')

    profile_navigation_soup = soup.find('div', class_='ProfileNav')
    try:
        tweets = profile_navigation_soup.find('li', class_='ProfileNav-item ProfileNav-item--tweets is-active').a.attrs['title']
    except AttributeError:
        tweets = str(0)
    try:
        following = profile_navigation_soup.find('li', class_='ProfileNav-item ProfileNav-item--following').a.attrs['title']
    except AttributeError:
        following = str(0)
    try:
        followers = profile_navigation_soup.find('li', class_='ProfileNav-item ProfileNav-item--followers').a.attrs['title']
    except AttributeError:
        followers = str(0)
    try:
        likes = profile_navigation_soup.find('li', class_='ProfileNav-item ProfileNav-item--favorites').a.attrs['title']
    except AttributeError:
        likes = str(0)

    tweets = re.sub(' Tweets| Tweet|,', '', tweets)
    following = re.sub(' Following|,', '', following)
    followers = re.sub(' Followers| Follower|,', '', followers)
    likes = re.sub(' Likes| Like|,', '', likes)


    profile_header_soup = soup.find('div', class_='ProfileHeaderCard')
    try:
        bio = profile_header_soup.find('p', class_='ProfileHeaderCard-bio u-dir').text.strip()
        bio = re.sub('"|\n|\t', '', bio).encode('utf-8')
    except AttributeError:
        bio = ''
    try:
        location = profile_header_soup.find('div', class_='ProfileHeaderCard-location').text.strip().encode('utf-8')
    except AttributeError:
        location = ''
    try:
        join_date = profile_header_soup.find('div', class_='ProfileHeaderCard-joinDate').text.strip()
    except AttributeError:
        join_date = ''
    try:
        is_verified = profile_header_soup.h1.span.text.strip()
        if is_verified == 'Verified account':
            is_verified = 'yes'
        else:
            is_verified = 'no'
    except AttributeError:
        is_verified = 'no'

    return [user_id,
            is_verified,
            bio,
            location,
            join_date,
            tweets,
            following,
            followers,
            likes]


def crawl_user_info(input, output):
    gmail = Gmail().set_from_to().set_subject('AWS Twitter.info').send_message(input + '\n')
    print 'Starting...'

    if isinstance(input, str):
        with open(input, 'r') as i:
            users = [line.strip() for line in i]
    if isinstance(input, list):
        users = input
    if isinstance(input, int):
        users = [str(int)]

    bar = ProgressBar(total=len(users))
    with open(output, 'a') as o:
        csvwriter = csv.writer(o)
        for user in users:
            bar.skip_move()
            try:
                gmail.send_message('User' + user + '...')
                csvwriter.writerow(get_user_info(user))
                gmail.send_message('Done!\n')
            except:
                Gmail().set_from_to().set_subject('AWS Twitter.info Error')\
                    .send_message(input + ':user ' + user + '\n' + traceback.format_exc()).close()
        gmail.send_message('\n\n' + input + '\nDone').close()
    bar.close()


if __name__ == '__main__':
    argvs = sys.argv[1:]
    input = argvs[0]
    output = input + '.csv'
    crawl_user_info(input, output)
