__author__ = 'miya'

import json
from .models import (SimplifiedObjectInfo,
                     SimplifiedBucketInfo,
                     PartInfo,
                     MultipartUploadInfo)

from .compat import urlunquote, to_unicode, to_string
from .utils import iso8601_to_unixtime, date_to_iso8601, iso8601_to_date


def parse_list_buckets(result, body):
    resp = json.loads(to_string(body))
    result.id = resp['Owner']['ID']
    result.display_name = resp['Owner']['DisplayName']
    for bucket_node in resp['Buckets']:
        result.buckets.append(SimplifiedBucketInfo(
            bucket_node['Name'],
            bucket_node['Location'],
            iso8601_to_unixtime(bucket_node['CreationDate']),
            bucket_node['ACL']
        ))
    return result

def parse_init_multipart_upload(result, body):
    resp = json.loads(to_string(body))
    result.upload_id = resp['UploadId']
    return result

def parse_list_multipart_uploads(result, body):
    resp = json.loads(to_string(body))

    result.bucket = resp['Bucket']
    result.is_truncated = resp['IsTruncated']
    result.next_upload_id_marker = resp['NextUploadIdMarker']
    for upload_node in resp['Uploads']:
        result.upload_list.append(MultipartUploadInfo(
            upload_node['Key'],
            upload_node['UploadId'],
            iso8601_to_unixtime(upload_node['Initiated'])
        ))

    return result

def parse_list_parts(result, body):
    resp = json.loads(to_string(body))
    result.is_truncated = resp['IsTruncated']
    result.next_marker = resp['NextPartNumberMarker']
    for part_node in resp['Parts']:
        result.parts.append(PartInfo(
            part_node['PartNumber'],
            part_node['ETag'],
            part_node['Size'],
            last_modified=iso8601_to_unixtime(part_node['LastModified'])
        ))
    return result


def parse_batch_delete_objects(result, body):
    if not body:
        return result
    resp = json.loads(to_string(body))
    for deleted_node in resp['Deleteds']:
        result.deleted_keys.append(deleted_node)
    for error in resp['Errors']:
        result.errors.append(error)
    return result

def parse_list_objects(result, body):
    resp = json.loads(to_string(body))
    result.is_truncated = resp[ 'IsTruncated']
    result.name = resp['Name']
    if result.is_truncated:
        result.next_marker = resp['NextMarker']
    for contents_node in resp['Contents']:
        result.object_list.append(SimplifiedObjectInfo(
            contents_node['Key'],
            iso8601_to_unixtime(contents_node['LastModified']),
            contents_node['ETag'].strip('"'),
            int(contents_node['Size']),
            contents_node['StorageClass'])
        )
    for prefix_node in resp['CommonPrefixes']:
        result.prefix_list.append(prefix_node['Prefix'])
    return result


def parse_get_bucket_location(result,body):
    resp = json.loads(to_string(body))
    result.location = resp ['LocationConstraint']

def parse_get_bucket_acl(result, body):
    resp = json.loads(to_string(body))
    result.acl = resp['AccessControlList']['Grant']
    return result
parse_get_object_acl = parse_get_bucket_acl

def parse_get_bucket_websiste(result, body):
    get_bucket_website_resp= json.loads(to_string(body))
    result.index_file = get_bucket_website_resp['IndexDocument']['Suffix']
    result.error_file = get_bucket_website_resp['ErrorDocument']['Key']
    return result



def to_complete_upload_request(parts):
    part_list=[]
    for part in parts:
        part_list.append(dict(PartNumber=part.part_number,ETag=part.etag))
    return json.dumps(dict(Parts=part_list))

def to_batch_delete_objects_request(keys, quiet):
    key_dict_list =[]

    for key in keys:
         key_dict_list.append({"Key":key})
    dict_batch_delete_objects = dict(Quiet=str(quiet).lower(),
                                     Objects=key_dict_list)
    return json.dumps(dict_batch_delete_objects)

def to_put_bucket_website(bucket_website):
    dict_put_bucket_website = dict(IndexDocument={'Suffix': bucket_website.index_file},
                                   ErrorDocument={'Key': bucket_website.error_file})

    # dict_put_bucket_website = dict(IndexDocument=dict(Suffix=bucket_website.index_file),
    #                                ErrorDocument=dict(Key=bucket_website.error_file))

    return json.dumps(dict_put_bucket_website)
