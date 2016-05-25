"""
tests for ip registry (iprir) project

work in progress
"""

import socket

from django.test import TestCase
from django.core.urlresolvers import reverse

from iprir.models import Registry, TLD, InetNum


class InetNumTests(TestCase):
    def test_if_localhost_returns_iana(self):

        localIP = socket.gethostbyname(socket.gethostname())

        registry = Registry.objects.create(registryDesc="itise")
        tld = TLD.objects.create(domain="NL", description=registry, active=False)
        inetnum = InetNum.objects.create(inetNumFrom=0, inetNumTo=4228250625, tld_id=tld.pk, Registry_id=registry.pk, inetNumValid=True, inetNumAllocated=True)

        response = self.client.get(reverse('iprir:index'))
        self.assertEqual(response.status_code, 200)
        #self.assertContains(response, 'itise')
