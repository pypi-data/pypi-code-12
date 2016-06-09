# -*- coding: utf-8 -*-
from brasil.gov.portlets import _
from DateTime import DateTime
from lxml import html
from lxml.html import builder as E
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
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def default_image_scale(context):
    image_scale = None
    properties_tool = api.portal.get_tool(name='portal_properties')
    imagescales_properties = getattr(properties_tool,
                                     'imaging_properties',
                                     None)
    raw_scales = getattr(imagescales_properties, 'allowed_sizes', None)
    if (raw_scales):
        image_scale = raw_scales[0]
    return image_scale


class ICollectionPortlet(IPortletDataProvider):
    '''Portal Padrao: Collection Portlet.
    '''

    header = schema.TextLine(
        title=_(u'title_text',
                default=u'Title text'),
        description=_(u'title_text_description',
                      default=u'Portlet text of the title.'),
        required=True,
        default=_(u'title_portlet_collection',
                  default=u'Portal Padrao Collection'))

    header_url = schema.TextLine(
        title=_(u'title_url',
                default=u'Title URL'),
        description=_(u'title_url_description',
                      default=u'Portlet title URL.'),
        required=False)

    show_image = schema.Bool(
        title=_(u'show_image',
                default=u'Show Image'),
        description=_(u'show_image_description',
                      default=u'If enabled, shows the image.'),
        required=False,
        default=False)

    image_size = schema.Choice(
        title=_(u'image_size',
                default=u'Image size'),
        description=_(u'image_size_description',
                      default=u'Image size that will be shown.'),
        vocabulary='brasil.image.scales',
        required=True,
        defaultFactory=default_image_scale
    )

    title_type = schema.Choice(
        title=_(u'title_type',
                default=u'Title type'),
        description=_(u'title_type_description',
                      default=u'Title type that will be shown.'),
        values=(u'H1',
                u'H2',
                u'H3',
                u'H4'),
        default=u'H2',
        required=True,
    )

    show_footer = schema.Bool(
        title=_(u'show_footer',
                default=u'Show footer'),
        description=_(u'show_footer_description',
                      default=u'If enabled, shows the footer.'),
        required=False,
        default=False)

    footer = schema.TextLine(
        title=_(u'footer_text',
                default=u'Footer text'),
        description=_(u'footer_text_description',
                      default=u'Portlet footer text.'),
        required=False)

    footer_url = schema.TextLine(
        title=_(u'footer_url',
                default=u'Footer URL'),
        description=_(u'footer_url_description',
                      default=u'Portlet footer URL.'),
        required=False)

    limit = schema.Int(
        title=_(u'limit',
                default=u'Number of items to show'),
        description=_(u'limit_description',
                      default=u'Total itens that should be displayed in ' +
                              u'the portlet.'),
        required=True,
        default=5)

    show_date = schema.Bool(
        title=_(u'show_date',
                default=u'Show date'),
        description=_(u'show_date_description',
                      default=u'If enabled, shows the date.'),
        required=False,
        default=False)

    show_time = schema.Bool(
        title=_(u'show_time',
                default=u'Show time'),
        description=_(u'show_time_description',
                      default=u'If enabled, shows the time.'),
        required=False,
        default=False)

    collection = schema.Choice(
        title=_(u'collection',
                default=u'Collection'),
        description=_(u'collection_description',
                      default=u'Searchs the collection that will be used ' +
                              u'in the portlet.'),
        required=True,
        source=SearchableTextSourceBinder(
            {'portal_type': ('Topic', 'Collection')},
            default_query='path:'))


