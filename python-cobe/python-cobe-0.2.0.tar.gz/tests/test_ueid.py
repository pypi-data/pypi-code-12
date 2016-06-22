import collections
import hashlib
import unittest.mock

import pytest

import cobe
import cobe.model


class TestUEID:

    def test_wrong_type(self):
        with pytest.raises(cobe.UEIDError):
            cobe.UEID(object())

    @pytest.mark.parametrize('length', [31, 33])
    def test_wrong_length(self, length):
        with pytest.raises(cobe.UEIDError) as exc:
            cobe.UEID('0' * length)
        assert 'length' in str(exc.value)

    def test_invalid_character(self):
        with pytest.raises(cobe.UEIDError) as exc:
            cobe.UEID('g' * 32)
        assert 'invalid character' in str(exc.value)

    @pytest.mark.parametrize('ueid_raw', [
        '0' * 32,
        cobe.UEID('0' * 32),
    ])
    def test_str(self, ueid_raw):
        ueid = cobe.UEID(ueid_raw)
        assert str(ueid) == '00000000000000000000000000000000'

    @pytest.mark.parametrize('ueid_raw', [
        'A' * 32,
        cobe.UEID('A' * 32),
    ])
    def test_normalise_case(self, ueid_raw):
        ueid = cobe.UEID('A' * 32)
        assert str(ueid) == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

    @pytest.mark.parametrize(('ueid_raw_a', 'ueid_raw_b'), [
        ('a' * 32, 'b' * 32),
        (cobe.UEID('a' * 32), cobe.UEID('b' * 32)),
    ])
    def test_hash(self, ueid_raw_a, ueid_raw_b):
        assert {
            cobe.UEID(ueid_raw_a),
            cobe.UEID(ueid_raw_a),
            cobe.UEID(ueid_raw_b),
        } == {
            cobe.UEID('a' * 32),
            cobe.UEID('b' * 32),
        }

    @pytest.mark.parametrize('ueid_raw', [
        'a' * 32,
        cobe.UEID('a' * 32),
    ])
    def test_eq(self, ueid_raw):
        assert cobe.UEID(ueid_raw) == cobe.UEID('a' * 32)

    @pytest.mark.parametrize('ueid_raw', [
        'a' * 32,
        cobe.UEID('a' * 32),
    ])
    def test_eq_uncomparable(self, ueid_raw):
        assert cobe.UEID(ueid_raw) != 'a' * 32

    @pytest.mark.parametrize('ueid_raw', [
        'a' * 32,
        cobe.UEID('a' * 32),
    ])
    def test_neq(self, ueid_raw):
        assert cobe.UEID(ueid_raw) != cobe.UEID('b' * 32)


