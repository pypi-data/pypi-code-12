# -*- coding: utf-8 -*-
from brasil.gov.portlets.portlets import audiogallery
from brasil.gov.portlets.testing import INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.GenericSetup.utils import _getDottedName
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class AudioGalleryPortletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.audios = {}
        self.audios['collection'] = self.portal['audios-folder']['audios-collection']
        self.audios['path'] = '/' + '/'.join(self.audios['collection'].getPhysicalPath()[2:])
        self.audios['url'] = self.audios['collection'].absolute_url()

    def _renderer(self, context=None, request=None, view=None, manager=None,
                  assignment=None):
        context = context or self.portal
        request = request or self.request
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def _assigned_renderer(self, col):
        assgmnt = audiogallery.Assignment(
            show_header=True,
            header=u'Portal Padrão Galeria de Áudios',
            header_type=u'H2',
            show_footer=True,
            footer=u'Mais...',
            footer_url=col['url'],
            limit=3,
            collection=col['path']
        )
        r = self._renderer(context=self.portal,
                           assignment=assgmnt)
        r = r.__of__(self.portal)
        r.update()
        return r

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.audiogallery')
        self.assertEqual(portlet.addview, 'brasil.gov.portlets.audiogallery')

    def test_registered_interfaces(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.audiogallery')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(
            ['plone.app.portlets.interfaces.IColumn',
             'plone.app.portlets.interfaces.IDashboard'],
            registered_interfaces
        )

    def test_interfaces(self):
        portlet = audiogallery.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_addview(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.audiogallery')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], audiogallery.Assignment))

    def test_portlet_properties(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.audiogallery')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={
            'show_header': True,
            'header': u'Portal Padrão Galeria de Áudios',
            'header_type': u'H4',
            'show_footer': True,
            'footer': u'Mais...',
            'footer_url': self.audios['url'],
            'limit': 2,
            'collection': self.audios['path']
        })

        title = mapping.values()[0].title
        self.assertEqual(title, u'Portal Padrão Galeria de Áudios')

        header = mapping.values()[0].header
        self.assertEqual(header, u'Portal Padrão Galeria de Áudios')

        header_type = mapping.values()[0].header_type
        self.assertEqual(header_type, u'H4')

        show_footer = mapping.values()[0].show_footer
        self.assertEqual(show_footer, True)

        footer = mapping.values()[0].footer
        self.assertEqual(footer, u'Mais...')

        footer_url = mapping.values()[0].footer_url
        self.assertEqual(footer_url, self.audios['url'])

        limit = mapping.values()[0].limit
        self.assertEqual(limit, 2)

        collection = mapping.values()[0].collection
        self.assertEqual(collection, self.audios['path'])

    def test_renderer(self):
        r = self._assigned_renderer(self.audios)

        self.assertIsInstance(r, audiogallery.Renderer)

    def test_renderer_cssclass(self):
        r1 = self._assigned_renderer(self.audios)

        self.assertEqual(r1.css_class(),
                         'brasil-gov-portlets-audiogallery-portal-padrao-galeria-de-audios')

    def test_renderer_results(self):
        r = self._assigned_renderer(self.audios)

        results = [b.id for b in r.results()]
        self.assertEqual(results, ['audio-2', 'audio-3', 'audio-1'])

    def test_renderer_collection(self):
        r = self._assigned_renderer(self.audios)

        self.assertEqual(r.collection(), self.audios['collection'])

    def test_renderer_title(self):
        r = self._assigned_renderer(self.audios)

        self.assertEqual(r.title(),
                         u'<h2 class="portlet-audiogallery-title">Portal ' +
                         u'Padr&#227;o Galeria de &#193;udios</h2>')

    def test_renderer_getitemurl(self):
        r = self._assigned_renderer(self.audios)

        urls = [r.get_item_url(b) for b in r.results()]
        self.assertEqual(urls, [
            'http://nohost/plone/audios-folder/audio-2/file.mp3',
            'http://nohost/plone/audios-folder/audio-3/file.mp3',
            'http://nohost/plone/audios-folder/audio-1/file.mp3'
        ])
