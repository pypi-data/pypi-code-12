import unittest

import pytest

import cobe
import cobe.model


class TestModel:

    def test_add_update(self):
        model = cobe.Model()
        update = cobe.Update('Foo')
        model.add(update)
        entities = list(model)
        assert len(entities) == 1
        assert entities[0][0] is update
        assert entities[0][1] == ()
        assert entities[0][2] == ()
        model.validate()  # Does not raise

    @pytest.mark.parametrize('foreign', [
        cobe.Identifier('Foo'),
        cobe.UEID('a' * 32),
    ])
    def test_add_identifier(self, foreign):
        model = cobe.Model()
        model.add(foreign)
        entities = list(model)
        assert len(model) == 0
        assert len(entities) == 0
        model.validate()  # Does not raise

    def test_add_wrong_type(self):
        model = cobe.Model()
        model.add(object())
        with pytest.raises(cobe.ModelError):
            model.validate()

    def test_add_same_ueid(self):
        model = cobe.Model()
        model.add(cobe.Update('Foo'))
        model.add(cobe.Update('Foo'))
        with pytest.raises(cobe.ModelError):
            model.validate()

    def test_add_redundant(self):
        model = cobe.Model()
        update_1 = cobe.Update('Foo')
        update_2 = cobe.Update('Bar')
        model.relate(parent=update_1, child=update_2)
        model.add(update_1)
        model.add(update_2)
        entities = list(model)
        assert len(entities) == 2
        assert entities[0][0] == update_1
        assert entities[0][1] == ()
        assert entities[0][2] == (update_2,)
        assert entities[1][0] == update_2
        assert entities[1][1] == (update_1,)
        assert entities[1][2] == ()
        model.validate()  # Does not raise

    def test_relate_local_to_local(self):
        model = cobe.Model()
        local_1 = cobe.Update('Foo1')  # Both updates, so need unique UEIDs
        local_2 = cobe.Update('Foo2')
        model.relate(parent=local_1, child=local_2)
        entities = list(model)
        assert len(entities) == 2
        assert entities[0][0] is local_1
        assert entities[0][1] == ()
        assert entities[0][2] == (local_2,)
        assert entities[1][0] is local_2
        assert entities[1][1] == (local_1,)
        assert entities[1][2] == ()
        model.validate()  # Does not raise

    @pytest.mark.parametrize('foreign', [
        cobe.Identifier('Foo'),
        cobe.UEID('a' * 32),
    ])
    def test_relate_local_to_foreign(self, foreign):
        model = cobe.Model()
        local = cobe.Update('Foo')
        model.relate(parent=local, child=foreign)
        entities = list(model)
        assert len(entities) == 1
        assert entities[0][0] is local
        assert entities[0][1] == ()
        assert entities[0][2] == (foreign,)
        model.validate()  # Does not raise

    @pytest.mark.parametrize('foreign', [
        cobe.Identifier('Foo'),
        cobe.UEID('a' * 32),
    ])
    def test_relate_foreign_to_local(self, foreign):
        model = cobe.Model()
        local = cobe.Update('Foo')
        model.relate(parent=foreign, child=local)
        entities = list(model)
        assert len(entities) == 1
        assert entities[0][0] is local
        assert entities[0][1] == (foreign,)
        assert entities[0][2] == ()
        model.validate()  # Does not raise

    @pytest.mark.parametrize('foreign', [
        cobe.Identifier('Foo'),
        cobe.UEID('a' * 32),
    ])
    def test_relate_foreign_to_foreign(self, foreign):
        model = cobe.Model()
        model.relate(parent=foreign, child=foreign)
        entities = list(model)
        assert len(entities) == 0
        with pytest.raises(cobe.ModelError):
            model.validate()

    def test_iter_no_relationships(self):
        model = cobe.Model()
        update_1 = cobe.Update('Foo1')
        update_2 = cobe.Update('Foo2')
        update_3 = cobe.Update('Foo3')
        model.add(update_1)
        model.relate(parent=update_2, child=update_3)
        entities = list(model)
        assert len(entities) == 3
        assert entities[0][0] is update_1
        assert entities[0][1] == ()
        assert entities[0][2] == ()
        assert entities[1][0] is update_2
        assert entities[1][1] == ()
        assert entities[1][2] == (update_3,)
        assert entities[2][0] is update_3
        assert entities[2][1] == (update_2,)
        assert entities[2][2] == ()
        model.validate()  # Does not raise

    def test_iter_order(self):
        model = cobe.Model()
        update_1 = cobe.Update('Foo1')
        update_2 = cobe.Update('Foo2')
        update_3 = cobe.Update('Foo3')
        update_4 = cobe.Update('Foo4')
        update_5 = cobe.Update('Foo5')
        update_1.timestamp = None  # Addition order after explicit
        update_2.timestamp = 1
        update_3.timestamp = 0
        update_4.timestamp = 1
        update_5.timestamp = None  # Addition order after explicit
        model.add(update_1)
        model.add(update_2)
        model.add(update_3)
        model.add(update_4)  # Add after update_2
        model.add(update_5)  # Add after update_1
        entities = [entity for entity, _, _ in model]
        assert entities[0] is update_3
        assert entities[1] is update_2
        assert entities[2] is update_4
        assert entities[3] is update_1
        assert entities[4] is update_5
        model.validate()  # Does not raise

    def test_iter_ignore_duplicate_relationships_updates(self):
        model = cobe.Model()
        update_1 = cobe.Update('Foo')
        update_2 = cobe.Update('Bar')
        update_3 = cobe.Update('Bar')
        model.relate(parent=update_1, child=update_2)
        model.relate(parent=update_1, child=update_3)
        entities = list(model)
        assert len(entities) == 3
        entity_1, parents_1, children_1 = entities[0]
        entity_2, parents_2, children_2 = entities[1]
        entity_3, parents_3, children_3 = entities[2]
        assert entity_1 is update_1
        assert len(parents_1) == 0
        assert len(children_1) == 1
        assert children_1 == (update_2,)
        assert children_1 == (update_3,)  # Equivalent to above
        assert entity_2 is update_2
        assert len(parents_2) == 1
        assert len(children_2) == 0
        assert parents_2 == (update_1,)
        assert entity_3 is update_3
        assert len(parents_3) == 1
        assert len(children_3) == 0
        assert parents_3 == (update_1,)
        with pytest.raises(cobe.ModelError):
            model.validate()

    @pytest.mark.parametrize(('foreign_1', 'foreign_2'), [
        (cobe.Identifier('Foo'), cobe.Identifier('Foo')),
        (cobe.UEID('a' * 32), cobe.UEID('a' * 32)),
    ])
    def test_iter_ignore_duplicate_relationships_identifiers(
            self, foreign_1, foreign_2):
        model = cobe.Model()
        update = cobe.Update('Foo')
        model.relate(parent=update, child=foreign_1)
        model.relate(parent=update, child=foreign_2)
        entities = list(model)
        assert len(entities) == 1
        entity, parents, children = entities[0]
        assert entity is update
        assert len(parents) == 0
        assert len(children) == 1
        assert children == (foreign_1,)
        assert children == (foreign_2,)  # Equivalent to above
        model.validate()  # Does not raise

    def test_iter_empty(self):
        model = cobe.Model()
        assert list(model) == []
        model.validate()  # Does not raise


