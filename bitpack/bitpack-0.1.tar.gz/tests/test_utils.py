import pytest

import bitpack.utils as mod


@pytest.mark.parametrize('fmt,data,exp', [
    ('>i', 1, '\x00\x00\x00\x01'),
    ('>i', 99, '\x00\x00\x00\x63'),
    ('>i', 18543, '\x00\x00\x48\x6f'),
    ('>f', 1.23, '\x3f\x9d\x70\xa4'),
    ('>f', 158.32, '\x43\x1e\x51\xec'),
    ('>f', 85234.32, '\x47\xa6\x79\x29'),
])
def test_pack(fmt, data, exp):
    assert mod.pack(fmt, data) == exp


@pytest.mark.parametrize('fmt,data,exp', [
    ('>i', '\x00\x00\x00\x01', 1),
    ('>i', '\x00\x00\x00\x63', 99),
    ('>i', '\x00\x00\x48\x6f', 18543),
    ('>f', '\x3f\x9d\x70\xa4', 1.23),
    ('>f', '\x43\x1e\x51\xec', 158.32),
    ('>f', '\x47\xa6\x79\x29', 85234.32),
])
def test_unpack(fmt, data, exp):
    assert round(mod.unpack(fmt, data), 2) == exp


@pytest.mark.parametrize('src,exp', [
    ('abcd', '\xab\xcd'),
    ('ABCD', '\xab\xcd'),
    ('a1b2c3d4e5f6', '\xa1\xb2\xc3\xd4\xe5\xf6'),
    ('0987654321', '\x09\x87\x65\x43\x21'),
])
def test_hex_to_bytes(src, exp):
    assert mod.hex_to_bytes(src) == exp


@pytest.mark.parametrize('src', [
    'abc',
    'ABC',
    'a1b2c',
    '0987654',
])
def test_hex_to_bytes_fail(src):
    with pytest.raises(ValueError):
        mod.hex_to_bytes(src)


@pytest.mark.parametrize('src,exp', [
    ('\xab\xcd', 'abcd'),
    ('\xa1\xb2\xc3\xd4\xe5\xf6', 'a1b2c3d4e5f6'),
    ('\x09\x87\x65\x43\x21', '0987654321'),
])
def test_bytes_to_hex(src, exp):
    assert mod.bytes_to_hex(src) == exp
