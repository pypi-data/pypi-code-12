import mock
import pytest

import bitpack.field as mod


@pytest.fixture
def bit_field():
    return mod.BitField(name='test', index=2, width=42, data_type='int')


def test_field_wrapper():
    cls = mock.Mock()
    args = [1, 2]
    kwargs = {'a': 3, 'b': 4}
    fw = mod.FieldWrapper(cls, args, kwargs)
    assert fw.instantiate('test') == cls.return_value
    cls.assert_called_once_with(index=0, name='test', *args, **kwargs)


def test_bit_field_init_deferred():
    args = (1, 2)
    kwargs = {'a': 3, 'b': 4}
    inst = mod.BitField(*args, **kwargs)
    assert isinstance(inst, mod.FieldWrapper)
    assert inst.cls is mod.BitField
    assert inst.args == args
    assert inst.kwargs == kwargs


def test_bit_field_init_performed(bit_field):
    assert isinstance(bit_field, mod.BitField)
    assert bit_field._name == 'test'
    assert bit_field._index == 2
    assert bit_field._width == 42
    assert bit_field._data_type == 'int'


def test_bit_field_properties(bit_field):
    assert bit_field.name == 'test'
    assert bit_field.width == 42
    assert bit_field.data_type == 'int'


def test_bit_field_deserialize(bit_field):
    test_fn = mock.Mock()
    mod.BitField._deserializers['test'] = test_fn
    inst = mod.BitField(name='test', index=2, width=42, data_type='test')
    assert inst.deserialize(mock.Mock()) == test_fn.return_value


def test_bit_field_deserialize_unknown_type():
    inst = mod.BitField(name='test', index=2, width=42, data_type='invalid')
    with pytest.raises(ValueError):
        inst.deserialize(mock.Mock())


@mock.patch.object(mod, 'bitarray')
def test_bit_field_serialize(bitarray, bit_field):
    test_fn = mock.Mock()
    value = mock.Mock()
    mod.BitField._serializers['test'] = test_fn
    inst = mod.BitField(name='test', index=2, width=42, data_type='test')
    ret = inst.serialize(value)
    assert ret == bitarray.return_value.__getitem__.return_value
    test_fn.assert_called_once_with(value)


def test_bit_field_serialize_unknown_type():
    inst = mod.BitField(name='test', index=2, width=42, data_type='invalid')
    with pytest.raises(ValueError):
        inst.serialize(mock.Mock())


def test_register_data_type():
    serializer = mock.Mock()
    deserializer = mock.Mock()
    mod.BitField.register_data_type('test', serializer, deserializer)
    assert mod.BitField._serializers['test'] is serializer
    assert mod.BitField._deserializers['test'] is deserializer
