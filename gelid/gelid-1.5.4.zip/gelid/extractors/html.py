# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/19.
import re
from urlparse import urlparse, urljoin

import six

from gelid import settings
from gelid.extractors import regex


def inner_text(tag, source):
    """返回标签内内容"""
    if tag and source:
        pattern = re.compile(u'<{0}.*?>([\w\W]*?)</{0}>'.format(tag), re.I | re.M)
        search = re.search(pattern, source)
        if search:
            return search.group(1)


def urls(url):
    """
    返回urls字典
    """
    assert url, u'url不能为空'
    parse = urlparse(url)
    question_index = url.find(u'?')
    url_host = parse.hostname
    url_without_question = url if question_index == -1 else url[0:question_index]
    url_root = url_without_question[0:url_without_question.rfind('/') + 1]
    url_filename = url_without_question[url_without_question.rfind('/') + 1:]
    path_index = url_filename.find('.')
    fileid = url_filename if path_index == -1 else url_filename[0:path_index]
    pattern = re.compile(r"^(.+)[\-_]\d{1,2}$", re.I)
    match = re.search(pattern, fileid)
    if match:
        fileid = match.group(1)
    _urls = {"dir": url_root, "filename": url_filename, "fileid": fileid, 'domain': url_host}
    return _urls


def next_page(url, source, token=u'下一页|下页|&gt;|》|next|翻页|next page'):
    u"""自动分析下一页地址：
    假设分页都是类似的，均与当前URL有一定的规则关联，仅为分页码不一样或有无
    正则获取下一页地址，如果为找到分页，且分页地址符合规则，则为分页
    """
    if not url or not re.match(r'http.+', url):
        raise ValueError(u'url格式错误!')
    _urls = urls(url)
    fileid = _urls["fileid"]
    pattern = u'href=.*?' + fileid + u'[\w\W]{1,200}?</a>'
    m = regex.find_all(pattern, source)
    page_url = None
    if m:
        for mc in m:
            if re.search(token, mc):
                pattern = u'href=\s*[\'"]([^\'"]*?' + fileid + u'[/\-\._][^\'" ]*?)[\'"]'
                mx = re.search(pattern, mc)
                if mx:
                    page_url = mx.group(1)
                    break
                else:
                    pattern = u'href=\s*([^\'"]*?' + fileid + u'[/\-\._][^\'"\s>]*)'
                    mx = re.search(pattern, mc)
                    if mx:
                        page_url = mx.group(1)
                        break

    if page_url:
        page_url = urljoin(url, page_url)
    return page_url


def clear_tags_with_content(tags, content):
    """清除标签组及中间的内容"""
    if isinstance(tags, six.string_types):
        tags = [tags]
    content = reduce(lambda x, y: clear_tag_with_content(y, x), tags, content)
    return content


def clear_tag_with_content(tag, content):
    """清除标签及中间的内容"""
    pattern = u'<({0})[^>]*?>[\w\W]*?</\\1>'.format(tag)
    return regex.replace(pattern, '', content)


def clear_tags(tags, content):
    """清除标签组"""
    if isinstance(tags, six.string_types):
        tags = [tags]
    content = reduce(lambda x, y: clear_tag(y, x), tags, content)
    return content


def clear_tag(tag, content):
    """清除标签"""
    pattern = u'</?{0}.*?>'.format(tag)
    return regex.replace(pattern, '', content)


def txt(content):
    """生成txt，并返回txt"""
    pattern = u'<[^>]*>|\r|\n|\t'
    content = regex.replace(pattern, '', content)
    pattern = u"&nbsp;"
    content = regex.replace(pattern, ' ', content)
    pattern = u"&[\w\d]{2,8}?;"
    content = regex.replace(pattern, '', content)
    return content


def clear_comment(content):
    """清除注释"""
    pattern = u'<!\-[\w\W]+?\->'
    return regex.replace(pattern, '', content)


def set_html_clean(content):
    """生成html无用标签清洗后的内容"""
    tags = [u'script', u'style', u'head', u'noscript']

    content = clear_comment(content)
    content = clear_tags_with_content(tags, content)
    content = clear_small_pic(content)
    return content


