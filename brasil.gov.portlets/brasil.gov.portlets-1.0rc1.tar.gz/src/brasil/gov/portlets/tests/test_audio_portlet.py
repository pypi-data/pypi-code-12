# -*- coding: utf-8 -*-
from brasil.gov.portlets.portlets import audio
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


class AudioPortletTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.audio = {}
        self.audio['object'] = self.portal['audios-folder']['audio-1']
        self.audio['path'] = '/' + '/'.join(self.audio['object'].getPhysicalPath()[2:])

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
        assgmnt = audio.Assignment(
            header=u'Portal Padrão Áudio',
            audio=col['path']
        )
        r = self._renderer(context=self.portal,
                           assignment=assgmnt)
        r = r.__of__(self.portal)
        r.update()
        return r

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.audio')
        self.assertEqual(portlet.addview, 'brasil.gov.portlets.audio')

    def test_registered_interfaces(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.audio')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(
            ['plone.app.portlets.interfaces.IColumn',
             'plone.app.portlets.interfaces.IDashboard'],
            registered_interfaces
        )

    def test_interfaces(self):
        portlet = audio.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_addview(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.audio')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], audio.Assignment))

    def test_portlet_properties(self):
        portlet = getUtility(IPortletType, name='brasil.gov.portlets.audio')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={
            'header': u'Portal Padrão Áudio',
            'audio': self.audio['path']
        })

        title = mapping.values()[0].title
        self.assertEqual(title, u'Portal Padrão Áudio')

        header = mapping.values()[0].header
        self.assertEqual(header, u'Portal Padrão Áudio')

        audio = mapping.values()[0].audio
        self.assertEqual(audio, self.audio['path'])

    def test_renderer(self):
        r = self._assigned_renderer(self.audio)

        self.assertIsInstance(r, audio.Renderer)

    def test_renderer_cssclass(self):
        r1 = self._assigned_renderer(self.audio)

        self.assertEqual(r1.css_class(),
                         'brasil-gov-portlets-audio-portal-padrao-audio')

    def test_renderer_audio(self):
        r = self._assigned_renderer(self.audio)

        audio = r.audio()
        self.assertEqual(audio, self.audio['object'])

    def test_renderer_title(self):
        r = self._assigned_renderer(self.audio)

        self.assertEqual(r.title(), 'Audio 1')

    def test_renderer_description(self):
        r = self._assigned_renderer(self.audio)

        self.assertEqual(r.description(),
                         'Audio 1 description - Lorem ipsum dolor sit amet, ' +
                         'consectetur adipiscing elit. Donec eleifend ' +
                         'hendrerit interdum.')

    def test_renderer_rights(self):
        r = self._assigned_renderer(self.audio)

        self.assertEqual(r.rights(), 'Audio rights')

    def test_renderer_url(self):
        r = self._assigned_renderer(self.audio)

        self.assertEqual(r.url(),
                         'http://nohost/plone/audios-folder/audio-1/file.mp3')

    def test_renderer_contenttype(self):
        r = self._assigned_renderer(self.audio)

        self.assertEqual(r.content_type(), u'audio/mp3')
