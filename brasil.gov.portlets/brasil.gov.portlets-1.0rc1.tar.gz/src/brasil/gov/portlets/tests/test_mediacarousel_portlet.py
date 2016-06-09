# -*- coding: utf-8 -*-
from brasil.gov.portlets.portlets import mediacarousel
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


class MediaCarouselPortletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.images = {}
        self.images['collection'] = self.portal['images-folder']['images-collection']
        self.images['path'] = '/' + '/'.join(self.images['collection'].getPhysicalPath()[2:])
        self.images['url'] = self.images['collection'].absolute_url()

        self.files = {}
        self.files['collection'] = self.portal['files-folder']['files-collection']
        self.files['path'] = '/' + '/'.join(self.files['collection'].getPhysicalPath()[2:])
        self.files['url'] = self.files['collection'].absolute_url()

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
        assgmnt = mediacarousel.Assignment(
            show_header=True,
            header=u'Portal Padrão Carrossel de Imagens',
            header_type=u'H2',
            show_title=True,
            show_description=True,
            show_footer=True,
            footer=u'Mais...',
            footer_url=col['url'],
            show_rights=True,
            limit=3,
            collection=col['path']
        )
        r = self._renderer(context=self.portal,
                           assignment=assgmnt)
        r = r.__of__(self.portal)
        r.update()
        return r

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.mediacarousel')
        self.assertEqual(portlet.addview, 'brasil.gov.portlets.mediacarousel')

    def test_registered_interfaces(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.mediacarousel')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(
            ['plone.app.portlets.interfaces.IColumn',
             'plone.app.portlets.interfaces.IDashboard'],
            registered_interfaces
        )

    def test_interfaces(self):
        portlet = mediacarousel.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_addview(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.mediacarousel')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], mediacarousel.Assignment))

    def test_portlet_properties(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.mediacarousel')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={
            'show_header': True,
            'header': u'Portal Padrão Carrossel de Imagens',
            'header_type': u'H4',
            'show_title': True,
            'show_description': True,
            'show_footer': True,
            'footer': u'Mais...',
            'footer_url': self.images['url'],
            'show_rights': True,
            'limit': 2,
            'collection': self.images['path']
        })

        title = mapping.values()[0].title
        self.assertEqual(title, u'Portal Padrão Carrossel de Imagens')

        header = mapping.values()[0].header
        self.assertEqual(header, u'Portal Padrão Carrossel de Imagens')

        header_type = mapping.values()[0].header_type
        self.assertEqual(header_type, u'H4')

        show_title = mapping.values()[0].show_title
        self.assertEqual(show_title, True)

        show_description = mapping.values()[0].show_description
        self.assertEqual(show_description, True)

        show_footer = mapping.values()[0].show_footer
        self.assertEqual(show_footer, True)

        footer = mapping.values()[0].footer
        self.assertEqual(footer, u'Mais...')

        footer_url = mapping.values()[0].footer_url
        self.assertEqual(footer_url, self.images['url'])

        show_rights = mapping.values()[0].show_rights
        self.assertEqual(show_rights, True)

        limit = mapping.values()[0].limit
        self.assertEqual(limit, 2)

        collection = mapping.values()[0].collection
        self.assertEqual(collection, self.images['path'])

    def test_renderer(self):
        r = self._assigned_renderer(self.images)

        self.assertIsInstance(r, mediacarousel.Renderer)

    def test_renderer_cssclass(self):
        r1 = self._assigned_renderer(self.images)

        self.assertEqual(r1.css_class(),
                         'brasil-gov-portlets-mediacarousel-portal-padrao-carrossel-de-imagens')

    def test_renderer_results(self):
        r = self._assigned_renderer(self.images)

        results = [b.id for b in r.results()]
        self.assertEqual(results, ['image-2', 'image-3', 'image-1'])

    def test_renderer_collection(self):
        r = self._assigned_renderer(self.images)

        self.assertEqual(r.collection(), self.images['collection'])

    def test_renderer_header(self):
        r = self._assigned_renderer(self.images)

        self.assertEqual(r.header(), u'<h2>Portal Padr&#227;o Carrossel de Imagens</h2>')

    def test_renderer_thumbnail(self):
        r1 = self._assigned_renderer(self.files)
        r2 = self._assigned_renderer(self.images)

        images = [r1.thumbnail(o) for o in r1.results()]
        self.assertEqual(images, [None, None, None])

        images = [r2.thumbnail(o) for o in r2.results()]
        img_order = [2, 3, 1]
        for i, img in enumerate(images):
            self.assertIn('src', img)
            self.assertTrue(img['src'])
            self.assertIn('alt', img)
            self.assertEqual(img['alt'],
                             ('Image {0} description - Lorem ipsum dolor sit ' +
                              'amet, consectetur adipiscing elit. Donec ' +
                              'eleifend hendrerit interdum.')
                             .format(img_order[i]))

    def test_renderer_scale(self):
        r1 = self._assigned_renderer(self.files)
        r2 = self._assigned_renderer(self.images)

        images = [r1.scale(o) for o in r1.results()]
        self.assertEqual(images, [None, None, None])

        images = [r2.scale(o) for o in r2.results()]
        img_order = [2, 3, 1]
        for i, img in enumerate(images):
            self.assertIn('src', img)
            self.assertTrue(img['src'])
            self.assertIn('alt', img)
            self.assertEqual(img['alt'],
                             ('Image {0} description - Lorem ipsum dolor sit ' +
                              'amet, consectetur adipiscing elit. Donec ' +
                              'eleifend hendrerit interdum.')
                             .format(img_order[i]))
