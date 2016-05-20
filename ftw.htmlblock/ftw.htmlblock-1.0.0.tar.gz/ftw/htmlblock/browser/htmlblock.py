from ftw.simplelayout.browser.blocks.base import BaseBlock
from plone import api


class HtmlBlockView(BaseBlock):
    def __call__(self):
        return self.index()

    def can_add(self):
        return api.user.has_permission('ftw.htmlblock: Add HTML block')
