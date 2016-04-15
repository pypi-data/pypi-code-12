# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/20.
import re
import jieba


def search(pattern, txt):
    """txt中搜索pattern"""
    _pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    _match = re.search(_pattern, txt)
    if _match:
        return _match.group(1)


def replace(pattern, repl, txt):
    _pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    return re.sub(_pattern, repl, txt)


def match_encoding(html):
    """从文本中获取charset编码"""
    pattern_str = u"text/html;\s*charset=([a-z\d-]{2,10})"
    group = search(pattern_str, html)
    if group is None:
        pattern_str = u'charset="([a-z\d-]{2,10})"'
        group = search(pattern_str, html)
    return group


def find_all(pattern, source):
    """正则查找匹配组集合"""
    p = re.compile(pattern, re.M | re.I)
    m = re.findall(p, source)
    return m


def match(pattern, source, index):
    """查找匹配字符串返回group(1)值"""
    p = re.compile(pattern, re.M)
    _match = p.search(source)
    if _match:
        return _match.group(index)

def search_cookie(html):
    if 'cookie' in html:
        cookie = re.search(re.compile('cookie=[\'"](.+?)[\'"]', re.I | re.M), html)
        if cookie:
            return cookie.group(1)


def zh_cn(html):
    if not isinstance(html, unicode):
        html = unicode(html)
    pattern = u"[^\u4e00-\u9fa5]+"
    pattern = re.compile(pattern, re.I | re.M)
    result = re.sub(pattern, '', html)
    seg_list = jieba.cut(result)
    b = [s for s in seg_list]
    a = set(b)
    return "".join(a)

def gb(html):

    if not isinstance(html, unicode):
        html = unicode(html)
    pattern = u"[^\u4e00-\u9fa5]+"
    pattern = re.compile(pattern, re.I | re.M)
    result = re.sub(pattern, '', html)
    return result

def remove_all_tags(html):
    pattern = u"<[^>]*?>"
    pattern = re.compile(pattern, re.I | re.M)
    result = re.sub(pattern, '', html)
    return result

def remove_all_blank(html):
    pattern = u"\s*"
    pattern = re.compile(pattern, re.I | re.M)
    result = re.sub(pattern, '', html)
    return result