# -*- coding: utf-8 -*-
from collective.calltoaction.portlets import calltoactionportlet
from collective.calltoaction.testing import COLLECTIVE_CALLTOACTION_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class PortletTestCase(unittest.TestCase):

    layer = COLLECTIVE_CALLTOACTION_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.folder = api.content.create(
            container=self.portal, type='Folder', title='Folder')


class TestPortlet(PortletTestCase):

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.calltoaction.CallToActionPortlet')
        self.assertEquals(portlet.addview,
                          'collective.calltoaction.CallToActionPortlet')

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        portlet = calltoactionportlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.calltoaction.CallToActionPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # TODO: Pass a dictionary containing dummy form inputs from the add
        # form.
        # Note: if the portlet has a NullAddForm, simply call
        # addview() instead of the next line.
        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   calltoactionportlet.Assignment))

    def test_invoke_add_view_fails_in_dashboard(self):
        portlet = getUtility(
            IPortletType,
            name='collective.calltoaction.CallToActionPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.dashboard1')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # Adding is not allowed in the dashboard, only on left and right.
        self.assertRaises(ValueError, addview.createAndAdd, data={})

        self.assertEquals(len(mapping), 0)

    def test_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = calltoactionportlet.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, calltoactionportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        # TODO: Pass any keyword arguments to the Assignment constructor
        assignment = calltoactionportlet.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, calltoactionportlet.Renderer))


class TestRenderer(PortletTestCase):

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        # TODO: Pass any default keyword arguments to the Assignment
        # constructor.
        assignment = assignment or calltoactionportlet.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_render(self):
        r = self.renderer(
            context=self.portal,
            assignment=calltoactionportlet.Assignment(
                header='My overlay header',
                text='My overlay text',
                milli_seconds_until_overlay=1000,
            ))
        r = r.__of__(self.folder)
        r.update()
        # The portlet is not available, because we do not want to render it in
        # a portlet column.
        self.assertFalse(r.available)
        # But the viewlet renders it.
        output = r.render()
        # css class
        self.assertIn('portletCallToAction', output)
        # fields
        self.assertIn('My overlay header', output)
        self.assertIn('My overlay text', output)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
