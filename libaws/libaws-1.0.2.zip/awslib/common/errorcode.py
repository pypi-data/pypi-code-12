#coding:utf-8
'''
    错误码文件
'''
BUCKET_FILE_NOT_EXISTS = 0
UPLOAD_FILE_NOT_EXISTS = 1
BUCKET_NOT_EXISTS = 2
BUCKET_UPLOAD_FILE_EXISTS = 3
DOWNLOAD_AGAIN_FILE_SUCCESS = 4
UPLOAD_AGAIN_FILE_SUCCESS = 5
EXCEED_MAX_DOWNLOAD_ATTEMPTS = 6
EXCEED_MAX_UPLOAD_ATTEMPTS = 7
OPEN_FILE_ERROR = 8
UPLOAD_PART_MD5_MATCH_ERROR = 9

ERROR_CODE_MESSAGES = {
    BUCKET_FILE_NOT_EXISTS:'file {} is not exist in bucket {}',
    UPLOAD_FILE_NOT_EXISTS:'file {} is not exist in local computer',
    BUCKET_NOT_EXISTS :'bucket {} is not exist',
    BUCKET_UPLOAD_FILE_EXISTS :'key {} is already exist in bucket {},if u want to upload replace it,please use -ignore-bucket-file param',
    DOWNLOAD_AGAIN_FILE_SUCCESS:'download file {} has already download success,if u want to download again use -force-again-download param',
    UPLOAD_AGAIN_FILE_SUCCESS:'file {} has already upload to bucket {},if u want to upload again use -force-again-upload param',
    EXCEED_MAX_DOWNLOAD_ATTEMPTS:'download retry times exceed max attemps',
    EXCEED_MAX_UPLOAD_ATTEMPTS:'upload retry times exceed max attemps',
    OPEN_FILE_ERROR:'open file {} error',
    UPLOAD_PART_MD5_MATCH_ERROR:'upload part md5 is not match',
}
