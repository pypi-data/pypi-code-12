
from __future__ import unicode_literals
from __future__ import absolute_import

import unittest
import pycountry
import datetime

from .. import ofx


class TestOfxGlobal(unittest.TestCase):

    def test_XMLElement(self):
        name = 'tag'
        content = '12345'

        self.assertEqual('<TAG>12345</TAG>', ofx.XMLElement(name, content))

        content = None

        self.assertEqual('', ofx.XMLElement(name, content))

        content = ''

        self.assertEqual('<TAG></TAG>', ofx.XMLElement(name, content))

        with self.assertRaises(Exception):
            ofx.XMLElement(None, content)

    def test_XMLAggregate(self):
        name = 'tag'
        content = '12345'

        self.assertEqual('<TAG>12345</TAG>', ofx.XMLAggregate(name, content))

        content = None

        self.assertEqual('', ofx.XMLAggregate(name, content))

        content = ''

        self.assertEqual('<TAG></TAG>', ofx.XMLAggregate(name, content))

        with self.assertRaises(Exception):
            ofx.XMLAggregate(None, content)

    def test_SGMLElement(self):
        name = 'tag'
        content = '12345'

        self.assertEqual('<TAG>12345', ofx.SGMLElement(name, content))

        content = None

        self.assertEqual('', ofx.SGMLElement(name, content))

        content = ''

        self.assertEqual('<TAG>', ofx.SGMLElement(name, content))

        with self.assertRaises(Exception):
            ofx.SGMLElement(None, content)

    def test_SGMLAggregate(self):
        name = 'tag'
        content = '12345'

        self.assertEqual('<TAG>12345</TAG>', ofx.SGMLAggregate(name, content))

        content = None

        self.assertEqual('', ofx.SGMLAggregate(name, content))

        content = ''

        self.assertEqual('<TAG></TAG>', ofx.SGMLAggregate(name, content))

        with self.assertRaises(Exception):
            ofx.SGMLAggregate(None, content)

    def test_strText(self):
        value = 'aeiou'

        self.assertEqual(value, ofx.strText(value))

    def test_strText_ampersand(self):
        ivalue = 's&m'
        ovalue = 's&amp;m'

        self.assertEqual(ovalue, ofx.strText(ivalue))

    def test_strText_lt(self):
        ivalue = 's<m'
        ovalue = 's&lt;m'

        self.assertEqual(ovalue, ofx.strText(ivalue))

    def test_strText_gt(self):
        ivalue = 's>m'
        ovalue = 's&gt;m'

        self.assertEqual(ovalue, ofx.strText(ivalue))

    def test_strDate(self):
        value = datetime.date(year=2004, month=3, day=1)

        self.assertEqual('20040301', ofx.strDate(value))

        value = None

        self.assertIsNone(ofx.strDate(value))

        value = 5

        with self.assertRaises(Exception):
            ofx.strDate(value)

    def test_strBool(self):
        value = True

        self.assertEqual('Y', ofx.strBool(value))

        value = False

        self.assertEqual('N', ofx.strBool(value))

        value = None

        self.assertIsNone(ofx.strBool(value))

        value = 5

        self.assertEqual('Y', ofx.strBool(value))

        value = ''

        self.assertEqual('N', ofx.strBool(value))

    def test_strCurrency(self):
        value = pycountry.currencies.get(letter='EUR')

        self.assertEqual('EUR', ofx.strCurrency(value))

        value = None

        self.assertIsNone(ofx.strCurrency(value))

        value = 5

        with self.assertRaises(Exception):
            ofx.strCurrency(value)


class TestOfxObject(unittest.TestCase):

    def test_init(self):

        with self.assertRaises(Exception):
            ofx.OfxObject()

        ofx.OfxObject(None)

        ofx.OfxObject('1234')

        ofx.OfxObject(5)

    def test_tag_name(self):
        value = 'tag1'

        o = ofx.OfxObject(value)

        self.assertEqual(value, o.get_tag_name())

        value = 'tag2'
        o.set_tag_name(value)

        self.assertEqual(value, o.get_tag_name())

    def test_str(self):

        o = ofx.OfxObject('tag')

        self.assertEqual('', str(o))