class TestFromAttributes:

    @pytest.fixture()
    def _encode_array(self, monkeypatch):
        _encode_array = unittest.mock.Mock(return_value=b'\x00' * 16)
        monkeypatch.setattr(cobe.UEID, '_encode_array', _encode_array)
        return _encode_array

    def test(self, _encode_array):
        # TODO: Don't mock _encode_array
        attributes = cobe.model.Attributes()
        attributes['foo'].set('spam')
        attributes['bar'].set('eggs')
        attributes['foo'].traits.add('entity:id')
        attributes['bar'].traits.add('entity:id')
        ueid = cobe.UEID.from_attributes('Foo', attributes)
        assert isinstance(ueid, cobe.UEID)
        assert _encode_array.call_args == ((['Foo', {
            'foo': 'spam',
            'bar': 'eggs',
        }],), {})
        assert str(ueid) == '00000000000000000000000000000000'

    def test_type_wrong_type(self):
        with pytest.raises(cobe.UEIDError) as exc:
            cobe.UEID.from_attributes(object(), cobe.model.Attributes())
        assert 'entity type' in str(exc.value)

    def test_attributes_wrong_type(self):
        with pytest.raises(cobe.UEIDError) as exc:
            cobe.UEID.from_attributes('Foo', object())
        assert 'attributes' in str(exc.value)

    def test_attribute_unencodable(self):
        attributes = cobe.model.Attributes()
        attributes['foo'].set(object())
        attributes['foo'].traits.add('entity:id')
        with pytest.raises(cobe.UEIDError) as exc:
            cobe.UEID.from_attributes('Foo', attributes)
        assert isinstance(exc.value.__context__, TypeError)

    def test_attribute_ignore_not_set(self, _encode_array):
        attributes = cobe.model.Attributes()
        attributes['foo'].set(...)
        attributes['foo'].traits.add('entity:id')
        attributes['bar'].unset()
        attributes['bar'].traits.add('entity:id')
        ueid = cobe.UEID.from_attributes('Foo', attributes)
        assert isinstance(ueid, cobe.UEID)
        assert _encode_array.call_args == ((['Foo', {'foo': ...}],), {})

    def test_attribute_ignore_deleted(self, _encode_array):
        attributes = cobe.model.Attributes()
        attributes['foo'].set(...)
        attributes['foo'].traits.add('entity:id')
        attributes['bar'].delete()
        attributes['bar'].traits.add('entity:id')
        ueid = cobe.UEID.from_attributes('Foo', attributes)
        assert isinstance(ueid, cobe.UEID)
        assert _encode_array.call_args == ((['Foo', {'foo': ...}],), {})

    def test_attribute_ignore_non_identifying(self, _encode_array):
        attributes = cobe.model.Attributes()
        attributes['foo'].set(...)
        attributes['foo'].traits.add('entity:id')
        attributes['bar'].set(...)
        attributes['bar'].traits = set()
        ueid = cobe.UEID.from_attributes('Foo', attributes)
        assert isinstance(ueid, cobe.UEID)
        assert _encode_array.call_args == ((['Foo', {'foo': ...}],), {})


class TestEncodeValue:

    @pytest.mark.parametrize(('value', 'identifier', 'expected'), [
        (None, b'\x00', b''),
        (False, b'\x01', b'\x00'),
        (0, b'\x02', b'\x43+0.' + (b'0' * 64)),
        (0.0, b'\x02', b'\x43+0.' + (b'0' * 64)),
        ('', b'\x04', b'\x00'),
        (b'', b'\x08', b'\x00'),
        ({}, b'\x10', hashlib.md5().digest()),
        ([], b'\x20', hashlib.md5().digest()),
        (cobe.UEID('a' * 32), b'\x04', b'\x20' + (b'\x61' * 32))
    ])
    def test(self, value, identifier, expected):
        encoded = cobe.UEID._encode_value(value)
        assert bytes([encoded[0]]) == identifier
        assert encoded[1:] == expected

    def test_unencodable(self):
        with pytest.raises(TypeError):
            cobe.UEID._encode_value(object())


class TestEncodeNil:

    def test(self):
        assert cobe.UEID._encode_nil(None) == b''


class TestEncodeBoolean:

    def test_false(self):
        assert cobe.UEID._encode_bool(False) == b'\x00'

    def test_true(self):
        assert cobe.UEID._encode_bool(True) == b'\x01'


class TestEncodeNumber:

    def test_int(self):
        assert cobe.UEID._encode_number(50) == (
            b'\x44' +  # 1 sign + 2 integer part + 1 point + 64 fractional part
            b'+50.00000000000000' +
            b'00000000000000000000000000000000000000000000000000'
        )

    def test_float(self):
        assert cobe.UEID._encode_number(50.1) == (
            b'\x44' +
            b'+50.10000000000000' +
            b'14210854715202003717422485351562500000000000000000'
        )

    def test_positive_zero(self):
        assert cobe.UEID._encode_number(+0.0) == (
            b'\x43' +
            b'+0.00000000000000' +
            b'00000000000000000000000000000000000000000000000000'
        )

    def test_negative_zero(self):
        assert cobe.UEID._encode_number(-0.0) == (
            b'\x43' +
            b'-0.00000000000000' +
            b'00000000000000000000000000000000000000000000000000'
        )

    def test_positive_infinity(self):
        assert cobe.UEID._encode_number(
            +float('inf')) == b'\x09' + b'+Infinity'

    def test_negative_infinity(self):
        assert cobe.UEID._encode_number(
            -float('inf')) == b'\x09' + b'-Infinity'

    def test_positive_nan(self):
        assert cobe.UEID._encode_number(
            +float('nan')) == b'\x04' + b'+NaN'

    def test_negative_nan(self):
        assert cobe.UEID._encode_number(
            -float('nan')) == b'\x04' + b'+NaN'


