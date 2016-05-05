# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import TestCase
from mock import patch, DEFAULT, Mock, MagicMock, call

from . import DataTestCase

from rattail.db import changes
from rattail.db import model
from sqlalchemy.orm import RelationshipProperty


class TestChangeRecorder(TestCase):

    def test_init(self):
        recorder = changes.ChangeRecorder()
        self.assertTrue(recorder.ignore_role_changes)
        recorder = changes.ChangeRecorder(False)
        self.assertFalse(recorder.ignore_role_changes)

    # def test_record_change(self):
    #     session = Mock()
    #     recorder = changes.ChangeRecorder()
    #     recorder.ensure_uuid = Mock()

    #     # don't record changes for changes
    #     self.assertFalse(recorder.record_change(session, model.Change()))

    #     # don't record changes for batch data
    #     self.assertFalse(recorder.record_change(session, model.Batch()))
    #     self.assertFalse(recorder.record_change(session, model.BatchColumn()))
    #     self.assertFalse(recorder.record_change(session, model.BatchRow()))

    #     # don't record changes for objects with no uuid attribute
    #     self.assertFalse(recorder.record_change(session, object()))

    #     # don't record changes for role data if so configured
    #     recorder.ignore_role_changes = True
    #     self.assertFalse(recorder.record_change(session, model.Role()))
    #     self.assertFalse(recorder.record_change(session, model.UserRole()))

    #     # none of the above should have involved a call to `ensure_uuid()`
    #     self.assertFalse(recorder.ensure_uuid.called)

    #     # make sure role data is *not* ignored if so configured
    #     recorder.ignore_role_changes = False
    #     self.assertTrue(recorder.record_change(session, model.Role()))
    #     self.assertTrue(recorder.record_change(session, model.UserRole()))

    #     # so far no *new* changes have been created
    #     self.assertFalse(session.add.called)

    #     # mock up session to force new change creation
    #     session.query.return_value = session
    #     session.get.return_value = None
    #     self.assertTrue(recorder.record_change(session, model.Product()))

    @patch.multiple('rattail.db.changes', get_uuid=DEFAULT, object_mapper=DEFAULT)
    def test_ensure_uuid(self, get_uuid, object_mapper):
        recorder = changes.ChangeRecorder()
        uuid_column = Mock()
        object_mapper.return_value.columns.__getitem__.return_value = uuid_column

        # uuid already present
        product = model.Product(uuid='some_uuid')
        recorder.ensure_uuid(product)
        self.assertEqual(product.uuid, 'some_uuid')
        self.assertFalse(get_uuid.called)

        # no uuid yet, auto-generate
        uuid_column.foreign_keys = False
        get_uuid.return_value = 'another_uuid'
        product = model.Product()
        self.assertTrue(product.uuid is None)
        recorder.ensure_uuid(product)
        get_uuid.assert_called_once_with()
        self.assertEqual(product.uuid, 'another_uuid')

        # some heavy mocking for following tests
        uuid_column.foreign_keys = True
        remote_side = MagicMock(key='uuid')
        prop = MagicMock(__class__=RelationshipProperty, key='foreign_thing')
        prop.remote_side.__len__.return_value = 1
        prop.remote_side.__iter__.return_value = [remote_side]
        object_mapper.return_value.iterate_properties.__iter__.return_value = [prop]
        
        # uuid fetched from existing foreign key object
        get_uuid.reset_mock()
        instance = Mock(uuid=None, foreign_thing=Mock(uuid='secondary_uuid'))
        recorder.ensure_uuid(instance)
        self.assertFalse(get_uuid.called)
        self.assertEqual(instance.uuid, 'secondary_uuid')

        # foreign key object doesn't exist; uuid generated as fallback
        get_uuid.return_value = 'fallback_uuid'
        instance = Mock(uuid=None, foreign_thing=None)
        recorder.ensure_uuid(instance)
        get_uuid.assert_called_once_with()
        self.assertEqual(instance.uuid, 'fallback_uuid')


class TestFunctionalChanges(DataTestCase):

    def setUp(self):
        super(TestFunctionalChanges, self).setUp()
        changes.record_changes(self.session)

    def test_add(self):
        product = model.Product()
        self.session.add(product)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 1)
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.instance_uuid, product.uuid)
        self.assertFalse(change.deleted)

    def test_change(self):
        product = model.Product()
        self.session.add(product)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 1)
        self.session.query(model.Change).delete()
        self.assertEqual(self.session.query(model.Change).count(), 0)

        product.description = 'Acme Bricks'
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 1)
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.instance_uuid, product.uuid)
        self.assertFalse(change.deleted)

    def test_delete(self):
        product = model.Product()
        self.session.add(product)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 1)
        self.session.query(model.Change).delete()
        self.assertEqual(self.session.query(model.Change).count(), 0)

        self.session.delete(product)

        self.assertEqual(self.session.query(model.Change).count(), 1)
        change = self.session.query(model.Change).one()
        self.assertEqual(change.class_name, 'Product')
        self.assertEqual(change.instance_uuid, product.uuid)
        self.assertTrue(change.deleted)

    def test_orphan_change(self):
        department = model.Department()
        subdepartment = model.Subdepartment()
        department.subdepartments.append(subdepartment)
        self.session.add(department)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 2)
        change = self.session.query(model.Change).filter_by(class_name='Department').one()
        self.assertFalse(change.deleted)
        change = self.session.query(model.Change).filter_by(class_name='Subdepartment').one()
        self.assertFalse(change.deleted)

        self.session.query(model.Change).delete()
        self.assertEqual(self.session.query(model.Change).count(), 0)

        # Creating an orphaned Subdepartment, which should be recorded as a
        # *change* due to the cascade rules in effect.
        department.subdepartments.remove(subdepartment)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 2)
        change = self.session.query(model.Change).filter_by(class_name='Department').one()
        self.assertFalse(change.deleted)
        change = self.session.query(model.Change).filter_by(class_name='Subdepartment').one()
        self.assertFalse(change.deleted)
        self.assertEqual(self.session.query(model.Subdepartment).count(), 1)
    
    def test_orphan_delete(self):
        customer = model.Customer()
        group = model.CustomerGroup()
        customer.groups.append(group)
        self.session.add(customer)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 3)
        change = self.session.query(model.Change).filter_by(class_name='Customer').one()
        self.assertFalse(change.deleted)
        change = self.session.query(model.Change).filter_by(class_name='CustomerGroup').one()
        self.assertFalse(change.deleted)
        change = self.session.query(model.Change).filter_by(class_name='CustomerGroupAssignment').one()
        self.assertFalse(change.deleted)

        self.session.query(model.Change).delete()
        self.assertEqual(self.session.query(model.Change).count(), 0)

        # Creating an orphaned CustomerGroupAssociation, which should be
        # recorded as a *deletion* due to the cascade rules in effect.  Note
        # that the CustomerGroup is not technically an orphan and in fact is
        # not even changed.
        customer.groups.remove(group)
        self.session.commit()

        self.assertEqual(self.session.query(model.Change).count(), 2)
        change = self.session.query(model.Change).filter_by(class_name='Customer').one()
        self.assertFalse(change.deleted)
        change = self.session.query(model.Change).filter_by(class_name='CustomerGroupAssignment').one()
        self.assertTrue(change.deleted)
        self.assertEqual(self.session.query(model.CustomerGroupAssignment).count(), 0)
