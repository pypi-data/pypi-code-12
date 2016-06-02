import pytest
import yter


def test_formatter():
    assert yter.formatter("val")(None) == "val"
    assert yter.formatter("{0:3d}")(22) == " 22"
    assert yter.formatter("{it}", it=True)(False) == "True"
    with pytest.raises(IndexError):
        yter.formatter("{1}")("one")



def test_numeric():
    assert yter.numeric("one2three") == ("one", 2, "three")
    assert yter.numeric("one-2three") == ("one", -2, "three")
    assert yter.numeric("1two3") == (1, "two", 3)
    assert yter.numeric("88") == (88,)
    assert yter.numeric("eight-eight") == ("eight-eight",)
    assert yter.numeric("eight-") == ("eight-",)
    assert yter.numeric("-") == ("-",)
    assert yter.numeric("") == ()


def test_getter():
    data = {"name": {"first": "Peter", "last": "Shinners"}, "id": 1234}
    key = yter.getter["name"]["first"]
    assert key(data) == "Peter"
    assert yter.getter.real(1.2) == 1.2
    assert yter.getter("nop") == "nop"
    assert yter.getter.waffle(data) == None
    assert yter.getter["name", "id"](data) == (data["name"], 1234)

    types = [bool, int, float, str]
    results = list(map(yter.getter._(12), types))
    assert results == [True, 12, 12.0, "12"]

    getter = yter.getter.split._("@", 2)
    assert getter("one@two@three@four") == ["one", "two", "three@four"]
