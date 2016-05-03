import re


def parse_user_info(user):
    userid = user.id
    username = user.username.encode('utf-8')
    NoFollower = user.counts.get('followed_by')
    NoFriends = user.counts.get('follows')
    NoMedia = user.counts.get('media')
    userWebsite = user.website
    userBio = user.bio.encode('utf-8')
    userBio = re.sub('\n|"', ' ', userBio)
    userBio = re.sub(' +', ' ', userBio)
    userProfilePic = user.profile_picture

    return [userid,
            username.encode('ascii', 'ignore'),
            NoFollower,
            NoFriends,
            NoMedia,
            userWebsite.encode('ascii', 'ignore'),
            userBio.encode('ascii', 'ignore'),
            userProfilePic.encode('ascii', 'ignore')]