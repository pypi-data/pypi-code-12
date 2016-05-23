from unittest import TestCase
from penelope.utils.auth import hash_password, verify_password


class AuthUtilsTestCase(TestCase):

    def test_hash_and_verify_password(self):
        password = 'abc123'
        hashed = hash_password(password=password)
        result = verify_password(password=password, hashed=hashed)
        self.assertTrue(result)
        result = verify_password(password='not the password', hashed=hashed)
        self.assertFalse(result)
