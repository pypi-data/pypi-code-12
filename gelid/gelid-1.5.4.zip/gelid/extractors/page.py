# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/19.
from gelid.extractors import html
from gelid.extractors.decorator import store


class Page(object):
    """页面HTML片断存储"""

    def __init__(self, source, url=None):
        self.url = url
        self.stores = {'html': source}

    @property
    @store
    def html(self):
        return None

    @property
    @store
    def header(self):
        return self._default_html(html.inner_text('header', self.html))

    def _default_html(self, value):
        if not value:
            return self.html
        else:
            return value

    @property
    @store
    def body(self):

        return self._default_html(html.inner_text('body', self.html))

    @property
    @store
    def title(self):
        return html.inner_text('title', self.html)

    @property
    @store
    def html_clean(self):
        return html.set_html_clean(self.html)

    @property
    @store
    def txt(self):
        return html.txt(self.html_clean)
