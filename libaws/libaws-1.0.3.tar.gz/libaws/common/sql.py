#coding:utf-8
'''
    下载，上传相关的创建表sql语句文件

    [upload]表结构:
    表示文件上传对象
    id: 上传id,唯一自增
    s3_upload:id: s3返回的上传id
    bucket: 上传bucket
    key: bucket上的文件名
    status: 上传状态
    part_num: 上传分块个数
    total_size: 上传文件的大小
    upload_size: 已经上传的字节数
    upload_percent: 上传百分比
    is_upload: 是否已经上传成功
    e_tag: 上传成功后返回s3文件的e_tag值
    start_time: 上传开始时间
    end_time: 上传结束时间
    file_id: 关联的上传文件id


    [part]表结构
    表示分解上传分块对象
    id: 分块id,唯一自增
    part_id: 上传分块的序号
    part_size: 分块的大小
    start_byte: 分块在文件的开始字节
    end_byte: 分块在文件的结束字节
    status: 分块上传状态
    is_upload: 分块是否上传成功
    etag: 分块内容的md5值
    start_time: 分块上传开始时间
    end_time: 分块上传结束时间
    is_last_part: 是否是最后一个分块
    upload_id：关联的上传id

    [file]表结构
    表示上传文件对象
    id: 文件id,唯一自增
    name: 上传文件名
    path: 上传文件完整名称
    hash: 文件的md5值
    size: 文件的大小
    time: 文件的创建时间

    [download]表结构
    表示下载对象
    id: 下载id,唯一自增
    bucket: 下载bucket
    key: 要下载的bucket里面的文件
    filepath: 下载到本地的文件路径名
    filename: 本地文件名
    tmp_file_path: 下载临时文件路径名
    dest_path: 下载路径
    status: 下载状态
    file_size: 下载文件的大小
    download_size: 已经下载的文件字节数
    download_percent: 下载进度百分比
    is_download: 下载是否成功
    etag: 下载文件s3上存储的hash值
    hash: 文件下载到本地后，计算文件的hash值
    start_time: 文件下载开始时间
    end_time: 文件下载结束时间
    range_num: 文件下载分块个数

    [range]下载分块表结构
    表示下载分块对象
    id: 分块id,唯一自增
    range_id: 下载分块的序号
    range_size: 分块的大小
    start_byte: 分块在文件的开始字节
    end_byte: 分块在文件的结束字节
    status: 分块下载状态
    is_download: 分块是否下载成功
    hash: 分块内容的md5值
    start_time: 分块下载开始时间
    end_time: 分块下载结束时间
    is_last_part: 是否是最后一个分块
    download_id：关联的下载id
'''

import config

CREATE_UPLOAD_TABLE_SQL = '''
    CREATE TABLE %s (
        id INTEGER primary key autoincrement,
        s3_upload_id text,
        bucket varchar (100),
        key varchar (260),
        status int,
        part_num int,
        total_size BIGINT,
        upload_size BIGINT default 0,
        upload_percent varchar(10) default '0.0%%',
        is_upload BOOLEAN default 0,
        etag varchar (100),
        start_time datetime,
        end_time datetime,
        created_time default (datetime('now', 'localtime')),
        updated_time default (datetime('now', 'localtime')),
        file_id int,
        FOREIGN KEY(file_id) REFERENCES file(id)
    )
''' % (config.UPLOAD_TABLE)


CREATE_PART_TABLE_SQL = '''
    CREATE TABLE %s  (
        id INTEGER primary key autoincrement,
        part_id int,
        part_size BIGINT,
        start_byte BIGINT,
        status int,
        is_upload BOOLEAN default 0,
        end_byte BIGINT,
        etag varchar (100),
        start_time datetime,
        end_time datetime,
        is_last_part BOOLEAN default 0,
        created_time default (datetime('now', 'localtime')),
        updated_time default (datetime('now', 'localtime')),
        upload_id int,
        FOREIGN KEY(upload_id) REFERENCES upload(id)
    )

''' % (config.UPLOAD_PART_TABLE)


CREATE_FILE_TABLE_SQL = '''
    CREATE TABLE %s (
        id INTEGER primary key autoincrement,
        name varchar(260),
        path varchar(300),
        hash varchar(200),
        size BIGINT,
        time datetime,
        created_time default (datetime('now', 'localtime')),
        updated_time default (datetime('now', 'localtime'))
    )
''' % (config.UPLOAD_FILE_TABLE)

CREATE_DOWNLOAD_TABLE_SQL = '''
    CREATE TABLE %s (
        id INTEGER primary key autoincrement,
        bucket varchar (100),
        key varchar (260),
        filepath varchar (260),
        filename varchar (260),
        tmp_file_path varchar (260),
        dest_path varchar (260),
        status int,
        file_size BIGINT,
        download_size BIGINT default 0,
        download_percent varchar(10) default '0.0%%',
        is_download BOOLEAN default 0,
        etag varchar (100),
        hash varchar (100),
        start_time datetime,
        end_time datetime,
        range_num int,
        created_time default (datetime('now', 'localtime')),
        updated_time default (datetime('now', 'localtime'))
    )
''' % (config.DOWNLOAD_TABLE)


CREATE_DOWNLOAD_RNAGE_TABLE_SQL = '''
    CREATE TABLE %s  (
        id INTEGER primary key autoincrement,
        range_id int,
        range_size BIGINT,
        start_byte BIGINT,
        status int,
        is_download BOOLEAN default 0,
        end_byte BIGINT,
        hash varchar (100),
        start_time datetime,
        end_time datetime,
        is_last_range BOOLEAN default 0,
        download_size BIGINT default 0,
        created_time default (datetime('now', 'localtime')),
        updated_time default (datetime('now', 'localtime')),
        download_id int,
        FOREIGN KEY(download_id) REFERENCES download(id)
    )

''' % (config.DOWNLOAD_RANGE_TABLE)


