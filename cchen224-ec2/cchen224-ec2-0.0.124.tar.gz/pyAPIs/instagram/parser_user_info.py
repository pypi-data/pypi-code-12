import re


def parse_user_info(user):
    userid = user.id
    username = user.username.encode('utf-8')#.encode('ascii', 'ignore')
    NoFollower = user.counts.get('followed_by')
    NoFriends = user.counts.get('follows')
    NoMedia = user.counts.get('media')
    userWebsite = user.website.encode('utf-8')#.encode('ascii', 'ignore')
    userBio = user.bio.encode('utf-8')#.encode('ascii', 'ignore')
    userBio = re.sub('\n|"', ' ', userBio)
    userBio = re.sub(' +', ' ', userBio)
    userProfilePic = user.profile_picture.encode('utf-8')#.encode('ascii', 'ignore')

    return [userid,
            username,
            NoFollower,
            NoFriends,
            NoMedia,
            userWebsite,
            userBio,
            userProfilePic]
