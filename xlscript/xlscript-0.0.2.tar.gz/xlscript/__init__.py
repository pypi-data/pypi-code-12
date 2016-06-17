import os
import re
import json
from urllib.request import urlopen, Request
from urllib.parse import quote, unquote, urlencode
import mimetypes


def get_content_type(file_path=None):
    if not file_path or not os.path.isfile(file_path):
        return 'application/octet-stream'
    return mimetypes.guess_type(file_path)[0] or 'application/octet-stream'


def encode_multipart_formdata(fields, files=()):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filepath) elements for data to be uploaded as
    files
    :param fields: The fields to encode.
    :param files: The file-type field set.
    :return: (content_type, body) ready for httplib.HTTP instance
    """
    boundary = '----xlsapi-boundary'
    lines = []

    for (key, value) in fields:
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="%s"' % key)
        lines.append('')
        lines.append(value)

    for (key, file) in files:
        lines.append('--' + boundary)
        lines.append(
            'Content-Disposition: form-data; name="%s"; filename=%s' %
            (key, os.path.basename(file))
        )
        if isinstance(file, bytes):
            lines.append('Content-Type: %s' % get_content_type(file))
            lines.append('')
            lines.append(file)
        elif isinstance(file, str):
            lines.append('Content-Type: %s' % get_content_type(file))
            lines.append('')
            lines.append(open(file, 'rb').read())
        elif hasattr(file, 'read'):
            lines.append('Content-Type: %s' % get_content_type(file))
            lines.append('')
            lines.append(file.read())
        else:
            raise AttributeError('The multipart encoding files content is bad.')

    lines.append('--' + boundary + '--')

    body = b'\r\n'.join([l.encode() if type(l) == str else l for l in lines])

    content_type = 'multipart/form-data; boundary=%s' % boundary

    return content_type, body


def render_xlscript(xlscript='',
                    template=(),
                    api_url='http://xlsapi.easecloud.cn',
                    config=None,
                    django_response=False):
    """发送请求处理一个 xlscript 渲染
    返回一个 http.client.HTTPResponse 对象，该响应对应于一个 excel 文件的下载响应。
    :param xlscript: 提交的 xlscript 脚本文本
    :param template: (可选) excel 模板的路径
    :param config: (可选) 配置项参数
    :param api_url: phpexcel-api 的服务 url
    :param django_response: 返回 djang.http.HttpResponse 对象而不是
        http.client.HTTPResponse 对象
    :returns: http.client.HTTPResponse object
    """
    content_type, body = encode_multipart_formdata(
        fields={
            'xlscript': xlscript,
            'config': json.dumps(config or {}),
        }.items(),
        files=template and [('template', template)],
    )

    request = Request(
        api_url,
        data=body,
        headers={'Content-Type': content_type}
    )
    response = urlopen(request)

    if django_response:
        from django.http import HttpResponse
        _response = HttpResponse(response.read())
        _response._headers = dict(response.headers)
        response = _response

    return response

# def render_excel(xlscript='',
#                  template=(),
#                  api_url='http://xlsapi.easecloud.cn',
#                  config=None):
#     """请求一个 xlscript 渲染，返回文件名，文件二进制内容，以及 mime 类型
#     :param xlscript: 渲染的 xlscript 脚本
#     :param template:
#     :param api_url: phpexcel-api 的服务 url
#     :return: (file_name, bytes, mime_type)
#     """
#     response = render_excel_response(xlscript, template, api_url, config)
#     assert response.status == 200, '接口调用失败，返回状态码：' + response.status
#     headers = dict(response.getheaders())
#     # print(headers)
#     # print(response.read().decode())
#     return (
#         unquote(
#             re.findall('filename="(.+)"', headers['Content-Disposition'])[0]),
#         response.read(),
#         headers.get('Content-Type'),
#     )
#
#
# def render_xlscript(xlscript):
#     fname, data, mime = render_excel(
#         xlscript,
#         config={'row_delimiter': '$$$', 'col_delimiter': '|'},
#     )
#     resp = HttpResponse(data, content_type=mime)
#     resp['Content-Disposition'] = 'attachment; ' + urlencode(
#         {'filename': fname})
#     return resp
