# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/19.

from gelid.extractors import title, content as ex_content, scan, tm, regex, score
from gelid.extractors.page import Page, store, html
from gelidhttp import request
from gelid import settings


class Article(object):
    def __init__(self, source, url, keyword=None,error_callback=None, next_min=50, parse=None):
        self.page = Page(source=source, url=url)
        self.stores = {}
        self.keyword = keyword
        self.request_all = False
        self.zh_count = 0
        self.next_min = next_min
        self.error_callback = error_callback
        self.parse = parse

    def _request(self, url, contents, pages, contents_images):
        """
        获取分页内容
        :param url:
        :param contents:
        :param pages:
        :param contents_images:
        :return:
        """
        if not contents:
            contents = list()

        if not pages:
            pages = list()

        if url not in pages and len(pages) < settings.REQUEST_MAX_PAGES:
            source = request.Request(url=url, error_callback=self.error_callback).response.body_as_unicode()
            if source:
                article = Article(source, url, parse=self.parse)
                _content = article.content
                # 清除之前有的图片
                for image in contents_images:
                    _content = regex.replace(u'<img .*?src=[\'" ]*{0}[\'" ]*.*?>'.format(image), '', _content)

                for image in article.images:
                    if image not in contents_images:
                        contents_images.append(image)
                if _content not in contents:
                    contents.append(_content)
                    pages.append(url)
                    next_page = html.next_page(url, source)
                    if next_page:
                        self._request(next_page, contents, pages, contents_images)

        self.page.stores['images'] = contents_images
        return contents

    def _page_contents(self):
        """
        获取所有分页内容
        :return:
        """
        pages = [self.page.url]
        contents = [self.content]
        contents_images = self.images
        next_page = html.next_page(self.page.url, self.page.html_clean)
        # 仅当有下一页且本内容有图片或汉字大于100字时获取下一页内容
        if next_page and (self.images or self.zh_count>self.next_min):
            return self._request(next_page, contents, pages, contents_images)
        else:
            return contents

    @property
    @store
    def page_contents(self):
        """
        所有分页内容
        :return:
        """
        self.request_all = True
        return self._page_contents()

    @property
    @store
    def title(self):
        """
        基于title文本扫描分析标题
        :return:
        """
        article_title = title.title_in_content(self.page.title, self.page.body)
        return article_title


    @property
    @store
    def content(self):
        if self.parse == 'readability':
            _content =  ex_content.readability_content(self.page.html_clean)
            zh_text = regex.zh_cn(_content)
            self.zh_count = len(zh_text)
        elif self.parse == 'distance':
            _content =  ex_content.distance_content(self.page.html_clean)
            zh_text = regex.zh_cn(_content)
            self.zh_count = len(zh_text)
        else:
            rank_content =  ex_content.rank_content_with_count(self.page.html_clean, clear=True)
            _content = rank_content[0]
            self.zh_count = rank_content[1]
        _content = html.rebuild(_content, self.page.url)
        _content = html.format_content(_content)
        return _content

    @property
    @store
    def author(self):
        return scan.get_author(self.page.txt)

    @property
    @store
    def time_posted(self):
        return tm.get_timestamp(scan.get_time(self.page.txt))

    @property
    @store
    def come_from(self):
        return scan.get_from(self.page.txt)
    @property
    @store
    def description(self):
        desc = regex.remove_all_tags(self.content)
        desc = regex.remove_all_blank(desc)
        if len(desc)>50:
            desc = desc[:50]
        return desc

    @property
    @store
    def images(self):
        return html.images(self.content)

    @property
    @store
    def rank(self):

        if self.request_all:
            _content = u'<p><!--pager--></p>'.join(self.page_contents)
        else:
            _content = self.content

        article = dict(content=_content, title=self.title, keyword=self.keyword, posted_date=self.time_posted)
        stat = score.Score(article)
        return stat.rank