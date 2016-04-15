# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/19.

# 部分代码参考与复制自 python-goose: https://github.com/grangier/python-goose
from collections import Counter
import random
import re
from gelidhttp.log import logger
from lxml import etree
import six

from gelid.extractors import html
from gelid.extractors.enums import ItemProp, Pack


class HtmlTree(object):
    def __init__(self, source, url=None):
        self.url = url
        self.stores = {Pack.html: etree.HTML(source, base_url=url)}

    @property
    def html(self):
        return self.stores.get(Pack.html)

    @property
    def author(self):
        """
        从itemprop获取作者名
        :return:
        """
        nodes = HtmlTree.item_prop(self.html, ItemProp.author.name)
        for node in nodes:
            name_nodes = HtmlTree.item_prop(node, ItemProp.name.name)
            if len(name_nodes) > 0:
                names = HtmlTree.texts(name_nodes[0])
                return u''.join([name.strip() for name in names if isinstance(name, six.string_types)])

    @staticmethod
    def item_prop(node, name):
        """
        从itemprop结构获取节点
        :param node:
        :param name:
        :return:
        """
        return HtmlTree.elements(node, attr=ItemProp.itemprop.name, value=name)

    @staticmethod
    def elements(node, tag=None, attr=None, value=None, child=False):
        """
        使用tag的attr属性值value获取节点
        :param node:原始节点数据
        :param tag:
        :param attr:
        :param value:
        :param child:
        :return:
        """
        ns = "http://exslt.org/regular-expressions"
        selector = 'descendant-or-self::%s' % (tag or '*')
        if attr and value:
            selector = '%s[re:test(@%s, "%s", "i")]' % (selector, attr, value)
        elems = node.xpath(selector, namespaces={"re": ns})
        if node in elems and (tag or child):
            elems.remove(node)
        return elems

    @staticmethod
    def texts(node):
        """
        获取节点内容
        :param node:
        :return:
        """
        return [i for i in node.itertext()]


def content_e(source, template):
    """
    获取两个html的非匹配元素
    :param source:
    :param template:
    :return:
    """
    tree1 = etree.HTML(clear_tag(source))
    tree2 = etree.HTML(clear_tag(template))

    e1, e2 = check_element(tree1, tree2)
    return e1


def content_html(e1):
    """
    获取元素html代码
    :param e1:
    :return:
    """

    return etree.tounicode(e1, method="html")


def clear_tag(source):
    """
    清除匹配时不需要的标签
    :param source:
    :return:
    """
    source = html.set_html_clean(source)
    source = re.sub('<(br|input).*?>', '', source)
    source = re.sub('<(ul|li|option|a|span|select|iframe|noscript|script|style)[^>]*?>[\w\W]*?</\\1>', '', source)
    source = re.sub('<([^>]+?) [^>]+?>\s*</\\1>', '', source)
    # p
    return source


def check_element(e1, e2):
    """
    比较两个lxml元素，直到分析至不同结构时返回
    :param e1:
    :param e2:
    :return:
    """
    l1 = len(e1)
    l2 = len(e2)
    if l1 and l1 != l2:
        return e1, e2  # e1.getparent()
    for i in range(0, l1):

        result = check_element(e1[i], e2[i])
        if result is not None:
            return result


def compare_pairs(item_count=10, max_count=20):
    """
    生成比较配对
    :param item_count:
    :param max_count:
    :return:
    """
    pairs = []
    rand_max_index = item_count - 1
    for i in range(1000):
        pair = (random.randint(0, rand_max_index), random.randint(0, rand_max_index))
        if pair not in pairs and (pair[1], pair[0]) not in pairs:
            pairs.append(pair)
            if len(pairs) >= max_count:
                break
    return pairs


def max_pattern(sources):
    """
    根据内容训练，查找最大数规则
    :param sources:
    :return:
    """
    sources_count = len(sources)
    pairs = compare_pairs(sources_count, 2*sources_count)
    patterns = []
    for pair in pairs:
        try:
            e = content_e(sources[pair[0]], sources[pair[1]])
            p1 = '//{0}[@id="{1}"]'
            p2 = '//{0}[@class="{1}"]'
            p3 = '//{0}[@id="{1}"][@class="{2}"]'
            p4 = '//{0}[@style="{1}"]'
            tag = e.tag
            id = e.attrib.get('id')
            cls = e.attrib.get('class')
            style = e.attrib.get('style')
            if id and cls:
                p = p3.format(tag, id, cls)
            elif id:
                p = p1.format(tag, id)
            elif cls:
                p = p2.format(tag, cls)
            elif style:
                p = p4.format(tag, style)
            else:
                p = ''
            patterns.append(p)
        except Exception,e:
            logger.warning(e)
            # logger.debug("S1-----------------------------------------")
            # logger.debug(sources[pair[0]])
            # logger.debug("S2-----------------------------------------")
            # logger.debug(sources[pair[1]])
            # logger.debug("SE-----------------------------------------")


    c = Counter(patterns)
    ps = c.most_common(1)
    return ps[0][0]
