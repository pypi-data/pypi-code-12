# -*- coding: utf-8 -*-

"""
cos2.utils
----------

工具函数模块。
"""

from email.utils import formatdate

import os.path
import mimetypes
import socket
import hashlib
import base64
import threading
import calendar
import datetime
import time
import errno
from . import defaults

from .compat import to_string, to_bytes
from .exceptions import ClientError

_MAX_PART_COUNT = 10000
_MIN_PART_SIZE = 100 * 1024


_EXTRA_TYPES_MAP = {
    ".js": "application/javascript",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xltx": "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
    ".potx": "application/vnd.openxmlformats-officedocument.presentationml.template",
    ".ppsx": "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".sldx": "application/vnd.openxmlformats-officedocument.presentationml.slide",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".dotx": "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
    ".xlam": "application/vnd.ms-excel.addin.macroEnabled.12",
    ".xlsb": "application/vnd.ms-excel.sheet.binary.macroEnabled.12",
    ".apk": "application/vnd.android.package-archive"
}


def b64encode_as_string(data):
    return to_string(base64.b64encode(data))


def content_md5(data):
    """计算data的MD5值，经过Base64编码并返回str类型。

    返回值可以直接作为HTTP Content-Type头部的值
    """
    m = hashlib.md5(to_bytes(data))

    return b64encode_as_string(m.digest())


def md5_string(data):
    """返回 `data` 的MD5值，以十六进制可读字符串（32个小写字符）的方式。"""
    return hashlib.md5(to_bytes(data)).hexdigest()


def content_type_by_name(name):
    """根据文件名，返回Content-Type。"""
    ext = os.path.splitext(name)[1].lower()
    if ext in _EXTRA_TYPES_MAP:
        return _EXTRA_TYPES_MAP[ext]

    return mimetypes.guess_type(name)[0]


def set_content_type(headers, name):
    """根据文件名在headers里设置Content-Type。如果headers中已经存在Content-Type，则直接返回。"""
    headers = headers or {}

    if 'Content-Type' in headers:
        return headers

    content_type = content_type_by_name(name)
    if content_type:
        headers['Content-Type'] = content_type

    return headers


def is_ip_or_localhost(netloc):
    """判断网络地址是否为IP或localhost。"""
    loc = netloc.split(':')[0]
    if loc == 'localhost':
        return True

    try:
        socket.inet_aton(loc)
    except socket.error:
        return False

    return True


_ALPHA_NUM = 'abcdefghijklmnopqrstuvwxyz0123456789'
_HYPHEN = '-'
_BUCKET_NAME_CHARS = set(_ALPHA_NUM + _HYPHEN)


def is_valid_bucket_name(name):
    """判断是否为合法的Bucket名"""
    if len(name) < 3 or len(name) > 63:
        return False

    if name[-1] == _HYPHEN:
        return False

    if name[0] not in _ALPHA_NUM:
        return False

    return set(name) <= _BUCKET_NAME_CHARS


class SizedFileAdapter(object):
    """通过这个适配器（Adapter），可以把原先的 `file_object` 的长度限制到等于 `size`。"""
    def __init__(self, file_object, size):
        self.file_object = file_object
        self.size = size
        self.offset = 0

    def read(self, amt=None):
        if self.offset >= self.size:
            return ''

        if (amt is None or amt < 0) or (amt + self.offset >= self.size):
            data = self.file_object.read(self.size - self.offset)
            self.offset = self.size
            return data

        self.offset += amt
        return self.file_object.read(amt)

    def __len__(self):
        return self.size


def how_many(m, n):
    return (m + n - 1) // n


def file_object_remaining_bytes(fileobj):
    current = fileobj.tell()

    fileobj.seek(0, os.SEEK_END)
    end = fileobj.tell()
    fileobj.seek(current, os.SEEK_SET)

    return end - current


def _get_data_size(data):
    if hasattr(data, '__len__'):
        return len(data)

    if hasattr(data, 'seek') and hasattr(data, 'tell'):
        return file_object_remaining_bytes(data)

    return None


_CHUNK_SIZE = 8 * 1024



_STRPTIME_LOCK = threading.Lock()

_GMT_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
_ISO8601_FORMAT = "%Y-%m-%dT%H:%M:%S"


def to_unixtime(time_string, format_string):
    with _STRPTIME_LOCK:
        return int(calendar.timegm(time.strptime(time_string, format_string)))


def http_date(timeval=None):
    """返回符合HTTP标准的GMT时间字符串，用strftime的格式表示就是"%a, %d %b %Y %H:%M:%S GMT"。
    但不能使用strftime，因为strftime的结果是和locale相关的。
    """
    return formatdate(timeval, usegmt=True)


def http_to_unixtime(time_string):
    """把HTTP Date格式的字符串转换为UNIX时间（自1970年1月1日UTC零点的秒数）。

    HTTP Date形如 `Sat, 05 Dec 2015 11:10:29 GMT` 。
    """
    return to_unixtime(time_string, _GMT_FORMAT)


def iso8601_to_unixtime(time):
    """把ISO8601时间字符串（形如，2012-02-24T06:07:48.000Z）转换为UNIX时间，精确到秒。"""
    time_string =time[:-6]
    return to_unixtime(time_string, _ISO8601_FORMAT)


def date_to_iso8601(d):
    return d.strftime(_ISO8601_FORMAT)  # It's OK to use strftime, since _ISO8601_FORMAT is not locale dependent


def iso8601_to_date(time_string):
    timestamp = iso8601_to_unixtime(time_string)
    return datetime.date.fromtimestamp(timestamp)


def makedir_p(dirpath):
    try:
        os.makedirs(dirpath)
    except os.error as e:
        if e.errno != errno.EEXIST:
            raise

def determine_part_size(total_size,
                        preferred_size=None):
    """确定分片大小。

    :param int total_size: 总共需要上传的长度
    :param int preferred_size: 用户期望的分片大小。如果不指定则采用defaults.part_size

    :return: 分片大小
    """
    if not preferred_size:
        preferred_size = defaults.part_size

    if total_size < preferred_size:
        return total_size

    if preferred_size * _MAX_PART_COUNT < total_size:
        if total_size % _MAX_PART_COUNT:
            return total_size // _MAX_PART_COUNT + 1
        else:
            return total_size // _MAX_PART_COUNT
    else:
        return preferred_size

class SizedFileAdapter(object):
    """通过这个适配器（Adapter），可以把原先的 `file_object` 的长度限制到等于 `size`。"""
    def __init__(self, file_object, size):
        self.file_object = file_object
        self.size = size
        self.offset = 0

    def read(self, amt=None):
        if self.offset >= self.size:
            return ''

        if (amt is None or amt < 0) or (amt + self.offset >= self.size):
            data = self.file_object.read(self.size - self.offset)
            self.offset = self.size
            return data

        self.offset += amt
        return self.file_object.read(amt)

    def __len__(self):
        return self.size