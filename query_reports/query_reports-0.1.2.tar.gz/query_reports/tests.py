from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase


class QueryReportTests(TestCase):
    fixtures = ['test_query_reports.json']

    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "", "admin")
        self.client.login(username="admin", password="admin")

    def testQueryReportIndex(self):
        response = self.client.get(reverse('qreports-report-index'))
        self.assertEqual(response.status_code, 200)

    def testQueryReport(self):
        response = self.client.get(
            reverse('qreports-show-report', kwargs=dict(slug="test"))
        )
        self.assertEqual(response.status_code, 200)

        # with variable
        response = self.client.get(
            reverse('qreports-show-report', kwargs=dict(slug="test")),
            dict(name="john")
        )
        self.assertEqual(response.status_code, 200)

