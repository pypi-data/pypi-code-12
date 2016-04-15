from django.test import TestCase
from hidash import views
from django.test import Client
from django.test.runner import DiscoverRunner
import json


class NoDbTestRunner(DiscoverRunner):
    """ A test runner to test without database creation """

    def setup_databases(self, **kwargs):
        """ Override the database creation defined in parent class """
        pass

    def teardown_databases(self, old_config, **kwargs):
        """ Override the database teardown defined in parent class """
        pass


class UnitTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_coerce_number(self):
        self.assertEqual(views._coerce_number("12", 0), 12)
        self.assertEqual(views._coerce_number("not a number", 0), 0)
        self.assertEqual(views._coerce_number("23.2", 0), 23.2)
        self.assertEqual(views._coerce_number(3, 0), 3)
        self.assertEqual(views._coerce_number(3.4, 0), 3.4)

    def test_to_time_of_day(self):
        self.assertEqual(views._to_time_of_day(10), (0, 0, 10, 0))
        self.assertEqual(views._to_time_of_day("not a valid time"), (0, 0, 0, 0))
        self.assertEqual(views._to_time_of_day("10:04:39"), (10, 04, 0, 0))
        self.assertEqual(views._to_time_of_day(120), (0, 2, 0, 0))

    def test_convert_to_type(self):
        self.assertEqual(views._convert_to_type(10, "timeofday"), (0, 0, 10, 0))
        self.assertEqual(views._convert_to_type(10, "number"), 10)
        self.assertEqual(views._convert_to_type(10.78, "number"), 10.78)

    def test_dispatch_api(self):
        response = self.client.get('/api/charts/timesheet4.json/?query=q1&start=1&end=12', {})
        self.assertEqual(response.status_code, 200)
        received_data = json.loads(response.content)
        self.assertGreaterEqual(len(received_data), 1)
        self.assertGreaterEqual(len(received_data[0]['rows']), 1)
        self.assertGreaterEqual(len(received_data[0]['cols']), 1)
        self.assertEqual(received_data,[{"rows": [{"c": [{"v": "Date(2015, 11, 5)"}, {"v": 2.0}]}, {"c": [{"v": "Date(2015, 12, 1)"}, {"v": 14.5}]}, {"c": [{"v": "Date(2015, 12, 2)"}, {"v": 8.0}]}, {"c": [{"v": "Date(2015, 12, 3)"}, {"v": 4.5}]}, {"c": [{"v": "Date(2015, 12, 4)"}, {"v": 6.5}]}, {"c": [{"v": "Date(2015, 12, 7)"}, {"v": 7.5}]}, {"c": [{"v": "Date(2015, 12, 8)"}, {"v": 8.0}]}, {"c": [{"v": "Date(2015, 12, 9)"}, {"v": 8.5}]}, {"c": [{"v": "Date(2015, 12, 10)"}, {"v": 10.5}]}, {"c": [{"v": "Date(2015, 12, 11)"}, {"v": 8.0}]}], "chart_type": "ColumnChart", "cols": [{"type": "date", "id": "month", "label": "Month"}, {"type": "number", "id": "ARUBACCUI", "label": "ARUBACCUI"}]}])

        response = self.client.get('/api/charts/timesheet.json/?query=q1', {})
        self.assertEqual(response.status_code, 200)
        received_data = json.loads(response.content)
        self.assertGreaterEqual(len(received_data), 1)
        self.assertGreaterEqual(len(received_data[0]['rows']), 1)
        self.assertGreaterEqual(len(received_data[0]['cols']), 1)
        self.assertEqual(received_data,[{"rows": [{"c": [{"v": "INDEED"}, {"v": 2414.6499999999996}]}, {"c": [{"v": "SYMWD"}, {"v": 1227.95}]}, {"c": [{"v": "ARUBACCUI"}, {"v": 772.7}]}, {"c": [{"v": "EXMSOFT-GA"}, {"v": 660.5}]}, {"c": [{"v": "BUZZ"}, {"v": 530.0}]}], "cols": [{"type": "string", "id": "project_code", "label": "Project_Code"}, {"type": "number", "id": "hrs", "label": "Hours"}], "chart_type": "ColumnChart"}])

    def test_dispatch_xls(self):
        response = self.client.get('/api/charts/timsheet.xls/?query=q1', {})
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.get('Content-Disposition'), "attachment; filename=Report.xls")
        self.assertEquals(response.get('Content-type'), "application/vnd.ms-excel")

    def test_dispatch_pdf(self):
        response = self.client.get('/api/reports/timesheet.pdf/?query=q1', {})
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.get('Content-Disposition'), "attachment; filename=Report.pdf")
        self.assertEquals(response.get('Content-type'), "application/pdf")
