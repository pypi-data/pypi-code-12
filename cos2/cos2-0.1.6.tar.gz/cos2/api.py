# -*- coding: utf-8 -*-

"""
文件上传方法中的data参数
------------------------
诸如 :func:`put_object <Bucket.put_object>` 这样的上传接口都会有 `data` 参数用于接收用户数据。`data` 可以是下述类型
    - unicode类型（对于Python3则是str类型）：内部会自动转换为UTF-8的bytes
    - bytes类型：不做任何转换
    - file-like object：对于可以seek和tell的file object，从当前位置读取直到结束。其他类型，请确保当前位置是文件开始。
    - 可迭代类型：对于无法探知长度的数据，要求一定是可迭代的。此时会通过Chunked Encoding传输。


返回值
------
:class:`Service` 和 :class:`Bucket` 类的大多数方法都是返回 :class:`RequestResult <cos2.models.RequestResult>`
及其子类。`RequestResult` 包含了HTTP响应的状态码、头部以及COS Request ID，而它的子类则包含用户真正想要的结果。例如，
`ListBucketsResult.buckets` 就是返回的Bucket信息列表；`GetObjectResult` 则是一个file-like object，可以调用 `read()` 来获取响应的
HTTP包体。


异常
----
一般来说Python SDK可能会抛出三种类型的异常，这些异常都继承于 :class:`CosError <cos2.exceptions.CosError>` ：
    - :class:`ClientError <cos2.exceptions.ClientError>` ：由于用户参数错误而引发的异常；
    - :class:`ServerError <cos2.exceptions.ServerError>` 及其子类：COS服务器返回非成功的状态码，如4xx或5xx；
    - :class:`RequestError <cos2.exceptions.RequestError>` ：底层requests库抛出的异常，如DNS解析错误，超时等；
当然，`Bucket.put_object_from_file` 和 `Bucket.get_object_to_file` 这类函数还会抛出文件相关的异常。


.. _byte_range:

指定下载范围
------------
诸如 :func:`get_object <Bucket.get_object>` 以及 :func:`upload_part_copy <Bucket.upload_part_copy>` 这样的函数，可以接受
`byte_range` 参数，表明读取数据的范围。该参数是一个二元tuple：(start, last)。这些接口会把它转换为Range头部的值，如：
    - byte_range 为 (0, 99) 转换为 'bytes=0-99'，表示读取前100个字节
    - byte_range 为 (None, 99) 转换为 'bytes=-99'，表示读取最后99个字节
    - byte_range 为 (100, None) 转换为 'bytes=100-'，表示读取第101个字节到文件结尾的部分（包含第101个字节）


分页罗列
-------
罗列各种资源的接口，如 :func:`list_buckets <Service.list_buckets>` 、 :func:`list_objects <Bucket.list_objects>` 都支持
分页查询。通过设定分页标记（如：`marker` 、 `key_marker` ）的方式可以指定查询某一页。首次调用将分页标记设为空（缺省值，可以不设），
后续的调用使用返回值中的 `next_marker` 、 `next_key_marker` 等。每次调用后检查返回值中的 `is_truncated` ，其值为 `False` 说明
已经到了最后一页。





.. _unix_time:

Unix Time
---------
COS Python SDK会把从服务器获得时间戳都转换为自1970年1月1日UTC零点以来的秒数，即Unix Time。
参见 `Unix Time <https://en.wikipedia.org/wiki/Unix_time>`_

COS中常用的时间格式有
    - HTTP Date格式，形如 `Sat, 05 Dec 2015 11:04:39 GMT` 这样的GMT时间。
      用在If-Modified-Since、Last-Modified这些HTTP请求、响应头里。
    - ISO8601格式，形如 `2015-12-05T00:00:00.000Z`。
      用在生命周期管理配置、列举Bucket结果中的创建时间、列举文件结果中的最后修改时间等处。

`http_date` 函数把Unix Time转换为HTTP Date；而 `http_to_unixtime` 则做相反的转换。如 ::

    >>> import cos2, time
    >>> unix_time = int(time.time())             # 当前UNIX Time，设其职为 1449313829
    >>> date_str = cos2.http_date(unix_time)     # 得到 'Sat, 05 Dec 2015 11:10:29 GMT'
    >>> cos2.http_to_unixtime(date_str)          # 得到 1449313829

.. note::

    生成HTTP协议所需的日期（即HTTP Date）时，请使用 `http_date` ， 不要使用 `strftime` 这样的函数。因为后者是和locale相关的。
    比如，`strftime` 结果中可能会出现中文，而这样的格式，COS服务器是不能识别的。

`iso8601_to_unixtime` 把ISO8601格式转换为Unix Time；`date_to_iso8601` 和 `iso8601_to_date` 则在ISO8601格式的字符串和
datetime.date之间相互转换。如 ::

    >>> import cos2
    >>> d = cos2.iso8601_to_date('2015-12-05T00:00:00.000Z')  # 得到 datetime.date(2015, 12, 5)
    >>> date_str = cos2.date_to_iso8601(d)                    # 得到 '2015-12-05T00:00:00.000Z'
    >>> cos2.iso8601_to_unixtime(date_str)                    # 得到 1449273600
"""

