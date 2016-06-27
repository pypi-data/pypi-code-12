from pylib.misc import dictutils


def test_remove_nones():
    obj = dict(id=12, name=None)
    assert len(dictutils.remove_nones(obj)) == 1
    assert 'id' in obj


def test_merge_dict():
    one, two = dict(id=1), dict(name='Arewa')
    three = dictutils.merge_dict(one, two)
    assert one != three
    assert two != three
    assert len(three) == 2


def test_dict_items():
    obj = dict(id=2, name='Arewa')
    items = dictutils.dict_items(obj)
    assert isinstance(items[0], tuple)
