import os
import unittest
from unittest import TestCase

import betamax
from betamax_serializers import pretty_json
from betamax.fixtures import unittest as unitest


najdisi_username = os.environ.get('USERNAME', 'fubar_username')
najdisi_password = os.environ.get('PASSWORD', 'fubar_password')
najdisi_phonenum = os.environ.get('PHONENUM', 'fubar_phonenum')

here_ = os.path.dirname(os.path.realpath(__file__))
betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with betamax.Betamax.configure() as config:
    config.cassette_library_dir = os.path.join(here_, 'fixtures', 'cassettes')
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.define_cassette_placeholder(
        '<NAJDISI_USERNAME>',
        najdisi_username
    )
    config.define_cassette_placeholder(
        '<NAJDISI_PASSWORD>',
        najdisi_password
    )
    config.define_cassette_placeholder(
        '<NAJDISI_PHONENUM>',
        najdisi_phonenum
    )


class VCRTestCase(unitest.BetamaxTestCase):
    # Add your the rest of the helper methods you want for your
    # integration tests
    pass


class LoadTestCase(VCRTestCase):
    """docstring for LoadTestCase"""
    def test_dummy(self):
        from najdisi_sms.api import SMSSender
        sender = SMSSender(najdisi_username, najdisi_password)
        sender.s = self.session
        sender.send(najdisi_phonenum, "test")


if __name__ == '__main__':
    unittest.main()