from . import http
from . import utils
from . import exceptions
from . import defaults
from . import json_utils

from .models import *
from .compat import urlquote, urlparse, to_unicode, to_string
from os.path import getsize

import time
import shutil
import cos2.utils
import os
from os.path import join


class _Base(object):
    def __init__(self, auth, endpoint, is_cname, session, connect_timeout,
                 app_name=''):
        self.auth = auth
        self.endpoint = _normalize_endpoint(endpoint.strip())
        self.session = session or http.Session()
        self.timeout = defaults.get(connect_timeout, defaults.connect_timeout)
        self.app_name = app_name

        self._make_url = _UrlMaker(self.endpoint, is_cname)

    def _do(self, method, bucket_name, key, **kwargs):
        key = to_string(key)
        req = http.Request(method, self._make_url(bucket_name, key),
                           app_name=self.app_name,
                           **kwargs)
        self.auth._sign_request(req, bucket_name, key)

        resp = self.session.do_request(req, timeout=self.timeout)

        if resp.status // 100 != 2:
            raise exceptions.make_exception(resp)

        return resp

    def _parse_result(self, resp, parse_func, klass):
        result = klass(resp)
        parse_func(result, resp.read())
        return result


class Service(_Base):
    """用于Service操作的类，如罗列用户所有的Bucket。

    用法 ::

        >>> import cos2
        >>> auth = cos2.Auth('your-access-key-id', 'your-access-key-secret')
        >>> service = cos2.Service(auth, 'cos2.chinac.com')
        >>> service.list_buckets()
        <cos2.models.ListBucketsResult object at 0x0299FAB0>

    :param auth: 包含了用户认证信息的Auth对象
    :type auth: cos2.Auth

    :param str endpoint: 访问域名，如杭州区域的域名为cos2.chinac.com

    :param session: 会话。如果是None表示新开会话，非None则复用传入的会话
    :type session: cos2.Session

    :param float connect_timeout: 连接超时时间，以秒为单位。
    :param str app_name: 应用名。该参数不为空，则在User Agent中加入其值。
        注意到，最终这个字符串是要作为HTTP Header的值传输的，所以必须要遵循HTTP标准。
    """
    def __init__(self, auth, endpoint,
                 session=None,
                 connect_timeout=None,
                 app_name=''):
        super(Service, self).__init__(auth, endpoint, False, session, connect_timeout,
                                      app_name=app_name)

    def list_buckets(self):
        """根据前缀罗列用户的Bucket。

        :param str prefix: 只罗列Bucket名为该前缀的Bucket，空串表示罗列所有的Bucket
        :param str marker: 分页标志。首次调用传空串，后续使用返回值中的next_marker
        :param int max_keys: 每次调用最多返回的Bucket数目

        :return: 罗列的结果
        :rtype: cos2.models.ListBucketsResult
        """
        resp = self._do('GET', '', '',
                        params={})
        return self._parse_result(resp, json_utils.parse_list_buckets, ListBucketsResult)


