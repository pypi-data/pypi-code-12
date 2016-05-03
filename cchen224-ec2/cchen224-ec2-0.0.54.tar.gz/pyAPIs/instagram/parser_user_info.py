
def parse_user_info(user):
    userid = user.id
    username = user.username
    NoFollower = user.counts.get('followed_by')
    NoFriends = user.counts.get('follows')
    NoMedia = user.counts.get('media')
    userWebsite = user.website
    userBio = user.bio.encode('utf-8')
    userProfilePic = user.profile_picture

    return [userid,username,NoFollower,NoFriends,NoMedia,userWebsite,userBio,userProfilePic]