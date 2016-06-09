# -*- coding: utf-8 -*-
from brasil.gov.portlets.portlets import collection
from brasil.gov.portlets.testing import INTEGRATION_TESTING
from plone.app.imaging.interfaces import IImageScale
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


class CollectionPortletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.news = {}
        self.news['collection'] = self.portal['news-folder']['news-collection']
        self.news['path'] = '/' + '/'.join(self.news['collection'].getPhysicalPath()[2:])
        self.news['url'] = self.news['collection'].absolute_url()

        self.events = {}
        self.events['collection'] = self.portal['events-folder']['events-collection']
        self.events['path'] = '/' + '/'.join(self.events['collection'].getPhysicalPath()[2:])
        self.events['url'] = self.events['collection'].absolute_url()

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

    def _assigned_renderer(self, col, showtime=False):
        assgmnt = collection.Assignment(
            header=u'Portal Padrão Coleção',
            header_url=u'http://www.plone.org',
            show_image=True,
            image_size=u'large 768:768',
            title_type=u'H4',
            show_footer=True,
            footer=u'Mais...',
            footer_url=col['url'],
            limit=3,
            show_date=True,
            show_time=showtime,
            collection=col['path']
        )
        r = self._renderer(context=self.portal,
                           assignment=assgmnt)
        r = r.__of__(self.portal)
        r.update()
        return r

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.collection')
        self.assertEqual(portlet.addview, 'brasil.gov.portlets.collection')

    def test_registered_interfaces(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.collection')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(
            ['plone.app.portlets.interfaces.IColumn',
             'plone.app.portlets.interfaces.IDashboard'],
            registered_interfaces
        )

    def test_interfaces(self):
        portlet = collection.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_addview(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.collection')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], collection.Assignment))

    def test_portlet_properties(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.collection')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={
            'header': u'Portal Padrão Coleção',
            'header_url': u'http://www.plone.org',
            'show_image': True,
            'image_size': u'large 768:768',
            'title_type': u'H4',
            'show_footer': True,
            'footer': u'Mais...',
            'footer_url': self.news['url'],
            'limit': 2,
            'show_date': True,
            'show_time': True,
            'collection': self.news['path']
        })

        title = mapping.values()[0].title
        self.assertEqual(title, u'Portal Padrão Coleção')

        header = mapping.values()[0].header
        self.assertEqual(header, u'Portal Padrão Coleção')

        header_url = mapping.values()[0].header_url
        self.assertEqual(header_url, u'http://www.plone.org')

        show_image = mapping.values()[0].show_image
        self.assertEqual(show_image, True)

        image_size = mapping.values()[0].image_size
        self.assertEqual(image_size, u'large 768:768')

        title_type = mapping.values()[0].title_type
        self.assertEqual(title_type, u'H4')

        show_footer = mapping.values()[0].show_footer
        self.assertEqual(show_footer, True)

        footer = mapping.values()[0].footer
        self.assertEqual(footer, u'Mais...')

        footer_url = mapping.values()[0].footer_url
        self.assertEqual(footer_url, self.news['url'])

        limit = mapping.values()[0].limit
        self.assertEqual(limit, 2)

        show_date = mapping.values()[0].show_date
        self.assertEqual(show_date, True)

        show_time = mapping.values()[0].show_time
        self.assertEqual(show_time, True)

        collection = mapping.values()[0].collection
        self.assertEqual(collection, self.news['path'])

    def test_renderer(self):
        r1 = self._assigned_renderer(self.news)
        r2 = self._assigned_renderer(self.events)

        self.assertIsInstance(r1, collection.Renderer)

        self.assertIsInstance(r2, collection.Renderer)

    def test_renderer_cssclass(self):
        r1 = self._assigned_renderer(self.news)

        self.assertEqual(r1.css_class(),
                         'brasil-gov-portlets-collection-portal-padrao-colecao')

    def test_renderer_typecriteria(self):
        r1 = self._assigned_renderer(self.news)
        r2 = self._assigned_renderer(self.events)

        type_criteria = r1._collection_type_criteria(self.news['collection'])
        self.assertEqual(type_criteria, u'News Item')

        type_criteria = r2._collection_type_criteria(self.events['collection'])
        self.assertEqual(type_criteria, u'Event')

    def test_renderer_results(self):
        r1 = self._assigned_renderer(self.news)
        r2 = self._assigned_renderer(self.events)

        results = [b.id for b in r1.results()]
        self.assertEqual(results, ['new-2', 'new-3', 'new-1'])

        results = [b.id for b in r2.results()]
        self.assertEqual(results, ['event-3', 'event-2', 'event-1'])

    def test_renderer_collection(self):
        r1 = self._assigned_renderer(self.news)
        r2 = self._assigned_renderer(self.events)

        self.assertEqual(r1.collection(), self.news['collection'])

        self.assertEqual(r2.collection(), self.events['collection'])

    def test_renderer_thumbnail(self):
        r1 = self._assigned_renderer(self.files)
        r2 = self._assigned_renderer(self.images)

        images = [r1.thumbnail(o) for o in r1.results()]
        self.assertEqual(images, [None, None, None])

        images = [r2.thumbnail(o) for o in r2.results()]
        for img in images:
            self.assertTrue(img)
            self.assertTrue(IImageScale.providedBy(img))

    def test_renderer_title(self):
        r1 = self._assigned_renderer(self.news)
        r2 = self._assigned_renderer(self.events)

        titles = [r1.title(o) for o in r1.results()]
        self.assertEqual(titles, [
            ('<h4 class="portlet-collection-title"><a ' +
             'href="http://nohost/plone/news-folder/new-2" ' +
             'title="New 2 description - Lorem ipsum dolor sit amet, ' +
             'consectetur adipiscing elit. Donec eleifend hendrerit ' +
             'interdum.">New 2</a></h4>'),
            ('<h4 class="portlet-collection-title"><a ' +
             'href="http://nohost/plone/news-folder/new-3" ' +
             'title="New 3 description - Lorem ipsum dolor sit amet, ' +
             'consectetur adipiscing elit. Donec eleifend hendrerit ' +
             'interdum.">New 3</a></h4>'),
            ('<h4 class="portlet-collection-title"><a ' +
             'href="http://nohost/plone/news-folder/new-1" ' +
             'title="New 1 description - Lorem ipsum dolor sit amet, ' +
             'consectetur adipiscing elit. Donec eleifend hendrerit ' +
             'interdum.">New 1</a></h4>')
        ])

        titles = [r2.title(o) for o in r2.results()]
        self.assertEqual(titles, [
            ('<h4 class="portlet-collection-title"><a ' +
             'href="http://nohost/plone/events-folder/event-3" ' +
             'title="Event 3 description - Lorem ipsum dolor sit amet, ' +
             'consectetur adipiscing elit. Donec eleifend hendrerit ' +
             'interdum.">Event 3</a></h4>'),
            ('<h4 class="portlet-collection-title"><a ' +
             'href="http://nohost/plone/events-folder/event-2" ' +
             'title="Event 2 description - Lorem ipsum dolor sit amet, ' +
             'consectetur adipiscing elit. Donec eleifend hendrerit ' +
             'interdum.">Event 2</a></h4>'),
            ('<h4 class="portlet-collection-title"><a ' +
             'href="http://nohost/plone/events-folder/event-1" ' +
             'title="Event 1 description - Lorem ipsum dolor sit amet, ' +
             'consectetur adipiscing elit. Donec eleifend hendrerit ' +
             'interdum.">Event 1</a></h4>')
        ])

    def test_renderer_date(self):
        r1 = self._assigned_renderer(self.news)
        r2 = self._assigned_renderer(self.events, showtime=True)

        dates = [r1.date(o) for o in r1.results()]
        self.assertEqual(dates, ['01/05/2014', '02/05/2014', '03/05/2014'])

        dates = [r2.date(o) for o in r2.results()]
        r2List = [
            '01/05/2014 | 17:23',
            '02/05/2014 | 17:23',
            '03/05/2014 | 17:23'
        ]
        if ('01/05/2014 | 14:23' in dates):
            r2List = [
                '01/05/2014 | 14:23',
                '02/05/2014 | 14:23',
                '03/05/2014 | 14:23'
            ]
        self.assertEqual(dates, r2List)
