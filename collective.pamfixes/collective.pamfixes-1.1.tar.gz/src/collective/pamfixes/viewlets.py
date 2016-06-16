# -*- coding: utf-8 -*-
"""collective.pamfixes custom viewlets."""

# python imports
import pkg_resources
from pkg_resources import parse_version

# Plone imports
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.multilingual.browser.selector import getPostPath
from plone.app.multilingual.browser.viewlets import (
    AlternateLanguagesViewlet)
from plone.memoize import ram, view
from zope.component import getUtility

# local imports
from collective.pamfixes.interfaces import ITranslationManager

pam_distribution = pkg_resources.get_distribution('plone.app.multilingual')
pam_version = pam_distribution.version


def _cache_until_catalog_change_post_path(fun, self):
    catalog = getToolByName(self.context, 'portal_catalog')
    key = '{0}{1}{2}/{3}'
    key = key.format(
        fun.__name__,
        catalog.getCounter(),
        '/'.join(self.context.getPhysicalPath()),
        self.post_path,
    )
    return key


class CustomAlternateLanguagesViewlet(AlternateLanguagesViewlet):
    """Notify search engines about alternates languages of current content
    item.
    """

    @property
    @view.memoize
    def post_path(self):
        return getPostPath(self.context, self.request)

    @ram.cache(_cache_until_catalog_change_post_path)
    def get_alternate_languages_pam_1_x(self):
        """Cache relative urls only. If we have multilingual sites and multi
        domain site caching absolute urls will result in very inefficient
        caching. Build absolute url in template.
        For plone.app.multilingual 1.x
        """
        tm = ITranslationManager(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(
            TranslationGroup=tm.query_canonical(),
            Language='all',
        )

        plone_site = getUtility(IPloneSiteRoot)
        portal_path = '/'.join(plone_site.getPhysicalPath())
        portal_path_len = len(portal_path)

        alternates = []
        for item in results:
            url = item.getURL(relative=1)
            path_len = len('{0:s}/'.format(item.Language))
            if url.startswith(portal_path):
                path_len += portal_path_len
            url = url[path_len:]
            if self.post_path:
                url = '/'.join([url.strip('/'), self.post_path.strip('/')])
            alternates.append({
                'lang': item.Language,
                'url': url.strip('/'),
            })

        return alternates

    @ram.cache(_cache_until_catalog_change_post_path)
    def get_alternate_languages_pam_2_x(self):
        """Cache relative urls only. If we have multilingual sites and multi
        domain site caching absolute urls will result in very inefficient
        caching. Build absolute url in template.
        For plone.app.multilingual 2.x
        """
        tm = ITranslationManager(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(TranslationGroup=tm.query_canonical())

        plone_site = getUtility(IPloneSiteRoot)
        portal_path = '/'.join(plone_site.getPhysicalPath())
        portal_path_len = len(portal_path)

        alternates = []
        for item in results:
            url = item.getURL(relative=1)
            path_len = len('{0:s}/'.format(item.Language))
            if url.startswith(portal_path):
                path_len += portal_path_len
            url = url[path_len:]
            if self.post_path:
                url = '/'.join([url.strip('/'), self.post_path.strip('/')])
            alternates.append({
                'lang': item.Language,
                'url': url.strip('/'),
            })

        return alternates

    def update(self):
        super(CustomAlternateLanguagesViewlet, self).update()
        if parse_version(pam_version) < parse_version('2.0'):
            self.alternates = self.get_alternate_languages_pam_1_x()
        else:
            self.alternates = self.get_alternate_languages_pam_2_x()