@implementer(ICollectionPortlet)
class Assignment(base.Assignment):

    header = _(u'title_portlet_collection',
               default=u'Portal Padrao Collection')
    header_url = u''
    show_image = False
    image_size = None
    title_type = u'H2'
    show_footer = False
    footer = u''
    footer_url = u''
    limit = 5
    show_date = False
    show_time = False
    collection = None

    def __init__(self,
                 header=_(u'title_portlet_collection',
                          default=u'Portal Padrao Collection'),
                 header_url=u'',
                 show_image=False,
                 image_size=None,
                 title_type=u'H2',
                 show_footer=False,
                 footer=u'',
                 footer_url=u'',
                 limit=5,
                 show_date=False,
                 show_time=False,
                 collection=None):
        self.header = header
        self.header_url = header_url
        self.show_image = show_image
        self.image_size = image_size
        self.title_type = title_type
        self.show_footer = show_footer
        self.footer = footer
        self.footer_url = footer_url
        self.limit = limit
        self.show_date = show_date
        self.show_time = show_time
        self.collection = collection

    @property
    def title(self):
        return self.header


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('templates/collection.pt')
    render = _template

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def css_class(self):
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return 'brasil-gov-portlets-collection-{0}'.format(normalizer.normalize(header))

    def _collection_type_criteria(self, collection):
        type_criteria = u''
        for c in collection.query:
            if ((c[u'i'] == u'portal_type') and
               (c[u'o'] == u'plone.app.querystring.operation.selection.is')):
                type_criteria = c[u'v']
                break
        return type_criteria

    @memoize
    def results(self):
        results = []
        collection = self.collection()
        query = {}
        if collection is not None:
            if (self._collection_type_criteria(collection) in [u'Compromisso',
                                                               u'Event']):
                query['sort_on'] = u'start'
            limit = self.data.limit
            if limit and limit > 0:
                # pass on batching hints to the catalog
                query['batch'] = True
                query['b_size'] = limit
                results = collection.queryCatalog(**query)
                results = results._sequence
            else:
                results = collection.queryCatalog(**query)
            if limit and limit > 0:
                results = results[:limit]
        return [b.getObject() for b in results]

    @memoize
    def collection(self):
        collection_path = self.data.collection
        if not collection_path:
            return None

        if collection_path.startswith('/'):
            collection_path = collection_path[1:]

        if not collection_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        if isinstance(collection_path, unicode):
            # restrictedTraverse accepts only strings
            collection_path = str(collection_path)

        result = portal.unrestrictedTraverse(collection_path, default=None)
        if result is not None:
            if not api.user.has_permission('View', obj=result):
                result = None
        return result

    def thumbnail(self, item):
        """Return a thumbnail of an image if the item has an image field and
        the field is visible in the portlet.

        :param item: [required]
        :type item: content object
        """
        if self._has_image_field(item) and self.data.show_image:
            scaleconf = self.data.image_size
            # scale string is something like: 'mini 200:200'
            scale = scaleconf.split(' ')[0]  # we need the name only: 'mini'
            scales = item.restrictedTraverse('@@images')
            return scales.scale('image', scale)

    def title(self, item):
        '''Generate html part with following structure
        <HX>
            <a href='${item/absolute_url}'
               title='${item/Description}'>
                ${item/Title}
            </a>
        </HX>
        '''
        hx = getattr(E, self.data.title_type)(E.CLASS('portlet-collection-title'))
        hx.append(
            E.A(item.Title().decode('utf-8'),
                href=item.absolute_url(),
                title=item.Description().decode('utf-8'))
        )
        return html.tostring(hx)

    def date(self, item):
        dt = DateTime(item.Date())
        if (item.portal_type in [u'Compromisso',
                                 u'Event']):
            dt = DateTime(item.start_date)
        if self.data.show_time:
            return dt.strftime('%d/%m/%Y | %H:%M')
        else:
            return dt.strftime('%d/%m/%Y')


class AddForm(base.AddForm):

    form_fields = form.Fields(ICollectionPortlet)
    form_fields['collection'].custom_widget = UberSelectionWidget

    label = _(u'Add Portlet Portal Padrao Collection')
    description = _(u'collection_portlet_description',
                    default=u'This portlet shows an item list of one ' +
                            u'Collection')

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    form_fields = form.Fields(ICollectionPortlet)
    form_fields['collection'].custom_widget = UberSelectionWidget

    label = _(u'Edit Portlet Portal Padrao Collection')
    description = _(u'collection_portlet_description',
                    default=u'This portlet shows an item list of one ' +
                            u'Collection')
