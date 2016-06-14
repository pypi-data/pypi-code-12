
import  cos2
import uuid
import os


if __name__ == '__main__':

    COS_ID = os.getenv("COS_TEST_ACCESS_KEY_ID")
    COS_SECRET = os.getenv("COS_TEST_ACCESS_KEY_SECRET")
    COS_ENDPOINT = os.getenv("COS_TEST_ENDPOINT")
    COS_BUCKET =  os.getenv("COS_TEST_BUCKET")
    COS_WEBSITE_ENDPOINT = os.getenv("COS_WEBSITE_ENDPOINT")

# print bucketName
    print '==========================================='
    print 'Getting Started with COS SDK for Python'
    print '===========================================\n'

# Init COS Python SDK
    auth = cos2.Auth(COS_ID, COS_SECRET)
    bucket = cos2.Bucket(auth, COS_ENDPOINT, COS_BUCKET)

# Create a new COS PublicRead bucket
    print 'Creating bucket ' + COS_BUCKET
# bucket.create_bucket(cos2.BUCKET_ACL_PUBLIC_READ)
    bucket.create_bucket()

# List the buckets in your account
    print 'Listing buckets'
    service = cos2.Service(auth, COS_ENDPOINT, connect_timeout=30)
    for bucketInfo in service.list_buckets().buckets:
        print ' - ' + bucketInfo.name

# Upload an object to your bucket
    print 'Uploading a new object to COS from memory'
    content = 'Thank you for using COS SDK for Python'
    bucket.put_object("cos-test-object", content)


# Determine whether an object residents in your bucket
    exist = bucket.object_exists("cos-test-object")
    print(bucket.get_object("cos-test-object").read())
