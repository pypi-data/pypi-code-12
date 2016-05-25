import csv
import time
import traceback

from bs4 import BeautifulSoup
from cutils import Gmail
from cutils import ProgressBar

from webparser_utility import *


def parse_user_info(user_id, **kwargs):
    """
    :param user_id:
    :return: user_id, is_verified, bio, location, join_date, tweets, following, followers, likes, profile_picture
    """
    has_profile_header = kwargs.get('header', True)
    has_profile_navigation = kwargs.get('navigation', True)
    has_profile_picture = kwargs.get('picture', True)

    url = 'https://twitter.com/' + str(user_id)
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    out = [user_id]
    if has_profile_header:
        out.extend(parse_profile_header(soup.find('div', class_='ProfileHeaderCard')))
    if has_profile_navigation:
        out.extend(parse_profile_navigation(soup.find('div', class_='ProfileNav')))
    if has_profile_picture:
        out.extend(parse_profile_picture(soup))
    return [out]


def parse_profile_header(profile_header_soup):
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

    return [is_verified, bio, location, join_date]


def parse_profile_navigation(profile_navigation_soup):
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
    return [tweets, following, followers, likes]


def parse_profile_picture(soup):
    pic_url = soup.find('img', class_='ProfileAvatar-image').attrs.get('src')
    return [pic_url.encode('utf-8')]


def crawl_user_info(input, output):
    gmail = Gmail().set_from_to().set_subject('AWS Twitter.info').send_message(input + '\n\n\n')
    print 'Starting...'

    if isinstance(input, str):
        with open(input, 'r') as i:
            users = [line.strip() for line in i]
    if isinstance(input, list):
        users = input

    bar = ProgressBar(total=len(users))
    with open(output, 'a') as o:
        csvwriter = csv.writer(o)
        for user in users:
            bar.move().log()
            if random.uniform(0, 1) > 0.999:
                time.sleep(random.uniform(4, 6))
            try:
                gmail = gmail.send_message(' User ' + user + '...')
                csvwriter.writerow(parse_user_info(user))
                gmail = gmail.send_message('Done!\n')
            except KeyboardInterrupt:
                gmail = gmail.send_message('KeyboardInterrupt.\n')
                break
            except:
                Gmail().set_from_to().set_subject('AWS Twitter.info Error') \
                    .send_message(input + ':user ' + user + '\n' + traceback.format_exc()).close()
        gmail.send_message('\n\n' + '\nDone').close()
    bar.close()
