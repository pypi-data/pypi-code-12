import cattleprod
from tests.configdata import *

from unittest import TestCase
from unittest.mock import patch, call


class TestBasicFunction(TestCase):

    @patch('cattleprod.requests')
    def test_flow(self, m_req):
        # the poke() answers
        # make sure we always return json ;)
        m_req.request.headers.get.return_value = "json"
        m_req.request.return_value.json.side_effect = [
            toplevel_dict, services_dict, {'result': 'ok'},
            # we test 1 time everything and one time only the
            # skey, akey notation
            toplevel_dict,
        ]
        expected_calls = [
            call('get', 'http://my_url/v1', auth=(1, 2)),
            call('get', 'http://my.rancher.url/v1/services', auth=(1, 2)),
            call('post', 'http://my.rancher.url/v1/dummy', auth=(1, 2), hey='ho'),
        ]

        t0 = cattleprod.poke('http://my_url/v1', auth=(1, 2))
        t1 = t0.get_services()
        t2 = t0.do_dummy(hey="ho")

        self.assertTrue(hasattr(t0.do_dummy, '__call__'))
        self.assertTrue(hasattr(t0.get_accounts, '__call__'))
        self.assertTrue(hasattr(t0.get_services, '__call__'))

        self.assertIsInstance(t0, cattleprod.Rod)
        self.assertIsInstance(t1, list)
        self.assertDictEqual({'result': 'ok'}, t2)

        for act_call, exp_call in zip(m_req.request.call_args_list, expected_calls):
            self.assertEqual(exp_call, act_call)

        t0 = cattleprod.poke('http://my_url/v1', 1, 2)
        self.assertIsInstance(t0, cattleprod.Rod)
        self.assertEqual(expected_calls[0], m_req.request.call_args_list[-1])
