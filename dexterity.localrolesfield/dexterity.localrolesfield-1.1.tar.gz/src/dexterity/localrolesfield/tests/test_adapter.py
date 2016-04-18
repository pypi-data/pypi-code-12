# encoding: utf-8

from persistent.mapping import PersistentMapping
import unittest

from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import logout

from dexterity.localrolesfield import testing
from dexterity.localrolesfield.adapter import LocalRoleFieldAdapter
from dexterity.localroles.utils import add_fti_configuration


class TestAdapter(unittest.TestCase):
    layer = testing.LOCALROLESFIELD_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.item = api.content.create(container=self.portal,
                                       type='testingtype',
                                       id='testlocalroles',
                                       title='TestLocalRoles',
                                       localrole_field=[u'mail'],
                                       localrole_user_field=[u'john',
                                                             u'kate'],
                                       mono_localrole_field=u'john')
        field_config = {
            u'private': {
                'editor': {'roles': ('Editor', 'Reader')},
                'reviewer': {'roles': ('Contributor', 'Reader')},
            },
            u'published': {
                'editor': {'roles': ('Reader', )},
                'reviewer': {'roles': ('Editor', 'Contributor', 'Reader')},
            },
        }

        userfield_config = {
            u'private': {
                None: {'roles': ('Reader', )},
            },
            u'published': {
                None: {'roles': ('Editor', )},
            },
        }

        global_config = {
            u'private': {
                'kate': {'roles': ('Editor', )},
            },
        }

        behavior_field_config = {
            u'private': {
                None: {'roles': ('Reviewer', )},
            },
        }

        add_fti_configuration('testingtype', global_config, keyname='static_config')
        add_fti_configuration('testingtype', field_config, keyname='localrole_field')
        add_fti_configuration('testingtype', userfield_config, keyname='localrole_user_field')
        add_fti_configuration('testingtype', behavior_field_config, keyname='mono_localrole_field')

    def tearDown(self):
        api.content.delete(obj=self.item)
        setattr(self.test_fti, 'localroles', PersistentMapping())
        logout()

    @property
    def test_fti(self):
        return self.portal.portal_types.get('testingtype')

    @property
    def _adapter(self):
        return LocalRoleFieldAdapter(self.item)

    def _check_roles(self, expected_roles):
        roles = self._adapter.getAllRoles()
        self.assertItemsEqual(expected_roles, [r for r in roles])

    def test_getRoles_private(self):
        adapter = self._adapter
        self.assertEqual('private', api.content.get_state(obj=self.item))
        # Users
        self.assertEqual((), adapter.getRoles('foo'))
        self.assertEqual(('Reader', 'Reviewer'), adapter.getRoles('john'))
        self.assertEqual((), adapter.getRoles('jane'))
        self.assertEqual((), adapter.getRoles('tom'))
        self.assertEqual(('Reader',), adapter.getRoles('kate'))

        # Groups
        self.assertEqual((), adapter.getRoles('support_editor'))
        self.assertEqual((), adapter.getRoles('support_reviewer'))
        self.assertEqual(('Editor', 'Reader'),
                         adapter.getRoles('mail_editor'))
        self.assertEqual(('Contributor', 'Reader'),
                         adapter.getRoles('mail_reviewer'))

    def test_getRoles_published(self):
        adapter = self._adapter
        api.content.transition(obj=self.item, transition='publish')
        self.assertEqual('published', api.content.get_state(obj=self.item))
        # Users
        self.assertEqual((), adapter.getRoles('foo'))
        self.assertEqual(('Editor', ), adapter.getRoles('john'))
        self.assertEqual((), adapter.getRoles('jane'))
        self.assertEqual((), adapter.getRoles('tom'))
        self.assertEqual(('Editor', ), adapter.getRoles('kate'))

        # Groups
        self.assertEqual((), adapter.getRoles('support_editor'))
        self.assertEqual((), adapter.getRoles('support_reviewer'))
        self.assertEqual(('Reader', ),
                         adapter.getRoles('mail_editor'))
        self.assertEqual(('Editor', 'Contributor', 'Reader'),
                         adapter.getRoles('mail_reviewer'))

    def test_getAllRoles_private(self):
        self.assertEqual('private', api.content.get_state(obj=self.item))
        roles = [(u'john', ('Reader', )),
                 (u'john', ('Reviewer', )),
                 (u'kate', ('Reader', )),
                 (u'mail_reviewer', ('Contributor', 'Reader')),
                 (u'mail_editor', ('Editor', 'Reader'))]
        self._check_roles(roles)

    def test_getAllRoles_published(self):
        api.content.transition(obj=self.item, transition='publish')
        self.assertEqual('published', api.content.get_state(obj=self.item))
        roles = [(u'john', ('Editor', )),
                 (u'kate', ('Editor', )),
                 (u'mail_reviewer', ('Editor', 'Contributor', 'Reader')),
                 (u'mail_editor', ('Reader', ))]
        self._check_roles(roles)

    def test_field_and_values_list(self):
        field_values = [
            ('localrole_field', u'mail'),
            ('localrole_user_field', u'john'),
            ('localrole_user_field', u'kate'),
            ('mono_localrole_field', u'john')
        ]
        self.assertItemsEqual(
            field_values,
            self._adapter.field_and_values_list)

    def test_format_suffix(self):
        adapter = self._adapter
        self.assertEqual(u'', adapter._format_suffix(None))
        self.assertEqual(u'_foo', adapter._format_suffix('foo'))

    def test_format_principal(self):
        adapter = self._adapter
        self.assertEqual('foo', adapter._format_principal('foo', None))
        self.assertEqual('foo_bar', adapter._format_principal('foo', 'bar'))
