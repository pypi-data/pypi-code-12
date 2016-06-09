# -*- coding: utf-8 -*-
from brasil.gov.portlets.portlets import video
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


class VideoPortletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.video = {}
        self.video['object'] = self.portal['videos-folder']['video-1']
        self.video['path'] = '/' + '/'.join(self.video['object'].getPhysicalPath()[2:])

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
        assgmnt = video.Assignment(
            show_header=False,
            header=u'Portal Padrão Vídeo',
            video=col['path']
        )
        r = self._renderer(context=self.portal,
                           assignment=assgmnt)
        r = r.__of__(self.portal)
        r.update()
        return r

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.video')
        self.assertEqual(portlet.addview, 'brasil.gov.portlets.video')

    def test_registered_interfaces(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.video')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(
            ['plone.app.portlets.interfaces.IColumn',
             'plone.app.portlets.interfaces.IDashboard'],
            registered_interfaces
        )

    def test_interfaces(self):
        portlet = video.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_addview(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.video')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], video.Assignment))

    def test_portlet_properties(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.video')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={
            'show_header': True,
            'header': u'Portal Padrão Vídeo',
            'video': self.video['path']
        })

        title = mapping.values()[0].title
        self.assertEqual(title, u'Portal Padrão Vídeo')

        show_header = mapping.values()[0].show_header
        self.assertEqual(show_header, True)

        header = mapping.values()[0].header
        self.assertEqual(header, u'Portal Padrão Vídeo')

        video = mapping.values()[0].video
        self.assertEqual(video, self.video['path'])

    def test_renderer(self):
        r = self._assigned_renderer(self.video)

        self.assertIsInstance(r, video.Renderer)

    def test_renderer_cssclass(self):
        r1 = self._assigned_renderer(self.video)

        self.assertEqual(r1.css_class(),
                         'brasil-gov-portlets-video-portal-padrao-video')

    def test_renderer_video(self):
        r = self._assigned_renderer(self.video)

        video = r.video()
        self.assertEqual(video, self.video['object'])
