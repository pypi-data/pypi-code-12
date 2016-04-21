# -*- coding: utf-8 -*-
import re
from collections import Counter
from urlparse import *

from gelid.extractors import regex
from gelid.extractors.decorator import store


class Link(object):
    """获取页面链接"""
    _pattern = "<a [^>]*?href[\s=]*[\"']?(%s)[\"' ][^>]*?>"

    def __init__(self, page):
        self.page = page
        self.stores = {}

    @property
    @store
    def urls(self):
        """
        获取页面所有链接
        :return:

        """
        html = self.page.html
        link_pattern = self._pattern % "[^>'\" ]*"
        findall = regex.find_all(link_pattern, html)
        if findall:
            findall = list(set(findall))

        hostname = Link.url_domain(self.page.url)
        findall = [urljoin(hostname, url) for url in findall]
        return findall

    @staticmethod
    def url_domain(url):
        """
        获取网址域名
        :param url:
        :return:
        """

        parse = urlparse(url)

        return '%s://%s' % (parse.scheme,parse.hostname)

    @property
    @store
    def domain_urls(self):
        """
        获取页面所有当前域名的链接
        :return:

        """
        hostname = Link.url_domain(self.page.url)

        return filter(lambda x: re.search(hostname, x), self.urls)

    @staticmethod
    def _max_urls(urls):
        """
        获取最大规则的链接集
        :param urls:
        :return:
        """

        pattern = Link.max_pattern(urls)
        return filter(lambda x: re.search(pattern, x), urls)


    @staticmethod
    def create_pattern(url):
        """
        创建链接规则
        :param url:
        :return:
        """
        return re.sub('\d+', '\d+', re.sub('[a-zA-Z]+', '[a-zA-Z]+', url))

    @staticmethod
    def create_domain_pattern(url):
        """
        创建当前链接基于域名的规则
        :param url:
        :return:
        """
        temp = '___--___'
        hostname = Link.url_domain(url)
        url = url.replace(hostname, temp)
        url = Link.create_pattern(url)
        url = url.replace(temp, hostname)
        return url

    @staticmethod
    def max_pattern(urls):
        """
        获取当前链接最大规则
        :param urls:
        :return:
        """
        _urls = []
        for url in urls:
            _urls.append(Link.create_pattern(url))
        c = Counter(_urls)
        ps = c.most_common(1)
        return ps[0][0]

    @property
    @store
    def max_urls(self):
        """
        获取当前页面最大规则链接集
        :return:
        """
        return Link._max_urls(self.urls)

    @property
    @store
    def domain_max_urls(self):
        """
        获取当前页面最大链接集规则
        :return:
        """
        return Link._max_urls(self.domain_urls)

    def urls_by_pattern(self, pattern):
        """
        获取页面所有链接
        :return:

        """
        html = self.page.html
        link_pattern = self._pattern % (pattern or "[^>'\" ]*")
        findall = regex.find_all(link_pattern, html)
        return findall

    def urls_by_full_pattern(self, pattern):
        """
        获取页面所有链接
        :return:

        """
        html = self.page.html
        findall = regex.find_all(pattern or self._pattern, html)
        return findall
