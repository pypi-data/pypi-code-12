from boto import *
import argparse
import datetime

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
        uploads = client.list_multipart_uploads(Bucket=bucket,UploadIdMarker=upload_id_marker)
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

            response = client.abort_multipart_upload(
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
        uploads = client.list_multipart_uploads(Bucket=bucket,UploadIdMarker=upload_id_marker)
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
