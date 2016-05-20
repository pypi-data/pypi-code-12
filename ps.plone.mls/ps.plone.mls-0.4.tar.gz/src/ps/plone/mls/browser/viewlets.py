# -*- coding: utf-8 -*-
"""Customized plone viewlets."""

# zope imports
from plone.app.layout.viewlets import common


class TitleViewlet(common.TitleViewlet):
    """Customized title Viewlet for MLS embeddings."""

    def update(self):
        super(TitleViewlet, self).update()

        try:
            title = self.view.item.title.value
        except Exception:
            return
        else:
            self.site_title = u'{0} &mdash; {1}'.format(title, self.site_title)
