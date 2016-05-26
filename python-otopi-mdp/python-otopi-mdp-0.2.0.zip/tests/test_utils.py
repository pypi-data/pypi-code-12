import pytest
from otopimdp.utils import split_valid_options


DATA = [
    ('', []),
    ('one', ['one']),
    ('one|two|three', ['one', 'two', 'three']),
    ('hello\\|aa|ksjbdkjd|jsbkds', ['hello|aa', 'ksjbdkjd', 'jsbkds']),
    ('\\\\|\\\\|\\|', ['\\', '\\', '|']),
]


@pytest.mark.parametrize("string,expected_options", DATA)
def test_split_function(string, expected_options):
    options = split_valid_options(string)
    assert options == expected_options


def test_negative_case():
    with pytest.raises(ValueError) as ex:
        split_valid_options("abc\\def|foobar")
    assert "Unescaped" in str(ex.value)
