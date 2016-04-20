import mock
import pytest

import bitpack.stream as mod


@pytest.fixture
def bit_stream():
    from bitpack.field import BitField

    class AStream(mod.BitStream):
        start_marker = 'HBO'
        end_marker = 'OBH'
        int_fld = BitField(width=2, data_type='integer')
        flt_fld = BitField(width=32, data_type='float')
        str_fld = BitField(width=32, data_type='string')
        hex_fld = BitField(width=32, data_type='hex')
    return AStream


@pytest.mark.parametrize('start,end', [
    (None, None),
    ('HBO', None),
    (None, 'OBH'),
])
def test_init_no_start_marker(start, end):
    class AStream(mod.BitStream):
        start_marker = start
        end_marker = end

    with pytest.raises(TypeError):
        AStream({})


def test_init_unequal_length_markers():
    class AStream(mod.BitStream):
        start_marker = 'HBO'
        end_marker = 'OBHH'

    with pytest.raises(ValueError):
        AStream({})


@mock.patch.object(mod.BitStream, '_collect_fields')
def test_init(_collect_fields):
    class AStream(mod.BitStream):
        start_marker = 'HBO'
        end_marker = 'OBH'
    inst = AStream({})
    _collect_fields.assert_called_once_with()
    inst._fields == _collect_fields.return_value


@mock.patch.object(mod.FieldWrapper, 'instantiate')
def test__collect_fields(instantiate):
    class AStream(mod.BitStream):
        start_marker = 'HBO'
        end_marker = 'OBH'
        fld1 = mod.FieldWrapper(1, 2, 3)
        fld2 = mod.FieldWrapper(1, 2, 3)
        fld3 = mod.FieldWrapper(1, 2, 3)
        fld4 = mod.FieldWrapper(1, 2, 3)
    inst = AStream({})
    inst._fields == [AStream.fld1, AStream.fld2, AStream.fld3, AStream.fld4]
    instantiate.assert_has_calls([mock.call('fld1'),
                                  mock.call('fld2'),
                                  mock.call('fld3'),
                                  mock.call('fld4')])


def test__run_processor():
    pre_x = mock.Mock()
    pre_x.side_effect = lambda x: x + 1
    post_x = mock.Mock()
    post_x.side_effect = lambda x: x - 1

    class AStream(mod.BitStream):
        start_marker = 'HBO'
        end_marker = 'OBH'
        preprocess_x = pre_x
        postprocess_x = post_x
    inst = AStream({})
    assert inst._run_processor('preprocess_', 'x', 11) == 12
    assert inst._run_processor('postprocess_', 'x', 21) == 20
    pre_x.assert_called_once_with(11)
    post_x.assert_called_once_with(21)
    # test nonexistent processor just returns the same value
    assert inst._run_processor('preprocess_', 'missing', 42) == 42


def test_serialize(bit_stream):
    data = [{'int_fld': 2,
             'flt_fld': 2.5,
             'str_fld': 'xyZD',
             'hex_fld': 'abCD'}]
    expected = 'HBO\x90\x08\x00\x00\x1e\x1e\x56\x91\x2a\xf3\x53\xd0\x92\x00'
    inst = bit_stream(data)
    assert inst.serialize() == expected


def test_deserialize(bit_stream):
    expected = [{'int_fld': 2,
                 'flt_fld': 2.5,
                 'str_fld': 'xyZD',
                 'hex_fld': 'abcd'}]
    data = 'HBO\x90\x08\x00\x00\x1e\x1e\x56\x91\x2a\xf3\x53\xd0\x92\x00'
    inst = bit_stream(data)
    assert inst.deserialize() == expected


def test_deserialize_start_marker_mismatch(bit_stream):
    data = 'HBU\x90\x08\x00\x00\x1e\x1e\x56\x91\x2a\xf3\x53\xd0\x92\x00'
    inst = bit_stream(data)
    with pytest.raises(ValueError):
        inst.deserialize()


@mock.patch.object(mod.BitStream, 'deserialize')
def test_from_bytes(deserialize, bit_stream):
    bit_stream.from_bytes('data')
    deserialize.assert_called_once_with()


@mock.patch.object(mod.BitStream, 'serialize')
def test_to_bytes(serialize, bit_stream):
    bit_stream.to_bytes('data')
    serialize.assert_called_once_with()
