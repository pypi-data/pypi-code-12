from Acquisition import aq_inner
from collective.ogtags.browser.controlpanel import IOGTagsControlPanel
from plone.app.layout.viewlets import ViewletBase
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import safe_unicode
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter

import cgi


def escape(value):
    """Extended escape, taken from quintagroup.seoptimizer."""
    value = cgi.escape(value, True)
    return value.replace("'", "&apos;")


class OGTagsViewlet(ViewletBase):

    def meta_tags(self):
        try:
            self.settings = getUtility(
                IRegistry).forInterface(IOGTagsControlPanel)
        except (ComponentLookupError, KeyError):
            return
        if not self.settings.enabled:
            return
        context = aq_inner(self.context)
        tags = {}

        # Basic properties
        title = context.title
        description = context.Description()
        url = context.absolute_url()

        # Allow overrides from quintagroup.seoptimizer
        seo = queryMultiAdapter(
            (self.context, self.request), name='seo_context')
        if seo is not None:
            if seo['has_seo_title']:
                title = safe_unicode(seo["seo_title"])
            if seo['has_seo_description']:
                description = safe_unicode(seo["seo_description"])
            if seo['has_seo_canonical']:
                url = safe_unicode(seo["seo_canonical"])

        # set title
        if title:
            title = escape(title)
            tags['og:title'] = title
            tags['twitter:title'] = title

        # set description
        if description:
            description = escape(description)
            tags['og:description'] = description
            tags['twitter:description'] = description

        # set url
        if url:
            tags['og:url'] = url

        # social media specific
        if self.settings.fb_id:
            tags['fb:app_id'] = self.settings.fb_id
        if self.settings.fb_username:
            tags['og:article:publisher'] = 'https://www.facebook.com/' \
                + self.settings.fb_username
        if self.settings.tw_id:
            tags['twitter:site'] = self.settings.tw_id
        tags['twitter:card'] = u'summary'

        # misc
        tags['og:type'] = u'website'
        if self.settings.og_site_name:
            tags['og:site_name'] = self.settings.og_site_name

        return tags

    def image_tags(self):
        try:
            self.settings = getUtility(
                IRegistry).forInterface(IOGTagsControlPanel)
        except (ComponentLookupError, KeyError):
            return
        if not self.settings.enabled:
            return
        tags = []
        context = aq_inner(self.context)
        try:
            scales = context.restrictedTraverse(
                '/'.join(context.getPhysicalPath()) + '/@@images')
        except (AttributeError, KeyError):
            return self.default_image(self.settings.default_img)
        if not scales:
            return self.default_image(self.settings.default_img)
        try:
            image = context.image
            field = 'image'
        except:
            try:
                image = context.getField(
                    'image') or context.getField('leadImage')
                field = image.getName()
                if not field:
                    raise AttributeError
            except AttributeError:
                return self.default_image(self.settings.default_img)
        tag_scales = []
        for scale in [
                'og_fbl',
                'og_fb',
                'og_tw',
                'og_ln']:
            fieldname = field or 'image'
            try:
                image = scales.scale(fieldname, scale=scale)
                if not image:
                    continue
            except AttributeError:
                continue
            tag = {}
            if scale == 'og_tw':
                tag['twitter:image'] = image.url
            else:
                if (image.width, image.height) not in tag_scales:
                    tag['og:image'] = image.url
                    tag['og:image:width'] = image.width
                    tag['og:image:height'] = image.height
                    tag_scales.append((image.width, image.height))
            tags.append(tag.copy())
        if not tags:
            return self.default_image(self.settings.default_img)
        return tags

    def default_image(self, image):
        if not image:
            return
        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')
        site_root_url = portal_state.navigation_root_url()
        twitter_tag = {}
        twitter_tag['twitter:image'] = '%s%s' % (site_root_url, image)
        og_tag = {}
        og_tag['og:image'] = '%s%s' % (site_root_url, image)
        return [twitter_tag, og_tag]