class Bucket(_Base):
    """用于Bucket和Object操作的类，诸如创建、删除Bucket，上传、下载Object等。

    用法（假设Bucket属于杭州区域） ::

        >>> import cos2
        >>> auth = cos2.Auth('your-access-key-id', 'your-access-key-secret')
        >>> bucket = cos2.Bucket(auth, 'http://cos2.chinac.com', 'your-bucket')
        >>> bucket.put_object('readme.txt', 'content of the object')
        <cos2.models.PutObjectResult object at 0x029B9930>

    :param auth: 包含了用户认证信息的Auth对象
    :type auth: cos2.Auth

    :param str endpoint: 访问域名或者CNAME
    :param str bucket_name: Bucket名
    :param bool is_cname: 如果endpoint是CNAME则设为True；反之，则为False。

    :param session: 会话。如果是None表示新开会话，非None则复用传入的会话
    :type session: cos2.Session

    :param float connect_timeout: 连接超时时间，以秒为单位。

    :param str app_name: 应用名。该参数不为空，则在User Agent中加入其值。
        注意到，最终这个字符串是要作为HTTP Header的值传输的，所以必须要遵循HTTP标准。
    """

    ACL = 'acl'
    CORS = 'cors'
    LIFECYCLE = 'lifecycle'
    LOCATION = 'location'
    LOGGING = 'logging'
    REFERER = 'referer'
    WEBSITE = 'website'

    def __init__(self, auth, endpoint, bucket_name,
                 is_cname=False,
                 session=None,
                 connect_timeout=None,
                 app_name=''):
        super(Bucket, self).__init__(auth, endpoint, is_cname, session, connect_timeout,
                                     app_name=app_name)
        self.bucket_name = bucket_name.strip()

    def sign_url(self, method, key, expires, headers=None, params=None):
        """生成签名URL。

        常见的用法是生成加签的URL以供授信用户下载，如为log.jpg生成一个5分钟后过期的下载链接::

            >>> bucket.sign_url('GET', 'log.jpg', 5 * 60)
            'http://your-bucket.cos2.chinac.com/logo.jpg?COSAccessKeyId=YourAccessKeyId\&Expires=1447178011&Signature=UJfeJgvcypWq6Q%2Bm3IJcSHbvSak%3D'

        :param method: HTTP方法，如'GET'、'PUT'、'DELETE'等
        :type method: str
        :param key: 文件名
        :param expires: 过期时间（单位：秒），链接在当前时间再过expires秒后过期

        :param headers: 需要签名的HTTP头部，如名称以x-cos-meta-开头的头部（作为用户自定义元数据）、
            Content-Type头部等。对于下载，不需要填。
        :type headers: 可以是dict，建议是cos2.CaseInsensitiveDict

        :param params: 需要签名的HTTP查询参数

        :return: 签名URL。
        """
        key = to_string(key)
        req = http.Request(method, self._make_url(self.bucket_name, key),
                           headers=headers,
                           params=params)
        return self.auth._sign_url(req, self.bucket_name, key, expires)

    def list_objects(self, prefix='', delimiter='', marker='', max_keys=100):
        """根据前缀罗列Bucket里的文件。

        :param str prefix: 只罗列文件名为该前缀的文件
        :param str delimiter: 分隔符。可以用来模拟目录
        :param str marker: 分页标志。首次调用传空串，后续使用返回值的next_marker
        :param int max_keys: 最多返回文件的个数，文件和目录的和不能超过该值

        :return: :class:`ListObjectsResult <cos2.models.ListObjectsResult>`
        """
        resp = self.__do_object('GET', '',
                                params={'prefix': prefix,
                                        'delimiter': delimiter,
                                        'marker': marker,
                                        'max-keys': str(max_keys)})
        return self._parse_result(resp, json_utils.parse_list_objects, ListObjectsResult)

    def put_object(self, key, data,
                   headers=None,):
        """上传一个普通文件。

        用法 ::
            >>> bucket.put_object('readme.txt', 'content of readme.txt')
            >>> with open(u'local_file.txt', 'rb') as f:
            >>>     bucket.put_object('remote_file.txt', f)

        :param key: 上传到COS的文件名

        :param data: 待上传的内容。
        :type data: bytes，str或file-like object

        :param headers: 用户指定的HTTP头部。可以指定Content-Type、Content-MD5、x-cos-meta-开头的头部等
        :type headers: 可以是dict，建议是cos2.CaseInsensitiveDict

        :return: :class:`PutObjectResult <cos2.models.PutObjectResult>`
        """
        headers = utils.set_content_type(http.CaseInsensitiveDict(headers), key)



        resp = self.__do_object('PUT', key, data=data, headers=headers)
        return PutObjectResult(resp)

    def put_object_from_file(self, key, filename,
                             headers=None):
        """上传一个本地文件到COS的普通文件。

        :param str key: 上传到COS的文件名
        :param str filename: 本地文件名，需要有可读权限

        :param headers: 用户指定的HTTP头部。可以指定Content-Type、Content-MD5、x-cos-meta-开头的头部等
        :type headers: 可以是dict，建议是cos2.CaseInsensitiveDict


        :return: :class:`PutObjectResult <cos2.models.PutObjectResult>`
        """
        headers = utils.set_content_type(http.CaseInsensitiveDict(headers), filename)

        with open(to_unicode(filename), 'rb') as f:
            return self.put_object(key, f, headers=headers)


    def get_object(self, key,
                   byte_range=None,
                   headers=None):
        """下载一个文件。

        用法 ::

            >>> result = bucket.get_object('readme.txt')
            >>> print(result.read())
            'hello world'

        :param key: 文件名
        :param byte_range: 指定下载范围。参见 :ref:`byte_range`

        :param headers: HTTP头部
        :type headers: 可以是dict，建议是cos2.CaseInsensitiveDict

        :return: file-like object

        :raises: 如果文件不存在，则抛出 :class:`NoSuchKey <cos2.exceptions.NoSuchKey>` ；还可能抛出其他异常
        """
        headers = http.CaseInsensitiveDict(headers)

        range_string = _make_range_string(byte_range)
        if range_string:
            headers['range'] = range_string

        resp = self.__do_object('GET', key, headers=headers)
        return GetObjectResult(resp)

    def get_object_to_file(self, key, filename,
                           byte_range=None,
                           headers=None):
        """下载一个文件到本地文件。

        :param key: 文件名
        :param filename: 本地文件名。要求父目录已经存在，且有写权限。
        :param byte_range: 指定下载范围。参见 :ref:`byte_range`

        :param headers: HTTP头部
        :type headers: 可以是dict，建议是cos2.CaseInsensitiveDict

        :return: 如果文件不存在，则抛出 :class:`NoSuchKey <cos2.exceptions.NoSuchKey>` ；还可能抛出其他异常
        """
        with open(to_unicode(filename), 'wb') as f:
            result = self.get_object(key, byte_range=byte_range, headers=headers)
            shutil.copyfileobj(result, f)
            #if(int(result.headers.get('content-length'))!=getsize(filename)):
            #    raise ClientError("Incomplete Consumed Body")
            return result

    def head_object(self, key, headers=None):
        """获取文件元信息。

        HTTP响应的头部包含了文件元信息，可以通过 `RequestResult` 的 `headers` 成员获得。
        用法 ::

            >>> result = bucket.head_object('readme.txt')
            >>> print(result.content_type)
            text/plain

        :param key: 文件名

        :param headers: HTTP头部
        :type headers: 可以是dict，建议是cos2.CaseInsensitiveDict

        :return: :class:`HeadObjectResult <cos2.models.HeadObjectResult>`

        :raises: 如果Bucket不存在或者Object不存在，则抛出 :class:`NotFound <cos2.exceptions.NotFound>`
        """
        resp = self.__do_object('HEAD', key, headers=headers)
        return HeadObjectResult(resp)

    def object_exists(self, key):
        """如果文件存在就返回True，否则返回False。如果Bucket不存在，或是发生其他错误，则抛出异常。"""

        # 如果我们用head_object来实现的话，由于HTTP HEAD请求没有响应体，只有响应头部，这样当发生404时，
        # 我们无法区分是NoSuchBucket还是NoSuchKey错误。
        #
        # 下面的实现是通过if-modified-since头部，把date设为当前时间24小时后，这样如果文件存在，则会返回
        # 304 (NotModified)；不存在，则会返回NoSuchKey
        date = cos2.utils.http_date(int(time.time()) + 24 * 60 * 60)

        try:
            self.get_object(key, headers={'if-modified-since': date})
        except exceptions.NotModified:
            return True
        except exceptions.NoSuchKey:
            return False
        else:
            raise exceptions.ClientError('Client time varies too much from server?')  # pragma: no cover

    def delete_object(self, key):
        """删除一个文件。

        :param str key: 文件名

        :return: :class:`RequestResult <cos2.models.RequestResult>`
        """
        resp = self.__do_object('DELETE', key)
        return RequestResult(resp)


    def batch_delete_objects(self, key_list):
        """批量删除文件。待删除文件列表不能为空。

        :param key_list: 文件名列表，不能为空。
        :type key_list: list of str

        :return: :class:`BatchDeleteObjectsResult <cos2.models.BatchDeleteObjectsResult>`
        """
        if not key_list:
            raise ClientError('key_list should not be empty')

        data = json_utils.to_batch_delete_objects_request(key_list, False)
        resp = self.__do_object('POST', '',
                                data=data,
                                params={'delete': ''},
                                headers={'Content-MD5': utils.md5_string(data)})
        return self._parse_result(resp, json_utils.parse_batch_delete_objects, BatchDeleteObjectsResult)

    def init_multipart_upload(self, key, headers=None):
        """初始化分片上传。

        返回值中的 `upload_id` 以及Bucket名和Object名三元组唯一对应了此次分片上传事件。

        :param str key: 待上传的文件名

        :param headers: HTTP头部
        :type headers: 可以是dict，建议是cos2.CaseInsensitiveDict

        :return: :class:`InitMultipartUploadResult <cos2.models.InitMultipartUploadResult>`
        """
        headers = utils.set_content_type(http.CaseInsensitiveDict(headers), key)

        resp = self.__do_object('POST', key, params={'uploads': ''}, headers=headers)
        return self._parse_result(resp, json_utils.parse_init_multipart_upload, InitMultipartUploadResult)

    def upload_part(self, key, upload_id, part_number, data):
        """上传一个分片。

        :param str key: 待上传文件名，这个文件名要和 :func:`init_multipart_upload` 的文件名一致。
        :param str upload_id: 分片上传ID
        :param int part_number: 分片号，最小值是1.
        :param data: 待上传数据。

        :return: :class:`PutObjectResult <cos2.models.PutObjectResult>`
        """

        resp = self.__do_object('PUT', key,
                                params={'uploadId': str(upload_id), 'partNumber': str(part_number)},
                                data=data)
        return PutObjectResult(resp)

    def complete_multipart_upload(self, key, upload_id, parts, headers=None):
        """完成分片上传，创建文件。

        :param str key: 待上传的文件名，这个文件名要和 :func:`init_multipart_upload` 的文件名一致。
        :param str upload_id: 分片上传ID

        :param parts: PartInfo列表。PartInfo中的part_number和etag是必填项。其中的etag可以从 :func:`upload_part` 的返回值中得到。
        :type parts: list of `PartInfo <cos2.models.PartInfo>`

        :param headers: HTTP头部
        :type headers: 可以是dict，建议是cos2.CaseInsensitiveDict

        :return: :class:`PutObjectResult <cos2.models.PutObjectResult>`
        """

        data = json_utils.to_complete_upload_request(sorted(parts, key=lambda p: p.part_number))
        resp = self.__do_object('POST', key,
                                params={'uploadId': str(upload_id)},
                                data=data,
                                headers=headers)
        return PutObjectResult(resp)

    def abort_multipart_upload(self, key, upload_id):
        """取消分片上传。

        :param str key: 待上传的文件名，这个文件名要和 :func:`init_multipart_upload` 的文件名一致。
        :param str upload_id: 分片上传ID

        :return: :class:`RequestResult <cos2.models.RequestResult>`
        """
        resp = self.__do_object('DELETE', key,
                                params={'uploadId': str(upload_id)})
        return RequestResult(resp)

    def list_multipart_uploads(self,
                               upload_id_marker='',
                               max_uploads=1000):
        """罗列正在进行中的分片上传。支持分页。

        :param str prefix: 只罗列匹配该前缀的文件的分片上传
        :param str delimiter: 目录分割符
        :param str key_marker: 文件名分页符。第一次调用可以不传，后续设为返回值中的 `next_key_marker`
        :param str upload_id_marker: 分片ID分页符。第一次调用可以不传，后续设为返回值中的 `next_upload_id_marker`
        :param int max_uploads: 一次罗列最多能够返回的条目数

        :return: :class:`ListMultipartUploadsResult <cos2.models.ListMultipartUploadsResult>`
        """
        resp = self.__do_object('GET', '',
                                params={'uploads': '',
                                        'upload-id-marker': upload_id_marker,
                                        'max-uploads': str(max_uploads)})
        return self._parse_result(resp, json_utils.parse_list_multipart_uploads, ListMultipartUploadsResult)

    def list_parts(self, key, upload_id,
                   marker='', max_parts=1000):
        """列举已经上传的分片。支持分页。

        :param str key: 文件名
        :param str upload_id: 分片上传ID
        :param str marker: 分页符
        :param int max_parts: 一次最多罗列多少分片

        :return: :class:`ListPartsResult <cos2.models.ListPartsResult>`
        """
        resp = self.__do_object('GET', key,
                                params={'uploadId': str(upload_id),
                                        'part-number-marker': marker,
                                        'max-parts': str(max_parts)})
        return self._parse_result(resp, json_utils.parse_list_parts, ListPartsResult)

    def create_bucket(self, permission=None):
        """创建新的Bucket。


        :param str permission: 指定Bucket的ACL。可以是cos2.BUCKET_ACL_PRIVATE（推荐、缺省）、cos2.BUCKET_ACL_PUBLIC_READ
        """

        if permission:
            headers = {'x-cos-acl': permission}
        else:
            headers = None
        resp = self.__do_bucket('PUT', headers=headers)
        return RequestResult(resp)

    def delete_bucket(self):
        """删除一个Bucket。只有没有任何文件，也没有任何未完成的分片上传的Bucket才能被删除。

        :return: :class:`RequestResult <cos2.models.RequestResult>`

        ":raises: 如果试图删除一个非空Bucket，则抛出 :class:`BucketNotEmpty <cos2.exceptions.BucketNotEmpty>`
        """
        resp = self.__do_bucket('DELETE')
        return RequestResult(resp)

    def put_bucket_acl(self, permission):
        """设置Bucket的ACL。

        :param str permission: 新的ACL，可以是cos2.BUCKET_ACL_PRIVATE、cos2.BUCKET_ACL_PUBLIC_READ或
            cos2.BUCKET_ACL_PUBLIC_READ_WRITE
        """
        resp = self.__do_bucket('PUT', headers={'x-cos-acl': permission}, params={Bucket.ACL: ''})
        return RequestResult(resp)

    def get_bucket_acl(self):
        """获取Bucket的ACL。

        :return: :class:`GetBucketAclResult <cos2.models.GetBucketAclResult>`
        """
        resp = self.__do_bucket('GET', params={Bucket.ACL: ''})
        return self._parse_result(resp, json_utils.parse_get_bucket_acl, GetBucketAclResult)


    def get_bucket_location(self):
        """获取Bucket的数据中心。

        :return: :class:`GetBucketLocationResult <cos2.models.GetBucketLocationResult>`
        """
        resp = self.__do_bucket('GET', params={Bucket.LOCATION: ''})
        return self._parse_result(resp, json_utils.parse_get_bucket_location, GetBucketLocationResult)


    def put_bucket_website(self, input):
        """为Bucket配置静态网站托管功能。

        :param input: :class:`BucketWebsite <cos2.models.BucketWebsite>`
        """
        # data = self.__convert_data(BucketWebsite, xml_utils.to_put_bucket_website, input)
        data = self.__convert_data(BucketWebsite,json_utils.to_put_bucket_website,input)
        resp = self.__do_bucket('PUT', data=data, params={Bucket.WEBSITE: ''})
        return RequestResult(resp)

    def get_bucket_website(self):
        """获取Bucket的静态网站托管配置。

        :return: :class:`GetBucketWebsiteResult <cos2.models.GetBucketWebsiteResult>`

        :raises: 如果没有设置静态网站托管，那么就抛出 :class:`NoSuchWebsite <cos2.exceptions.NoSuchWebsite>`
        """
        resp = self.__do_bucket('GET', params={Bucket.WEBSITE: ''})
        return self._parse_result(resp, json_utils.parse_get_bucket_websiste, GetBucketWebsiteResult)

    def delete_bucket_website(self):
        """关闭Bucket的静态网站托管功能。"""
        resp = self.__do_bucket('DELETE', params={Bucket.WEBSITE: ''})
        return RequestResult(resp)

    def _get_bucket_config(self, config):
        """获得Bucket某项配置，具体哪种配置由 `config` 指定。该接口直接返回 `RequestResult` 对象。
        通过read()接口可以获得XML字符串。不建议使用。

        :param str config: 可以是 `Bucket.ACL` 、 `Bucket.LOGGING` 等。

        :return: :class:`RequestResult <cos2.models.RequestResult>`
        """
        return self.__do_bucket('GET', params={config: ''})

    def __do_object(self, method, key, **kwargs):
        return self._do(method, self.bucket_name, key, **kwargs)

    def __do_bucket(self, method, **kwargs):
        return self._do(method, self.bucket_name, '', **kwargs)

    def __convert_data(self, klass, converter, data):
        if isinstance(data, klass):

            return converter(data)
        else:

            return data


