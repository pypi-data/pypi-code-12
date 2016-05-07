import re


def parse_media(item):
    photo_caption = re.sub('\n|"', '', item.caption.text.encode('utf-8')) if item.caption is not None else ''
    photo_comment = item.comment_count
    created_time = item.created_time
    photo_filter = item.filter
    photo_id = item.id
    photo_url = item.images.get('standard_resolution').url
    photo_like = item.like_count
    photo_link = item.link
    tags = item.tags if hasattr(item, 'tag') else ''
    item_type = item.type
    user_username = item.user.username.encode('utf-8')
    user_id = item.user.id
    photo_userliked = item.user_has_liked

    users_in_photo = item.users_in_photo
    usernames = '|'.join([user.user.id for user in users_in_photo])
    no_users_in_photo = len(users_in_photo)
    # if len(users_in_photo) > 0:
    #     no_users_in_photo = len(users_in_photo)
    #
    # else:
    #     no_users_in_photo = 0
    #     usernames = ''

    if hasattr(item, 'location'):
        location_disclosed = 1
        photo_location_id = item.location.id
        # print item.location.point
        photo_location_name = item.location.name.encode('utf-8')
        if item.location.point is None:
            photo_location_lat = ''
            photo_location_long = ''
        else:
            photo_location_lat = item.location.point.latitude
            photo_location_long = item.location.point.longitude
    else:
        location_disclosed = 0
        photo_location_id = ''
        photo_location_name = ''
        photo_location_lat = ''
        photo_location_long = ''


    return [user_id,
            user_username,
            photo_id,
            created_time,
            photo_caption,
            photo_filter,
            photo_link,
            photo_url,
            item_type,
            photo_like,
            photo_comment,
            photo_userliked,
            tags,
            no_users_in_photo,
            usernames,
            location_disclosed,
            photo_location_id,
            photo_location_name,
            photo_location_lat,
            photo_location_long]
