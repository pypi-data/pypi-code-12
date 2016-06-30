import pytest

from charticle import venn


def test_non_negative():
    with pytest.raises(ValueError) as val:
        venn.Venn3.Sizes(a=-0.1)
    assert 'is negative' in str(val.value)


def test_zero_to_one():
    with pytest.raises(ValueError) as val:
        venn.Venn3.Palette(alpha=50)
    assert 'outside of [0,1] interval' in str(val.value)


def test_positive_int():
    with pytest.raises(ValueError) as val:
        venn.FontSizes(title=0)
    assert 'not positive' in str(val.value)


def test_legal_color():
    with pytest.raises(ValueError) as val:
        venn.Venn3.Palette(a="carpaccioid")
    assert 'not a legal color' in str(val.value)
