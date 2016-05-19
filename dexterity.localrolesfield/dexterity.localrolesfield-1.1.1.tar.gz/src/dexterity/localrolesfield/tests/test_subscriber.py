# -*- coding: utf-8 -*-
import transaction
import unittest
import zope.event
from zope.annotation.interfaces import IAnnotations
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
from plone import api
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID

from dexterity.localroles.browser.settings import LocalRoleConfigurationAdapter
from dexterity.localroles.utils import add_fti_configuration, get_related_roles, rel_key

from ..testing import LOCALROLESFIELD_FUNCTIONAL, ITestingType, ITestingBehavior


class TestSubscriber(unittest.TestCase):

    layer = LOCALROLESFIELD_FUNCTIONAL

    def setUp(self):
        super(TestSubscriber, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        field_config = {
            u'private': {
                'editor': {'roles': ('Editor', 'Reader'), 'rel': "{'dexterity.localroles.related_parent':['Editor']}"},
                'reviewer': {'roles': ('Contributor', 'Reader'), 'rel': "{'dexterity.localroles.related_parent':[]}"},
            },
            u'published': {
                'editor': {'roles': ('Reader', ), 'rel': "{'dexterity.localroles.related_parent':['Reader']}"},
                'reviewer': {'roles': ('Editor', 'Contributor', 'Reader')},
            },
        }
        userfield_config = {
            u'private': {
                None: {'roles': ('Reader', ), 'rel': "{'dexterity.localroles.related_parent':['Reader']}"},
            },
            u'published': {
                None: {'roles': ('Editor', ), 'rel': "{'dexterity.localroles.related_parent':['Editor']}"},
            },
        }
        global_config = {
            u'private': {
                'kate': {'roles': ('Editor', )},
            },
        }
        behavior_field_config = {
            u'private': {
                None: {'roles': ('Reviewer', ), 'rel': "{'dexterity.localroles.related_parent':['Reviewer']}"},
            },
        }
        add_fti_configuration('testingtype', global_config, keyname='static_config')
        add_fti_configuration('testingtype', field_config, keyname='localrole_field')
        add_fti_configuration('testingtype', userfield_config, keyname='localrole_user_field')
        add_fti_configuration('testingtype', behavior_field_config, keyname='mono_localrole_field')

        self.item = api.content.create(container=self.portal, type='testingtype',
                                       id='testlocalroles', title='TestLocalRoles',
                                       localrole_field=[u'mail'],
                                       localrole_user_field=[u'john', u'kate'],
                                       mono_localrole_field=u'john')

    def test_update_security(self):
        doc = api.content.create(container=self.item, type='Document', id='doc', title='Document')
        ctool = self.portal.portal_catalog
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(self.item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertSetEqual(set(['Manager', 'Site Administrator', 'Reader', 'Editor', 'Contributor', 'user:admin',
                                 'user:test_user_1_', 'user:kate', u'user:mail_editor', u'user:mail_reviewer',
                                 u'user:john']), set(allowedRolesAndUsers))
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(doc.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertSetEqual(set(['Manager', 'Site Administrator', 'Reader', 'Editor', 'Contributor', 'user:admin',
                                 'user:test_user_1_', 'user:kate', u'user:mail_editor', u'user:mail_reviewer',
                                 u'user:john']), set(allowedRolesAndUsers))
        self.item.localrole_field = ['support']
        self.item.localrole_user_field = ['jane', 'tom']
        self.item.mono_localrole_field = 'basic-user'
        zope.event.notify(ObjectModifiedEvent(self.item, Attributes(ITestingBehavior,
                                              'ITestingBehavior.mono_localrole_field'), Attributes(ITestingType,
                                              'localrole_field', 'localrole_user_field'), ))
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(self.item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertSetEqual(set(['Manager', 'Site Administrator', 'Reader', 'Editor', 'Contributor', 'user:admin',
                                 'user:test_user_1_', 'user:kate', u'user:support_editor', u'user:support_reviewer',
                                 u'user:jane', u'user:tom']), set(allowedRolesAndUsers))
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(doc.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertSetEqual(set(['Manager', 'Site Administrator', 'Reader', 'Editor', 'Contributor', 'user:admin',
                                 'user:test_user_1_', 'user:kate', u'user:support_editor', u'user:support_reviewer',
                                 u'user:jane', u'user:tom']), set(allowedRolesAndUsers))

    def test_related_change_on_transition(self):
        api.content.transition(obj=self.item, transition='publish')
        self.assertDictEqual(dict(get_related_roles(self.portal, self.item.UID())),
                             {u'mail_editor': set(['Reader']), u'john': set(['Editor']),
                              u'kate': set(['Editor'])})

    def test_related_change_on_addition(self):
        self.assertDictEqual(dict(get_related_roles(self.portal, self.item.UID())),
                             {u'mail_editor': set(['Editor']), u'john': set(['Reviewer', 'Reader']),
                              u'kate': set(['Reader'])})

    def test_related_change_on_removal(self):
        # The parent is set by addition subscriber
        self.assertDictEqual(dict(get_related_roles(self.portal, self.item.UID())),
                             {u'mail_editor': set(['Editor']), u'john': set(['Reviewer', 'Reader']),
                              u'kate': set(['Reader'])})
        api.content.delete(obj=self.item)
        # The parent is changed
        self.assertDictEqual(get_related_roles(self.portal, self.item.UID()), {})

    def test_related_change_on_move(self):
        # We need to commit here so that _p_jar isn't None and move will work
        transaction.savepoint(optimistic=True)
        # The parent is set by addition subscriber
        self.assertDictEqual(dict(get_related_roles(self.portal, self.item.UID())),
                             {u'mail_editor': set(['Editor']), u'john': set(['Reviewer', 'Reader']),
                              u'kate': set(['Reader'])})
        # We create a folder
        self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal['folder']
        self.assertDictEqual(get_related_roles(folder, self.item.UID()), {})
        # We move the item
        api.content.move(source=self.item, target=folder)
        # The old parent is changed
        self.assertDictEqual(get_related_roles(self.portal, self.item.UID()), {})
        # The new parent is changed
        self.assertDictEqual(dict(get_related_roles(folder, self.item.UID())),
                             {u'mail_editor': set(['Editor']), u'john': set(['Reviewer', 'Reader']),
                              u'kate': set(['Reader'])})
        item = folder['testlocalroles']
        api.content.rename(obj=item, new_id='test1')

    def test_local_role_configuration_updated(self):
        class dummy(object):
            def __init__(self, fti):
                self.fti = fti
                self.context = self

        ctool = self.portal.portal_catalog
        fti = self.portal.portal_types.get('testingtype')
        dum = dummy(fti)
        cls = LocalRoleConfigurationAdapter(dum)
        fti.localroles = {}
        api.content.transition(obj=self.item, transition='submit')
        annot = IAnnotations(self.portal)
        del annot[rel_key]
        item1 = api.content.create(container=self.portal, type='testingtype',
                                   id='testlocalroles1', title='TestLocalRoles1',
                                   localrole_field=[u'mail'],
                                   localrole_user_field=[u'john', u'kate'],
                                   mono_localrole_field=u'john')
        # Nothing is set !
        self.assertDictEqual(get_related_roles(self.portal, item1.UID()), {})
        # Adding a state
        setattr(cls, 'static_config',
                [{'state': 'private', 'value': 'jane', 'roles': ('Reader',),
                  'related': "{'dexterity.localroles.related_parent':['Reader']}"}])
        setattr(cls, 'localrole_field',
                [{'state': 'private', 'value': 'editor', 'roles': ('Editor',),
                  'related': "{'dexterity.localroles.related_parent':['Editor']}"}])
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item1.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertIn('user:jane', allowedRolesAndUsers)
        self.assertIn('user:mail_editor', allowedRolesAndUsers)
        self.assertDictEqual(dict(get_related_roles(self.portal, item1.UID())),
                             {'jane': set(['Reader']), 'mail_editor': set(['Editor'])})
        # Removing a state
        setattr(cls, 'static_config',
                [{'state': 'pending', 'value': 'kate', 'roles': ('Reader',),
                  'related': "{'dexterity.localroles.related_parent':['Reader']}"}])
        setattr(cls, 'localrole_field',
                [{'state': 'pending', 'value': 'reviewer', 'roles': ('Reviewer',),
                  'related': "{'dexterity.localroles.related_parent':['Reviewer']}"}])
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(item1.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertNotIn('user:jane', allowedRolesAndUsers)
        self.assertNotIn('user:mail_editor', allowedRolesAndUsers)
        self.assertDictEqual(get_related_roles(self.portal, item1.UID()), {})
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(self.item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertIn('user:kate', allowedRolesAndUsers)
        self.assertIn('user:mail_reviewer', allowedRolesAndUsers)
        self.assertDictEqual(dict(get_related_roles(self.portal, self.item.UID())),
                             {'kate': set(['Reader']), 'mail_reviewer': set(['Reviewer'])})
        # Adding principal
        setattr(cls, 'static_config',
                [{'state': 'pending', 'value': 'kate', 'roles': ('Reader',),
                  'related': "{'dexterity.localroles.related_parent':['Reader']}"},
                 {'state': 'pending', 'value': 'jane', 'roles': ('Reader',),
                  'related': "{'dexterity.localroles.related_parent':['Reader']}"}])
        setattr(cls, 'localrole_field',
                [{'state': 'pending', 'value': 'reviewer', 'roles': ('Reviewer',),
                  'related': "{'dexterity.localroles.related_parent':['Reviewer']}"},
                 {'state': 'pending', 'value': 'editor', 'roles': ('Editor',),
                  'related': "{'dexterity.localroles.related_parent':['Editor']}"}])
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(self.item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertIn('user:kate', allowedRolesAndUsers)
        self.assertIn('user:jane', allowedRolesAndUsers)
        self.assertIn('user:mail_editor', allowedRolesAndUsers)
        self.assertIn('user:mail_reviewer', allowedRolesAndUsers)
        self.assertDictEqual(dict(get_related_roles(self.portal, self.item.UID())),
                             {'kate': set(['Reader']), 'jane': set(['Reader']),
                              'mail_reviewer': set(['Reviewer']), 'mail_editor': set(['Editor'])})
        # Removing principal
        setattr(cls, 'static_config',
                [{'state': 'pending', 'value': 'jane', 'roles': ('Reader',),
                  'related': "{'dexterity.localroles.related_parent':['Reader']}"}])
        setattr(cls, 'localrole_field',
                [{'state': 'pending', 'value': 'editor', 'roles': ('Editor',),
                  'related': "{'dexterity.localroles.related_parent':['Editor']}"}])
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(self.item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertNotIn('user:kate', allowedRolesAndUsers)
        self.assertIn('user:jane', allowedRolesAndUsers)
        self.assertNotIn('user:mail_reviewer', allowedRolesAndUsers)
        self.assertIn('user:mail_editor', allowedRolesAndUsers)
        self.assertDictEqual(dict(get_related_roles(self.portal, self.item.UID())),
                             {'jane': set(['Reader']), 'mail_editor': set(['Editor'])})
        # Removing roles, Adding and removing rel
        setattr(cls, 'static_config',
                [{'state': 'pending', 'value': 'jane', 'roles': (),
                  'related': "{'dexterity.localroles.related_parent':['Reviewer']}"}])
        setattr(cls, 'localrole_field',
                [{'state': 'pending', 'value': 'editor', 'roles': (),
                  'related': "{'dexterity.localroles.related_parent':['Reviewer']}"}])
        allowedRolesAndUsers = ctool.getIndexDataForUID('/'.join(self.item.getPhysicalPath()))['allowedRolesAndUsers']
        self.assertNotIn('user:kate', allowedRolesAndUsers)
        self.assertNotIn('user:jane', allowedRolesAndUsers)
        self.assertNotIn('user:mail_reviewer', allowedRolesAndUsers)
        self.assertNotIn('user:mail_editor', allowedRolesAndUsers)
        self.assertDictEqual(dict(get_related_roles(self.portal, self.item.UID())),
                             {'jane': set(['Reviewer']), 'mail_editor': set(['Reviewer'])})
