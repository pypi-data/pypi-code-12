import unittest
import base64

from mauveinternet.ordering.lockbox import *
from mauveinternet.ordering.card import *

__doc__= """
>>> is_valid_pan('4111 1111 1111 1111')
True
>>> is_valid_pan('5454 6091 1567 2355')
False
>>> is_valid_pan('')
False
>>> is_valid_pan('a')
False
>>> is_valid_pan('4111 1111 1111 1111A')
False
>>> is_valid_pan('A4I11 1111 1111 1111')
False
"""


class TestCard(unittest.TestCase):
    def test_generator(self):
        """Test that the card generator generates valid PANs.

        Because these are randomly generated, we'll repeat the test a few times to
        ensure it's not just random chance that they pass."""

        for i in range(10):
            mc = Card.generateTestCard('mastercard')
            visa = Card.generateTestCard('visa')

            self.failUnless(is_valid_pan(mc.sensitive_data['pan']), mc.sensitive_data['pan'] + ' is not a valid PAN')
            self.failUnless(is_valid_pan(visa.sensitive_data['pan']), visa.sensitive_data['pan'] + ' is not a valid PAN')

    def test_pan_obfuscator(self):
        card = Card.generateTestCard('visa')
        card.setPAN('4111 1111 1111 1111')
        self.failUnlessEqual(card.getObfuscatedPAN(), 'XXXX XXXX XXXX 1111')


class TestCardAddressSplitting(unittest.TestCase):
    def setUp(self):
        self.card = Card.generateTestCard('visa')
        long_address = """Flat 1,
123 Test Street,
Testville,
Testshire,
TESTOPIA"""
        self.expected_address_lines = ["Flat 1", "123 Test Street", "Testville", "Testshire", "TESTOPIA"]
        self.card.sensitive_data['billing_address'] = long_address

    def test_full_address(self):
        ls = self.card.getAddressLines()
        self.failUnlessEqual(ls, self.expected_address_lines)

    def test_restricted_address(self):
        """Test that an address restricted to a maximum is both within that
        maximum number of lines and contains all the original data"""

        ls = self.card.getAddressLines(3)
        self.failUnless(len(ls) <= 3)

        recombined = '\n'.join(ls)
        for l in self.expected_address_lines:
            self.failUnless(l in recombined)

    def test_last_line_commas(self):
        """Test that a split address doesn't get double commas inserted anywhere"""

        ls = self.card.getAddressLines(3)
        for l in ls:
            self.failIf(',,' in l)


class TestCardEncryption(unittest.TestCase):
    def testEncryption(self):
        """Test that the symmetric object encryption can encrypt and decrypt arbitrary python objects."""

        key, data = symmetric_encrypt([1, 2, 3+2j])
        base64.decodestring(key)
        base64.decodestring(data)
        self.failUnlessEqual(symmetric_decrypt(key, data), [1, 2, 3+2j])

    def testDecryptionFailed(self):
        """Test that attempting to decrypt invalid data raises ValueError"""

        key, data = symmetric_encrypt(1)
        self.failUnlessRaises(ValueError, symmetric_decrypt, key, 'abcd')
        self.failUnlessRaises(ValueError, symmetric_decrypt, 'abcd', data)