class TestIdentifier:

    def test_attribute(self):
        identifier = cobe.Identifier('Foo')
        identifier['bar'] = 'baz'
        assert identifier['bar'] == 'baz'
        del identifier['bar']
        with pytest.raises(KeyError):
            identifier['bar']

    def test_len(self):
        identifier = cobe.Identifier('Foo')
        identifier['bar'] = 'baz'
        assert len(identifier) == 1
        identifier['spam'] = 'eggs'
        assert len(identifier) == 2

    def test_iter(self):
        identifier = cobe.Identifier('Foo')
        identifier['bar'] = 'baz'
        identifier['spam'] = 'eggs'
        assert set(identifier) == {'bar', 'spam'}

    def test_ueid(self):
        identifier = cobe.Identifier('Foo')
        identifier['foo'] = 'spam'
        identifier['bar'] = 'eggs'
        ueid = identifier.ueid()
        assert isinstance(ueid, cobe.UEID)
        assert str(ueid) == '802e3d14b8877b7ce352f213f2c6aa46'

    def test_eq_identifier(self):
        identifier_1 = cobe.Identifier('Foo')
        identifier_1['spam'] = 'eggs'
        identifier_2 = cobe.Identifier('Foo')
        identifier_2['spam'] = 'eggs'
        assert identifier_1 == identifier_2

    def test_neq_wrong_type(self):
        assert cobe.Identifier('Foo') != object()

    def test_neq_identifier_different_type(self):
        identifier_1 = cobe.Identifier('Foo')
        identifier_1['spam'] = 'eggs'
        identifier_2 = cobe.Identifier('Bar')
        identifier_2['spam'] = 'eggs'
        assert identifier_1 != identifier_2

    def test_neq_identifier_different_attribute_names(self):
        identifier_1 = cobe.Identifier('Foo')
        identifier_1['spam'] = 'eggs'
        identifier_2 = cobe.Identifier('Foo')
        identifier_2['baz'] = 'eggs'
        assert identifier_1 != identifier_2

    def test_neq_identifier_different_attribute_values(self):
        identifier_1 = cobe.Identifier('Foo')
        identifier_1['spam'] = 'eggs'
        identifier_2 = cobe.Identifier('Foo')
        identifier_2['spam'] = 'baz'
        assert identifier_1 != identifier_2

    def test_eq_ueid(self):
        identifier = cobe.Identifier('Foo')
        identifier['spam'] = 'eggs'
        attributes = cobe.model.Attributes()
        attributes['spam'].set('eggs')
        attributes['spam'].traits.add('entity:id')
        ueid = cobe.UEID.from_attributes('Foo', attributes)
        assert identifier == ueid

    def test_neq_ueid_different_type(self):
        identifier = cobe.Identifier('Foo')
        identifier['spam'] = 'eggs'
        attributes = cobe.model.Attributes()
        attributes['spam'].set('eggs')
        attributes['spam'].traits.add('entity:id')
        ueid = cobe.UEID.from_attributes('Bar', attributes)
        assert identifier != ueid

    def test_neq_ueid_different_attribute_names(self):
        identifier = cobe.Identifier('Foo')
        identifier['spam'] = 'eggs'
        attributes = cobe.model.Attributes()
        attributes['baz'].set('eggs')
        attributes['spam'].traits.add('entity:id')
        ueid = cobe.UEID.from_attributes('Bar', attributes)
        assert identifier != ueid

    def test_neq_ueid_different_attribute_values(self):
        identifier = cobe.Identifier('Foo')
        identifier['spam'] = 'eggs'
        attributes = cobe.model.Attributes()
        attributes['spam'].set('baz')
        attributes['spam'].traits.add('entity:id')
        ueid = cobe.UEID.from_attributes('Bar', attributes)
        assert identifier != ueid

    def test_neq_ueid_error(self, monkeypatch):
        identifier = cobe.Identifier('Foo')
        identifier['spam'] = 'eggs'
        attributes = cobe.model.Attributes()
        attributes['spam'].set('eggs')
        attributes['spam'].traits.add('entity:id')
        ueid = cobe.UEID.from_attributes('Foo', attributes)
        monkeypatch.setattr(
            identifier,
            'ueid',
            unittest.mock.Mock(side_effect=cobe.UEIDError),
        )
        assert identifier != ueid