def _normalize_endpoint(endpoint):
    if not endpoint.startswith('http://') and not endpoint.startswith('https://'):
        return 'http://' + endpoint
    else:
        return endpoint


_ENDPOINT_TYPE_CHINAC = 0
_ENDPOINT_TYPE_CNAME = 1
_ENDPOINT_TYPE_IP = 2


def _make_range_string(range):
    if range is None:
        return ''

    start = range[0]
    last = range[1]

    if start is None and last is None:
        return ''

    return 'bytes=' + _range(start, last)


def _range(start, last):
    def to_str(pos):
        if pos is None:
            return ''
        else:
            return str(pos)

    return to_str(start) + '-' + to_str(last)


def _determine_endpoint_type(netloc, is_cname, bucket_name):
    if utils.is_ip_or_localhost(netloc):
        return _ENDPOINT_TYPE_IP

    if is_cname:
        return _ENDPOINT_TYPE_CNAME

    if utils.is_valid_bucket_name(bucket_name):
        return _ENDPOINT_TYPE_CHINAC
    else:
        return _ENDPOINT_TYPE_IP


class _UrlMaker(object):
    def __init__(self, endpoint, is_cname):
        p = urlparse(endpoint)

        self.scheme = p.scheme
        self.netloc = p.netloc
        self.is_cname = is_cname

    def __call__(self, bucket_name, key):
        self.type = _determine_endpoint_type(self.netloc, self.is_cname, bucket_name)

        key = urlquote(key, '/')

        if self.type == _ENDPOINT_TYPE_CNAME:
            return '{0}://{1}/{2}'.format(self.scheme, self.netloc, key)

        if self.type == _ENDPOINT_TYPE_IP:
            if bucket_name:
                return '{0}://{1}/{2}/{3}'.format(self.scheme, self.netloc, bucket_name, key)
            else:
                return '{0}://{1}/{2}'.format(self.scheme, self.netloc, key)

        if not bucket_name:
            assert not key
            return '{0}://{1}'.format(self.scheme, self.netloc)

        return '{0}://{1}.{2}/{3}'.format(self.scheme, bucket_name, self.netloc, key)
