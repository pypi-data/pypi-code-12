import pytest
from cratis.utils import Collectable, Resolvable


def test_resolvable_abstract_working():
    with pytest.raises(TypeError):
        Resolvable()

    with pytest.raises(TypeError):
        class MyCls(Resolvable):
            pass

        MyCls()

    class MyCls2(Resolvable):
        def resolve(self):
            pass

    MyCls2()


def test_collectable():
    boo = Collectable()

    assert isinstance(boo, Resolvable)

    boo.append('123')
    boo.append(['321'])

    assert boo.resolve() == ('123', '321')

def test_collectable_non_unique_list():
    boo = Collectable(unique=False, _format=list)

    assert isinstance(boo, Resolvable)

    boo.append('123')
    boo.append('321')
    boo.append('321')

    assert boo.resolve() == ['123', '321', '321']

