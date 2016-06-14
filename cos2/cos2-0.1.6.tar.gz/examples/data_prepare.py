
import os
import cos2
import random


COS_ENDPOINT = os.getenv("COS_TEST_ENDPOINT","http://cos-cn-guangzhou.chinac.com")
COS_WEBSITE_ENDPOINT = os.getenv("COS_WEBSITE_ENDPOINT","http://cos-cn-guangzhou-website.chinac.com")

bucket_src_auth = cos2.Auth("e1eacdfd85df47589a7712251271ec46", "b2a7d846a9e24832a9b1e614caa404a1")
bucket_src = cos2.Bucket(bucket_src_auth,COS_ENDPOINT,"cos-test")

bucket_dst_auth = cos2.Auth("ad039afdb6614e4994a177474dee1356", "d7844d2510d74036825bf21126d48bd8")
bucket_dst = cos2.Bucket(bucket_src_auth,COS_ENDPOINT,"cos-perf-test-1m")


object_list = bucket_src.list_objects().object_list
bucket_dst.create_bucket("public-read")

# for i in range(500,10000):
#      src_objectName =object_list[random.randint(0,len(object_list)-1)].key
#      data = bucket_src.get_object(src_objectName)
#      dst_objectName="img-"+str(i)
#      bucket_dst.put_object(dst_objectName,data)
#      print(src_objectName,dst_objectName)
