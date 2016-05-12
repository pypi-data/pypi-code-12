import cattleprod
from tests.configdata import *

from unittest import TestCase
from unittest.mock import patch


class TestBasicFunction(TestCase):

    @patch('cattleprod.requests.post')
    @patch('cattleprod.requests.get')
    def testFlow(self, m_get, m_post):
        # the poke() answers
        m_get.return_value.json.side_effect = [toplevel_dict, services_dict]
        # the do_update() answer
        m_post.return_value.json.return_value = service_dict
        t0 = cattleprod.poke("http://my_url/v1")
        services = t0.get_services()
        self.assertIsInstance(services, list)
        service = services[0]
        self.assertIsInstance(service, cattleprod.Rod)
        self.assertTrue(hasattr(service.do_udpate, '__call__'))
        self.assertTrue(hasattr(service.get_self, '__call__'))
        restarted_service = service.do_restart()
        self.assertIsInstance(restarted_service, cattleprod.Rod)