class TestAttributes:

    def test_len(self):
        attributes = cobe.model.Attributes()
        attributes['foo'].set('foo')
        attributes['bar'].delete()
        attributes['baz'].unset()
        assert len(attributes) == 2

    def test_iter(self):
        attributes = cobe.model.Attributes()
        attributes['foo'].set('foo')
        attributes['bar'].delete()
        attributes['baz'].unset()
        keys = list(attributes)
        assert sorted(keys) == ['bar', 'foo']

    def test_getitem(self):
        attributes = cobe.model.Attributes()
        assert attributes['foo'] is attributes['foo']
        assert isinstance(attributes['foo'], cobe.model.Attribute)

    def test_set(self):
        value = 1024
        attributes = cobe.model.Attributes()
        attributes['foo'].set(value)
        assert attributes['foo'].is_set()
        assert not attributes['foo'].is_not_set()
        assert not attributes['foo'].is_deleted()
        assert attributes['foo'].value is value

    def test_unset(self):
        attributes = cobe.model.Attributes()
        attributes['foo'].set(2014)
        attributes['foo'].traits.add('bar')
        assert attributes['foo'].is_set()
        attributes['foo'].unset()
        assert not attributes['foo'].is_set()
        assert attributes['foo'].is_not_set()
        assert not attributes['foo'].is_deleted()
        assert attributes['foo'].value is cobe.model.Attribute.NOT_SET
        assert len(attributes['foo'].traits) == 0

    def test_delete(self):
        attributes = cobe.model.Attributes()
        attributes['foo'].set(1024)
        attributes['foo'].traits.add('bar')
        assert attributes['foo'].is_set()
        attributes['foo'].delete()
        assert not attributes['foo'].is_set()
        assert not attributes['foo'].is_not_set()
        assert attributes['foo'].is_deleted()
        assert attributes['foo'].value is cobe.model.Attribute.DELETE
        assert len(attributes['foo'].traits) == 0

    def test_traits(self):
        attributes = cobe.model.Attributes()
        assert isinstance(attributes['foo'].traits, set)
        assert not attributes['foo'].is_identifier()
        attributes['foo'].traits.add('entity:id')
        assert attributes['foo'].is_identifier()

    def test_neq_wrong_type(self):
        assert cobe.model.Attributes() != object()

    def test_eq_set(self):
        attributes_1 = cobe.model.Attributes()
        attributes_1['foo'].set('bar')
        attributes_1['spam'].set('eggs')
        attributes_2 = cobe.model.Attributes()
        attributes_2['foo'].set('bar')
        attributes_2['spam'].set('eggs')
        assert attributes_1 == attributes_2

    def test_eq_delete(self):
        attributes_1 = cobe.model.Attributes()
        attributes_1['foo'].delete()
        attributes_1['bar'].delete()
        attributes_2 = cobe.model.Attributes()
        attributes_2['foo'].delete()
        attributes_2['bar'].delete()
        assert attributes_1 == attributes_2

    def test_neq_set_different_attribute_names(self):
        attributes_1 = cobe.model.Attributes()
        attributes_1['foo'].set('bar')
        attributes_1['spam'].set('eggs')
        attributes_2 = cobe.model.Attributes()
        attributes_2['foo'].set('bar')
        attributes_2['baz'].set('eggs')
        assert attributes_1 != attributes_2

    def test_neq_set_different_attribute_values(self):
        attributes_1 = cobe.model.Attributes()
        attributes_1['foo'].set('bar')
        attributes_1['spam'].set('eggs')
        attributes_2 = cobe.model.Attributes()
        attributes_2['foo'].set('bar')
        attributes_2['spam'].set('baz')
        assert attributes_1 != attributes_2

    def test_neq_delete_different_names(self):
        attributes_1 = cobe.model.Attributes()
        attributes_1['foo'].delete()
        attributes_1['bar'].delete()
        attributes_2 = cobe.model.Attributes()
        attributes_2['foo'].delete()
        attributes_2['baz'].delete()
        assert attributes_1 != attributes_2


