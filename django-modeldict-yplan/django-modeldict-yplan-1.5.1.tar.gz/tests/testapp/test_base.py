import pytest
from django.test import SimpleTestCase
from modeldict.base import CachedDict


class CachedDictTest(SimpleTestCase):

    def test_setitem_not_implemented(self):
        d = CachedDict()

        with pytest.raises(NotImplementedError):
            d['x'] = 'foo'

    def test_delitem_not_implemented(self):
        d = CachedDict()

        with pytest.raises(NotImplementedError):
            del d['x']
