# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/26.
import re
import jieba

from gelid.extractors import regex
from gelid.extractors import html
from gelid.extractors import score

from gelid import settings
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def readability_content(source, only_content=True):
    """
    使用readability获取内容，需要安装 readability-lxml
    :param source:
    :param only_content:
    :return:
    """

    try:
        from readability.readability import Document

        doc = Document(source)
        if source and re.search(re.compile('<html', re.I | re.M), source):
            readable_article = doc.summary(html_partial=True)
            if readable_article and only_content:
                readable_article = regex.replace(u'<h1>.*?</h1>', '', readable_article)

            for item in settings.NOT_EXIST:
                find = readable_article.find(item)
                if find>100:
                    readable_article = readable_article[0:find]

            readable_article = readable_article.replace(u'&#13;','')
            return readable_article
    except:
        return ''


def distance_content(source, clear=False, article=False, duplicate=False):
    """
    根据行距离及距离中心距离实现主内容计算
    :param source:
    :return:
    """
    if not clear:
        source = html.set_html_clean(source)
    if not article:
        article_content = html.inner_text('article', source)
        if article_content:
            source = article_content

    pattern = u'<div[^>]*>\s*</div>'
    body = regex.replace(pattern, '', source)

    # 过滤所有正文可能使用的标签
    tags = u'(?P<tag>(/?(p|strong|img|font|span|br|h\d|a|b|i|u|pre|center))[\w\W]*?)'

    def holder_tags(content, tag):
        """
        变化指定标签
        :param content:
        :param tag:
        :return:
        """
        pattern = u'<{0}>'.format(tag)
        content = regex.replace(pattern, u'##\g<tag>##', content)
        # content = regex.replace('<{0}>([\w\W]*?>(</\\1>)?'.format(tag), r'##\g<tag>\g<2>\g<tag>##', content)
        # 转换\n为特殊符号┠
        return regex.replace(u'\n', u'┠', content)

    def clear_tags(content, tag):
        """
        清除转化标签
        :param content:
        :param tag:
        :return:
        """
        _pattern = re.compile(u'(##a [\w\W]*?##/a##)|(##{0}##)'.format(tag) + u'|(┠)', re.I)
        content = re.sub(_pattern, r"", content)
        tag = u'[^\u4e00-\u9fa5\ufe30-\uffa0]'
        return regex.replace(tag, u"", content)

    def recover(content, tag):
        """
        还原转化标签
        :param content:
        :param tag:
        :return:
        """
        _pattern = re.compile(u'##{0}##'.format(tag), re.I)
        return re.sub(_pattern, u'<\g<tag>>', content)

    body = holder_tags(body, tags)
    # 其它html标签转换行
    body = regex.replace(u'(</?.*?>)', u'\n', body)
    # 分割内容至数据
    lines = re.split(u'\n', body)

    # 清除保留的标签，以备文字计数
    z = [clear_tags(i, tags) for i in lines]

    def duplicate_line(line):
        tokens = jieba.cut(line)
        tokens = [token for token in tokens]
        tokens = set(tokens)
        line = ''.join(tokens)
        return line

    # 内容分词处理，清除重复词后再计算文字
    if duplicate:
        z = map(duplicate_line, z)

    # 计算行内数据长
    x = [len(i) for i in z]
    max_x = max(x)
    max_t = 0
    body = lines[x.index(max_x)]


    index = 0
    if max_x > 100 and index == 0:
        index = max_x
    # 如果字数少于100字，则根据距离中心点重新计算
    new_body = None
    if max_x < settings.MAX_WORD_RESEARCH:
        # lines.remove(lines[index])
        mid = len(x) / 2
        if index > 0:
            mid = index
        t = []
        i = 0
        for count in x:
            abs_distance = abs(mid - i)
            nx = count * mid / ((abs_distance + mid) + 1)
            t.append(nx)
            i += 1
        max_t = max(t)
        new_body = lines[t.index(max_t)]

    if new_body:
        for w in settings.NOT_EXIST:
            if w in new_body:
                new_body = None
                break
    if new_body:
        body = new_body
        max_x = max_t
    body = recover(body, tags)
    # 替换原始┠为\n
    body = re.sub(u'┠', u'\n', body)
    # 所有标签改小写
    # body = re.sub(r'<.*?>', lambda a: a.group().lower(), body)
    return body

def zh_CN():
    pass

def rank_content(source, clear=False, duplicate=True):
    return rank_content_with_count(source,clear,duplicate)[0]

def rank_content_with_count(source, clear=False, duplicate=True):

    readability_rank_content = readability_content(source)
    readability_rank = score.Score(dict(content=readability_rank_content))
    distance_rank_content = distance_content(source, clear=clear, duplicate=duplicate)
    distance_rank = score.Score(dict(content=distance_rank_content))

    if distance_rank.rank + 5 > readability_rank.rank:
        return distance_rank.article['content'], len(distance_rank.zh_text)
    else:
        return readability_rank.article['content'], len(distance_rank.zh_text)

