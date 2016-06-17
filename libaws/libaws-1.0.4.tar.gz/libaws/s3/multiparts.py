import argparse
import sys
import datetime
from libaws.common.boto import *
from libaws.common import config

def remove_all_multiparts(expire_day = None):
    
    parts_num = 0
    for bucket in s3.buckets.all():
        print 'remove bucket:',bucket.name,'multiparts'   
        parts_num += remove_bucket_multiparts(bucket.name,expire_day)

    return parts_num

def list_all_multiparts():

    parts_num = 0
    for bucket in s3.buckets.all():
        print 'list bucket:',bucket.name,'multiparts'   
        parts_num += list_bucket_multiparts(bucket.name)
    
    return parts_num

def remove_bucket_multiparts(bucket,expire_day = None):

    upload_id_marker = ''
    parts_num = 0
    while True:
        uploads = client_s3.list_multipart_uploads(Bucket=bucket,UploadIdMarker=upload_id_marker)
        next_upload_id = uploads['NextUploadIdMarker']
        is_truncated = uploads['IsTruncated']
        upload_id_marker = next_upload_id
        uploads = uploads.get('Uploads',[])
        for multi_part_upload in uploads:
            key = multi_part_upload['Key']
            upload_id = multi_part_upload['UploadId']
            if expire_day is not None:
                upload_create_time = multi_part_upload['Initiated']
                upload_create_time = upload_create_time.replace(tzinfo=None)
                now_time = datetime.datetime.utcnow()
                time_delta = now_time - upload_create_time
                if time_delta.days < expire_day:
                    continue

            response = client_s3.abort_multipart_upload(
                            Bucket=bucket,Key=key,UploadId=upload_id,
                            )
            print 'abort upload:',upload_id,'success'
            parts_num += 1
        if next_upload_id is None or not is_truncated:
            break

    return parts_num

def list_bucket_multiparts(bucket):

    upload_id_marker = ''
    parts_num = 0
    while True:
        uploads = client_s3.list_multipart_uploads(Bucket=bucket,UploadIdMarker=upload_id_marker)
        next_upload_id = uploads['NextUploadIdMarker']
        is_truncated = uploads['IsTruncated']
        upload_id_marker = next_upload_id
        uploads = uploads.get('Uploads',[])
        for multi_part_upload in uploads:
            key = multi_part_upload['Key']
            upload_id = multi_part_upload['UploadId']
            multipart_upload = s3.MultipartUpload(bucket,key,upload_id)
            file_obj = multipart_upload.Object()
            try:
                file_obj.e_tag
                print upload_id,multi_part_upload['Initiated']
            except:
                print upload_id,multi_part_upload['Initiated'],'upload unfinished'
            parts_num += 1

        if next_upload_id is None or not is_truncated:
            break

    return parts_num

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-bucket", "--bucket", type=str, dest="bucket",help='dest bucket to process')
    parser.add_argument("-list-all-multiparts", "--list-all-multiparts", action='store_true', dest="list_all_multiparts",help='list all multi upload parts',default = False)
    parser.add_argument("-remove-all-multiparts", "--remove-all-multiparts", action='store_true', dest="remove_all_multiparts",help='remove all multi upload parts',default=False )
    parser.add_argument("-e", "--expire", action='store_false', dest="is_bucket_expired",help='set remove bucket use expired true or false',default=True)
    parser.add_argument("-day", "--day", type=int, dest="expire_day",help='set remove bucket expire day',default=config.BUCKET_UPLOAD_EXPIRE_DAY)
    args = parser.parse_args()
    if 1 == len(sys.argv):
        parser.print_help()
        sys.exit(0)
    bucket = args.bucket
    #is_list_all_multiparts =  getattr(args,'list_all_multiparts')
    #is_remove_all_multiparts =  getattr(args,'remove_all_multiparts')
    is_list_all_multiparts =  args.list_all_multiparts
    is_remove_all_multiparts =  args.remove_all_multiparts

    if is_list_all_multiparts:
        if bucket is None:
          parts_num = list_all_multiparts()
        else:
            parts_num = list_bucket_multiparts(bucket)
        print 'total',parts_num,'multi upload parts'
    
    expire_day = args.expire_day
    if is_remove_all_multiparts:
        if not args.is_bucket_expired:
            expire_day = None
        if bucket is None:
            parts_num = remove_all_multiparts(expire_day)    
        else:
            parts_num = remove_bucket_multiparts(bucket,expire_day)
        print 'total',parts_num,'multi upload parts'

if __name__ == "__main__":
    main()
    

