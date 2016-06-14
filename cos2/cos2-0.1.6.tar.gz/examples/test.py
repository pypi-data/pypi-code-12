# -*- coding: utf-8 -*-

import os
import cos2

COS_ID = os.getenv("COS_TEST_ACCESS_KEY_ID","6fb51794f303431d88ba78af3e807550")
COS_SECRET = os.getenv("COS_TEST_ACCESS_KEY_SECRET","929c01e27bbe465392868db05e2ceba1")
COS_ENDPOINT = os.getenv("COS_TEST_ENDPOINT","cos-beta.chinac.com")
COS_BUCKET =  os.getenv("COS_TEST_BUCKET","img-sample")
COS_WEBSITE_ENDPOINT = os.getenv("COS_WEBSITE_ENDPOINT","cos-beta-website.chinac.com")

auth = cos2.Auth(COS_ID, COS_SECRET)
service = cos2.Service(auth, COS_ENDPOINT)
bucket = cos2.Bucket(auth,COS_ENDPOINT,COS_BUCKET)
bucket.put_object_from_file("test.mp4","/Users/miya/Downloads/test.mp4")




#bucket.create_bucket("public-read")
#bucket.delete_bucket()
#for objectinfo in bucket.list_objects().object_list:

for objectinfo in bucket.list_objects().object_list:
          #bucket.delete_object(objectinfo.key)
          print(objectinfo.key)

#bucket.delete_bucket()
#print(objectinfo.key)


#bucket.create_bucket()
for bucketinfo in service.list_buckets().buckets:
     print(bucketinfo.name)
#     bucket = cos2.Bucket(auth, COS_ENDPOINT, bucketinfo.name)
#
