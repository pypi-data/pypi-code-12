from main import InstagramAPI, client, oauth2, InstagramAPIError
from main.bind import InstagramAPIError
import csv
from time import sleep
from datetime import datetime
import os
import sys



# access_token = '937212526.80bcce7.4 1f9aea947504150b418c4d60d159929'
#access_token = '937212526.d2aec0b.24b8d6c3940643a592b5c72512e42d4c'
#access_token = '937212526.5f06f7a.90966e83f9dd43eeb1fac3d135abed24'
#access_token = '937212526.35519fe.91c4ebdf62444231b36df3066a9a62e1'
#access_token = '937212526.d356296.1ec199e742b540b69017d1fdc0838404'
#access_token = '937280448.63a8f6e.f08c72c5df0a46099da1c17b2022b4ef'
#access_token = '937280448.09bccc4.d4c901f227464006a60b7367f92c023d'
#access_token = '937280448.948a325.347e49226f974a718765c8611720f780'
#access_token = '937280448.197d7e4.0ba69739bf02428782546dbdacc9337f'
#access_token = '937280448.5182a49.11af1a709c9c4fa7b9c96a4f6bb38ac7'
#access_token = '937358110.64ee73f.9ea27205a93d485a932fbbd771122574'
#access_token = '937358110.a358ce4.de1b7e677c86409ca93916e972c7d2d0'
#access_token = '937358110.7de18ec.01ef8f2c7591467b99285e0f8abb0b20'
#access_token = '937358110.38e9503.edb2757a445e48bb9cbf35a90ac60ede'
#access_token = '937358110.7781482.f19e57cac4cd455b8c3d68ed1c3d1462'
# access_token = '938075294.a594a2a.0924280c580147b5b43ba715a3f90052'
#access_token = '938075294.8576c14.dbd08371297f4956bc3f9142b4ba5944'
#access_token = '938075294.93b5a61.a03807e6e0c848e1adda4722f5aafc6d'
#access_token = '938075294.71ab8b9.97fbee0735a64f8c90dcbaeca7457f7e'
#access_token = '938075294.938bcc8.09a1241cf00e4a6fb899207704749a17'

#new
# access_token = '616474981.003c66c.42dfbdb746d149469331f3acd0300455'
#access_token=616474981.ed555dc.8e8e521b689e4bbbb58c611d8fb628dd
#access_token=616474981.a822b83.c3af254747c849ee8b6c1469e0bd0186
#access_token=616474981.86f3a3d.b59f6439980049b2b3383bda9f2f5c5d
#access_token=616474981.bfe25b6.3a90d1a792b142dfb70dce8e4b606c34

#accessToken = sys.argv[1]
# filetoread = sys.argv[1]
# dir = sys.argv[2]
# errorfile = sys.argv[3]

api = InstagramAPI(access_token=access_token)

def GetPhotoByUsername(uid):
     try:
        for recent_media in api.user_recent_media(user_id=uid, as_generator=True, max_pages=60): #only one page
            global j
            j += len(recent_media[0])
            for item in recent_media[0]:
                if item.caption is not None: #can be no caption
                    photo_caption = item.caption.text.encode('utf-8')
                else:
                    photo_caption = ''
                # print photo_caption
                photo_comment = item.comment_count
                created_time = item.created_time
                photo_filter = item.filter
                photo_id = item.id
                photo_url = item.images.get('standard_resolution').url
                photo_like = item.like_count
                photo_link = item.link
                if hasattr(item, 'tag'): #can be no caption
                    tags = item.tags
                else:
                    tags = ''
                item_type = item.type
                user_username = item.user.username.encode('utf-8')
                user_id = item.user.id
                photo_userliked = item.user_has_liked
                users_in_photo = item.users_in_photo
                if len(users_in_photo) > 0:
                    no_users_in_photo = len(users_in_photo)
                    usernames = ''
                    for user in users_in_photo:
                        usernames += user.user.id + ','
                else:
                    no_users_in_photo = 0
                    usernames = ''

                if hasattr(item, 'location'):
                    location_disclosed = 1
                    photo_location_id = item.location.id
                    # print item.location.point
                    photo_location_name = item.location.name.encode('utf-8')
                    photo_location_lat = item.location.point.latitude
                    photo_location_long = item.location.point.longitude

                else:
                    location_disclosed = 0
                    photo_location_id = ''
                    photo_location_name = ''
                    photo_location_lat = ''
                    photo_location_long = ''

                writer.writerow([user_id,user_username,photo_id,created_time,photo_caption,photo_filter,photo_link,photo_url,item_type,photo_like,photo_comment,photo_userliked,tags,no_users_in_photo,usernames,location_disclosed,photo_location_id,photo_location_name,photo_location_lat,photo_location_long])
     except Exception as e:
         print e,
         errorwriter.writerow([uid,str(datetime.now())])


uid = '628056564'
uid = '9273671' #shulei test

lines = [line.rstrip('\n') for line in open('/Users/hyheng/Dropbox/Instagram-projects/ids_merge_sample.txt')]


index = 0
j = 0

# with open('/Users/hyheng/Dropbox/Instagram-projects/merge de-outlier-sample.csv', 'rb') as fin:
with open('/Users/hyheng/Dropbox/Instagram-projects/data/test_csv_res.csv', 'a') as fout:
    with open('/Users/hyheng/Dropbox/Instagram-projects/data/test_csv_res[error].csv', 'a') as ferror:

        # reader = csv.reader(fin)
        writer = csv.writer(fout)
        errorwriter = csv.writer(ferror)

        # for row in reader:
        #     uid = row[0]
        for line in lines[index:]:
            GetPhotoByUsername(line)
            # print line
            # j += 1
            if j % 20 is 0:
                res = j/20
            else:
                res = j/20 + 1
            print res
            if res >= 4800:
                print 'sleep - ' + str(datetime.now())
                sleep(3300)
                j = 0