class TestUpdate:

    def test_defaults(self):
        update = cobe.Update('Foo')
        assert update.type == 'Foo'
        assert update.timestamp is None
        assert update.label is None
        assert update.ttl is None
        assert update.exists is True
        assert isinstance(update.attributes, cobe.model.Attributes)

    def test_ueid(self):
        update = cobe.Update('Foo')
        update.attributes['foo'].set('spam')
        update.attributes['foo'].traits.add('entity:id')
        update.attributes['bar'].set('eggs')
        update.attributes['bar'].traits.add('entity:id')
        ueid = update.ueid()
        assert isinstance(ueid, cobe.UEID)
        assert str(ueid) == '802e3d14b8877b7ce352f213f2c6aa46'

    def test_eq(self):
        update_1 = cobe.Update('Foo')
        update_1.timestamp = 123
        update_1.label = 'foo'
        update_1.ttl = 60
        update_1.exists = True
        update_1.attributes['foo'].set('bar')
        update_1.attributes['baz'].delete()
        update_2 = cobe.Update('Foo')
        update_2.timestamp = 123
        update_2.label = 'foo'
        update_2.ttl = 60
        update_2.exists = True
        update_2.attributes['foo'].set('bar')
        update_2.attributes['baz'].delete()
        assert update_1 == update_2

    def test_neq_wrong_type(self):
        assert cobe.Update('Foo') != object()

    def test_neq_different_type(self):
        assert cobe.Update('Foo') != cobe.Update('Bar')

    def test_new_different_timestamp(self):
        update_1 = cobe.Update('Foo')
        update_1.timestamp = 123
        update_2 = cobe.Update('Foo')
        update_1.timestamp = 456
        assert update_1 != update_2

    def test_neq_different_label(self):
        update_1 = cobe.Update('Foo')
        update_1.label = 'foo'
        update_2 = cobe.Update('Foo')
        update_2.label = 'bar'
        assert update_1 != update_2

    def test_neq_different_ttl(self):
        update_1 = cobe.Update('Foo')
        update_1.ttl = 60
        update_2 = cobe.Update('Foo')
        update_2.ttl = 180
        assert update_1 != update_2

    def test_neq_different_exists(self):
        update_1 = cobe.Update('Foo')
        update_1.exists = True
        update_2 = cobe.Update('Foo')
        update_2.exists = False
        assert update_1 != update_2

    def test_neq_different_attributes(self):
        update_1 = cobe.Update('Foo')
        update_1.attributes['foo'].set('bar')
        update_2 = cobe.Update('Foo')
        update_2.attributes['foo'].set('baz')
        assert update_1 != update_2
