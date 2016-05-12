import unittest
from kerb_sts.awsrole import AWSRole


class TestAWSRoleCreation(unittest.TestCase):
    def test_with_role_as_none(self):
        is_valid = AWSRole.is_valid(None)
        self.assertFalse(is_valid)

    def test_with_empty_string(self):
        is_valid = AWSRole.is_valid('')
        self.assertFalse(is_valid)

    def test_with_malformed_role_string(self):
        is_valid = AWSRole.is_valid('arn_noseparator_provider')
        self.assertFalse(is_valid)

    def test_with_missing_arn_string(self):
        is_valid = AWSRole.is_valid(',provider')
        self.assertFalse(is_valid)

    def test_with_missing_provider_string(self):
        is_valid = AWSRole.is_valid('arn/role,')
        self.assertFalse(is_valid)

    def test_with_valid_strings(self):
        is_valid = AWSRole.is_valid('arn/role,provider')
        self.assertTrue(is_valid)

    def test_parsed_role(self):
        role = AWSRole('arn/role,provider')
        self.assertEqual(role.arn, 'arn/role')
        self.assertEqual(role.provider, 'provider')

    def test_with_valid_strings(self):
        role = AWSRole('arn/role,provider')
        self.assertEqual(role.name, 'role')


if __name__ == '__main__':
    unittest.main()
