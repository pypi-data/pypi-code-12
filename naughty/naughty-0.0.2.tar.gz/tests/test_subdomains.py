import pytest

from naughty import subdomains


@pytest.mark.parametrize('words', [
    subdomains.obscene,
    subdomains.phishing,
])
def test_is_a_set(words):
    assert isinstance(words, set)
