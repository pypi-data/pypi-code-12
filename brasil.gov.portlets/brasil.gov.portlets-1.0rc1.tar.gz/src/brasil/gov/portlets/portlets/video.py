# -*- coding: utf-8 -*-
from brasil.gov.portlets import _
from plone import api
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implementer


class IVideoPortlet(IPortletDataProvider):
    '''Portal Padrão: Portlet de vídeo.
    '''

    show_header = schema.Bool(
        title=_(u'show_title',
                default=u'Show title'),
        description=_(u'show_title_description',
                      default=u'If enabled, shows the title.'),
        required=False,
        default=False)

    header = schema.TextLine(
        title=_(u'title_text',
                default=u'Title text'),
        description=_(u'title_text_description',
                      default=u'Portlet text of the title.'),
        required=True,
        default=_(u'title_portlet_video',
                  default=u'Portal Padrão Video'))

    video = schema.Choice(
        title=_(u'Video'),
        description=_(u'Search the video used into the portlet.'),
        required=True,
        source=SearchableTextSourceBinder(
            {'portal_type': ('sc.embedder')},
            default_query='path:'))


@implementer(IVideoPortlet)
class Assignment(base.Assignment):

    show_header = False
    header = _(u'title_portlet_video',
               default=u'Portal Padrão Video')
    video = None

    def __init__(self,
                 show_header=False,
                 header=_(u'title_portlet_video',
                          default=u'Portal Padrão Video'),
                 video=None):
        self.show_header = show_header
        self.header = header
        self.video = video

    @property
    def title(self):
        return self.header


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('templates/video.pt')
    render = _template

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def css_class(self):
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return 'brasil-gov-portlets-video-{0}'.format(normalizer.normalize(header))

    @memoize
    def video(self):
        video_path = self.data.video
        if not video_path:
            return None

        if video_path.startswith('/'):
            video_path = video_path[1:]

        if not video_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        if isinstance(video_path, unicode):
            # restrictedTraverse accepts only strings
            video_path = str(video_path)

        result = portal.unrestrictedTraverse(video_path, default=None)
        if result is not None:
            if not api.user.has_permission('View', obj=result):
                result = None
        return result


class AddForm(base.AddForm):

    form_fields = form.Fields(IVideoPortlet)
    form_fields['video'].custom_widget = UberSelectionWidget

    label = _(u'Add Portlet Portal Padrao Video')
    description = _('video_portlet_description',
                    default=u'This portlet show a Video Player.')

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    form_fields = form.Fields(IVideoPortlet)
    form_fields['video'].custom_widget = UberSelectionWidget

    label = _(u'Edit Portlet Portal Padrao Video')
    description = _('video_portlet_description',
                    default=u'This portlet show a Video Player.')
