import unittest
import os

class TestAWS(unittest.TestCase):

    def test_credentials(self):
        from baiji.config import credentials
        from baiji.util import yaml
        bodylabs_file_path = os.getenv('BODYLABS_CREDENTIAL_FILE', os.path.expanduser('~/.bodylabs'))
        if not os.path.exists(bodylabs_file_path):
            raise unittest.SkipTest("Skipping test_credentials because ~/.bodylabs doesn't exist.")
        truth = yaml.load(bodylabs_file_path)
        self.assertEqual(credentials.key, truth['AWS_ACCESS_KEY'])
        self.assertEqual(credentials.secret, truth['AWS_SECRET'])
