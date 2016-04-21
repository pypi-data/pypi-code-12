# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/26.
import re
from gelid.extractors import regex
import time


def get_author(txt):
    """查找作者，以作者|记者开头的文本即为作者"""
    tag = u"(作者|记者)"
    author = get_string_some(txt, tag, 3)
    if not author:
        author = get_string_mix(txt, tag)
    return author


def scan(txt, tag):
    """查找"""
    return get_string_mix(txt, u'({0})'.format(tag))


def get_editor(txt):
    """查找编辑"""
    tag = u"(编辑|责编)"
    return get_string_mix(txt, tag)


def get_from(txt):
    """查找来源"""
    tag = u"(来源|来自|出自|摘自|出处)"
    return get_string_mix(txt, tag)


def get_share_count(txt):
    """查找推荐|分享"""
    tag = u"(推荐|分享)"
    return get_search_mix(txt, tag, u"\d+")


def get_comment_count(txt):
    """查找推荐|分享"""
    tag = u"(回贴数?|回复数?|跟贴数?)"
    comment = get_search_mix(txt, tag, u"\d+")
    if not comment:
        tag = u"(人回贴|人回复|人跟贴)"
        comment = get_search_last(txt, tag, u"\d+")
    return comment


def get_string_some(txt, tag, max_len):
    """找多匹配字符串"""
    pn = u'\s*[:：/]\s*(([^\s]{2,' + str(max_len) + u'} )*)'
    txt = get_match_group(txt, tag, pn, 2)
    if txt:
        clear = u"[/，,、|｜:：]"
        txt = regex.replace(clear, " ", txt)
        some = re.split(' ', txt)
        txt = ""
        for s in some:
            slen = len(s)
            if slen > max_len:
                break
            elif slen > 0:
                txt = txt + " " + s
        if len(txt) > 0:
            txt = txt[1:]
        if len(txt) > 2:
            return txt


def get_string_first(txt, tag):
    """优先查找匹配字符串"""
    return get_search_first(txt, tag, u".*?")


def get_string_second(txt, tag):
    """普通查找匹配字符串"""
    return get_search_second(txt, tag, u".*?")


def get_string_mix(txt, tag):
    """混合查找匹配字符串，先优先，后普通"""
    mix = get_string_first(txt, tag)
    if not mix:
        mix = get_string_second(txt, tag)
    return mix


def get_search_first(txt, tag, search):
    """优先查找匹配字符串"""
    pn = u'\s*[:：/]\s*(' + search + u')\s'
    return get_match_group(txt, tag, pn, 2)


def get_search_second(txt, tag, search):
    """普通查找匹配字符串"""
    pn = u'\s*[:：\s]+(' + search + u')\s'
    return get_match_group(txt, tag, pn, 2)


def get_search_last(txt, tag, search):
    """普通查找匹配字符串"""
    pn = u'(' + search + ')\s*'
    return get_match_group_last(txt, tag, pn, 1)


def get_search_mix(txt, tag, search):
    """混合查找匹配字符串，先优先，后普通"""
    mix = get_search_first(txt, tag, search)
    if not mix:
        mix = get_search_second(txt, tag, search)
    return mix


def get_match_group(txt, tag, pn, index):
    """查找匹配字符串返回group(1)值"""
    pattern = tag + pn
    return get_match_base(txt, pattern, index)


def get_match_group_last(txt, tag, pn, index):
    """查找匹配字符串返回group(1)值"""
    pattern = pn + tag
    return get_match_base(txt, pattern, index)


def get_match_base(txt, pattern, index):
    """查找匹配字符串返回group(1)值"""
    return regex.match(pattern, txt, index)

def get_time(txt):
    time_format = u"\
(\d{4})[年\-/ ]{1,2}\
(\d{1,2})[月\-/ ]{1,2}\
(\d{1,2})[日\-/ ]{0,2}\
((\d{1,2})[时点:\-/ ]{1,2})?\
((\d{1,2})[分:\-/ ]{1,2})?\
((\d{1,2})[秒:\-/ ]{0,2})?\
"
    pattern = re.compile(time_format)
    match = pattern.search(txt)
    # 提取时间内容
    if match:
        group = match.groups()
        time_list = list()
        # 提取时间数字生成数组
        index = 0
        for data in group:
            if index in (0, 1, 2, 4, 6, 8):
                if data:
                    time_list.append(int(data))
                else:
                    time_list.append(0)
            index += 1

        str_time = ''
        for data in time_list:
            str_time = u"%s:%s" % (str_time, data)

        str_time = str_time[1:]
        # 生成时间
        try:
            tx = time.strptime(str_time, u'%Y:%m:%d:%H:%M:%S')
        except:
            tx = None
        return tx