def http_join(url, content, tags=u'a|img', attrs=u'src|href', protocol=u'http|ftp'):
    """
    将内容中指定位置的url转为http开头的绝对路径
    根据items指定的参数，结合html结构抽取分别属性由双引号，单引号，后空格等形式的链接保存至字典
    遍历字典替换文本中的url为http url
    """
    pattern = u"(<({0}) [^>]*?({1})[\s=]*[\"']?([^>'\" ]*)[\"' ][^>]*?>)".format(tags, attrs)
    findall = regex.find_all(pattern, content)
    match_dict = dict()
    for match in findall:
        match_dict[match[0]] = match[3]
    _protocol = protocol.split(u'|')

    def __is_not_full(i, p):
        for _p in p:
            # if isinstance(i, unicode):
            # i = str(i)
            if i.startswith(_p):
                return True
        return False

    for k, v in match_dict.iteritems():
        if not __is_not_full(v, _protocol):
            http_k = urljoin(url, v)
            v2 = k.replace(v, http_k)
            content = content.replace(k, v2)
    return content


def rebuild_url(content, url):
    """
    重建URL，将URL转为绝对网址
    :param content:
    :param url:
    :return:
    """
    return http_join(url, content)


def clear_small_pic(content):
    """
    清除小图片
    :param content:
    :return:
    """
    pattern = u"(<img[^>]*?width\s*=\s*['\"](.+?)['\"][^>]*?>)"
    pics = re.findall(re.compile(pattern, re.I | re.M), content)
    if pics:
        for pic in pics:
            try:
                width = int(pic[1])
                if width < settings.MIN_IMAGE_WIDTH:
                    content = content.replace(pic[0], '')
            except:
                pass
    pattern = u"(<img[^>]*?height\s*=\s*['\"](.+?)['\"][^>]*?>)"
    pics = re.findall(re.compile(pattern, re.I | re.M), content)
    if pics:
        for pic in pics:
            try:
                width = int(pic[1])
                if width < settings.MIN_IMAGE_HEIGHT:
                    content = content.replace(pic[0], '')
            except:
                pass
    return content


def rebuild_img(content):
    """
    重建图片标签
    :param content:
    :return:
    """
    pattern = u"<img[^>]*?{0}\s*=\s*['\"](.+?)['\"][^>]*?>".format(settings.IMG_SRC)
    return regex.replace(pattern,
                         u'<img src="\g<2>" class="img-responsive">', content)


def images(content):
    """
    获取文章所有图片
    :param content:
    :return:
    """
    pattern = u'<img[^>]*?src=["](.+?)["].*?>'
    return list(set(regex.find_all(pattern, content)))


def rebuild(content, url):
    """
    重建URL和重建图片标签
    :param content:
    :param url:
    :return:
    """
    return rebuild_url(rebuild_img(content), url)


def format_content(content):
    """
    清除a，div换p
    :param content:
    :return:
    """
    content = clear_tag(u'a', content)
    content = regex.replace(u'<div.*?>', u'<p>', content)
    content = regex.replace(u'</div.*?>', u'</p>', content)
    content = regex.replace(u'<h1.*?>.*?</h1>', u'', content)
    content = regex.replace(u'>\s*<', u'><', content)
    content = regex.replace(u'<(b|strong|i)[^>]+?/>', u'', content)
    content = regex.replace(u'<img .*?>', u'\g<0><br/>', content)
    # content = regex.replace(u'(</?(p|br)>)+', u'\g<1>', content)
    # content = regex.replace(u'(</?(p|br)>*>)+', u'\g<1>', content)
    content = regex.replace(u'(</?br>)+', u'\g<1>', content)
    # content = regex.replace(u'(<p>\s*</p>)+', u'\g<1>', content)
    # content = regex.replace('[^"\']http://.+?\s*|</?strong>|</?b>|</?i>|</?em>', '', content)
    # content = regex.replace('[^"\']http://.+?\s*', '', content)
    content = regex.replace(u'声明[^><"]+', u'', content)
    content = regex.replace(u'\(?（?原标?题[^><"]+?<', u'<', content)
    content = regex.replace(u'>\s*[\w\d/\-_\.,\?&":\s]+?<', u'><', content)
    content = regex.replace(u'<(p|div)>(&nbsp;)*?</(p|div)>', '', content)
    # content = regex.replace('style=".*?"', '', content)


    # raise Exception(content)

    return content


def clear_content(content):
    content = regex.replace(u'<(?!img|a)(\w*?)\s.*?>', u'<\g<1>>', content)
    content = regex.replace(u'\s*?(<.*?>)\s*', u'\g<1>', content)
    content = regex.replace(u'<(/?)div.*?>', u'<\g<1>p>', content)
    content = regex.replace(u'<(/?)div.*?>', u'<\g<1>p>', content)
    content = regex.replace(u'(<p>)+', u'\g<1>', content)
    content = regex.replace(u'(</p>)+', u'\g<1>', content)
    content = regex.replace(u'<(/?)h\d+.*?>+', u'<\g<1>strong>', content)
    content = regex.replace(u'<p>\s*</p>|<p>.</p>|</?span>|<strong></strong>', u'', content)
    return content