class TestEncodeUnicode:

    def test_empty(self):
        assert cobe.UEID._encode_unicode('') == b'\x00'

    def test_short(self):
        assert cobe.UEID._encode_unicode('qux') == \
            b'\x03' + b'\x71\x75\x78'

    def test_long(self):
        assert cobe.UEID._encode_unicode(' ' * 256) == \
            b'\x01\x00' + (b'\x20' * 256)

    def test_null(self):
        assert cobe.UEID._encode_unicode('\u0000') == b'\x01' + b'\x00'

    def test_non_ascii(self):
        assert cobe.UEID._encode_unicode('Катюша') == \
            b'\x0C' + b'\xd0\x9a\xd0\xb0\xd1\x82\xd1\x8e\xd1\x88\xd0\xb0'


class TestEncodeBytes:

    def test_empty(self):
        assert cobe.UEID._encode_bytes(b'') == b'\x00'

    def test_short(self):
        assert cobe.UEID._encode_bytes(
            b'\x01\x02\x03') == b'\x03' + b'\x01\x02\x03'

    def test_long(self):
        assert cobe.UEID._encode_bytes(
            b'\xFF' * 256) == b'\x01\x00' + (b'\xFF' * 256)


class TestEncodeMapping:

    def test(self):
        unordered = collections.OrderedDict([
            (b'\x03', b'\x00'),  # 3rd
            (b'\x01', b'\x00'),  # 1st
            (b'\x02', b'\x00'),  # 2nd
        ])
        assert cobe.UEID._encode_mapping(unordered) == hashlib.md5(
            cobe.UEID._encode_value(b'\x01') +  # 1st key
            cobe.UEID._encode_value(b'\x00') +  # 1st value
            cobe.UEID._encode_value(b'\x02') +  # 2nd key
            cobe.UEID._encode_value(b'\x00') +  # 2nd value
            cobe.UEID._encode_value(b'\x03') +  # 3rd key
            cobe.UEID._encode_value(b'\x00')    # 3rd value
        ).digest()

    def test_empty(self):
        assert cobe.UEID._encode_mapping({}) == hashlib.md5().digest()


class TestEncodeArray:

    def test(self):
        array = [b'\x00', b'\x00', b'\x00']
        assert cobe.UEID._encode_array(array) == hashlib.md5(
            cobe.UEID._encode_value(0) +        # 1st index
            cobe.UEID._encode_value(b'\x00') +  # 1st value
            cobe.UEID._encode_value(1) +        # 2nd index
            cobe.UEID._encode_value(b'\x00') +  # 2nd value
            cobe.UEID._encode_value(2) +        # 3rd index
            cobe.UEID._encode_value(b'\x00')    # 3rd value
        ).digest()

    def test_empty(self):
        assert cobe.UEID._encode_array([]) == hashlib.md5().digest()


class TestEncodeInteger:

    def test(self):
        assert cobe.UEID._encode_integer(10) == b'\x0A'

    def test_exact_fit(self):
        assert cobe.UEID._encode_integer(65535) == b'\xFF\xFF'

    def test_zero(self):
        assert cobe.UEID._encode_integer(0) == b'\x00'

    def test_big_endian(self):
        assert cobe.UEID._encode_integer(256) == b'\x01\x00'
