import unittest
import koalacompanies
from google.appengine.ext import testbed
from google.appengine.ext import deferred
from datetime import datetime

__author__ = 'Matt Badger'


class TestCompany(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases
        self.test_company_with_spaces = {
            'company_name': '  test_company_name  ',
            'contact_first_name': '  test_contact_first_name  ',
            'contact_last_name': '  test_contact_last_name  ',
            'contact_email': '  test_contact_email  ',
            'contact_phone': '  test_contact_phone  ',
            'contact_mobile': '  test_contact_mobile  ',
            'delivery_address_1': '  test_delivery_address_1  ',
            'delivery_address_2': '  test_delivery_address_2  ',
            'delivery_address_3': '  test_delivery_address_3  ',
            'delivery_city': '  test_delivery_city  ',
            'delivery_county': '  test_delivery_county  ',
            'delivery_state': '  test_delivery_state  ',
            'delivery_post_code': '  test_delivery_post_code  ',
            'delivery_country': '  test_delivery_country  ',
            'billing_address_1': '  test_billing_address_1  ',
            'billing_address_2': '  test_billing_address_2  ',
            'billing_address_3': '  test_billing_address_3  ',
            'billing_city': '  test_billing_city  ',
            'billing_county': '  test_billing_county  ',
            'billing_state': '  test_billing_state  ',
            'billing_post_code': '  test_billing_post_code  ',
            'billing_country': '  test_billing_country  ',
        }
        self.test_company = {
            'company_name': 'test_company_name',
            'contact_first_name': 'test_contact_first_name',
            'contact_last_name': 'test_contact_last_name',
            'contact_email': 'test_contact_email',
            'contact_phone': 'test_contact_phone',
            'contact_mobile': 'test_contact_mobile',
            'delivery_address_1': 'test_delivery_address_1',
            'delivery_address_2': 'test_delivery_address_2',
            'delivery_address_3': 'test_delivery_address_3',
            'delivery_city': 'test_delivery_city',
            'delivery_county': 'test_delivery_county',
            'delivery_state': 'test_delivery_state',
            'delivery_post_code': 'test_delivery_post_code',
            'delivery_country': 'test_delivery_country',
            'billing_address_1': 'test_billing_address_1',
            'billing_address_2': 'test_billing_address_2',
            'billing_address_3': 'test_billing_address_3',
            'billing_city': 'test_billing_city',
            'billing_county': 'test_billing_county',
            'billing_state': 'test_billing_state',
            'billing_post_code': 'test_billing_post_code',
            'billing_country': 'test_billing_country',
        }

    def tearDown(self):
        self.testbed.deactivate()

    def test_insert_company(self):
        company = koalacompanies.Companies.new(**self.test_company)
        company_uid = koalacompanies.Companies.insert(resource_object=company)
        self.assertTrue(company_uid)

    def test_get_company(self):
        company = koalacompanies.Companies.new(**self.test_company)
        company_uid = koalacompanies.Companies.insert(resource_object=company)

        retrieved_company = koalacompanies.Companies.get(resource_uid=company_uid)
        self.assertTrue(retrieved_company, u'Stored value mismatch')
        self.assertTrue(retrieved_company.uid, u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_company.created, datetime), u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_company.updated, datetime), u'Stored value mismatch')
        self.assertEqual(retrieved_company.company_name, self.test_company['company_name'], u'Stored company_name value mismatch')
        self.assertEqual(retrieved_company.contact_first_name, self.test_company['contact_first_name'], u'Stored contact_first_name value mismatch')
        self.assertEqual(retrieved_company.contact_last_name, self.test_company['contact_last_name'], u'Stored contact_last_name value mismatch')
        self.assertEqual(retrieved_company.contact_email, self.test_company['contact_email'], u'Stored contact_email value mismatch')
        self.assertEqual(retrieved_company.contact_phone, self.test_company['contact_phone'], u'Stored contact_phone value mismatch')
        self.assertEqual(retrieved_company.contact_mobile, self.test_company['contact_mobile'], u'Stored contact_mobile value mismatch')
        self.assertEqual(retrieved_company.delivery_address_1, self.test_company['delivery_address_1'], u'Stored delivery_address_1 value mismatch')
        self.assertEqual(retrieved_company.delivery_address_2, self.test_company['delivery_address_2'], u'Stored delivery_address_2 value mismatch')
        self.assertEqual(retrieved_company.delivery_address_3, self.test_company['delivery_address_3'], u'Stored delivery_address_3 value mismatch')
        self.assertEqual(retrieved_company.delivery_city, self.test_company['delivery_city'], u'Stored delivery_city value mismatch')
        self.assertEqual(retrieved_company.delivery_county, self.test_company['delivery_county'], u'Stored delivery_county value mismatch')
        self.assertEqual(retrieved_company.delivery_state, self.test_company['delivery_state'], u'Stored delivery_state value mismatch')
        self.assertEqual(retrieved_company.delivery_post_code, self.test_company['delivery_post_code'], u'Stored delivery_post_code value mismatch')
        self.assertEqual(retrieved_company.delivery_country, self.test_company['delivery_country'], u'Stored delivery_country value mismatch')
        self.assertEqual(retrieved_company.billing_address_1, self.test_company['billing_address_1'], u'Stored billing_address_1 value mismatch')
        self.assertEqual(retrieved_company.billing_address_2, self.test_company['billing_address_2'], u'Stored billing_address_2 value mismatch')
        self.assertEqual(retrieved_company.billing_address_3, self.test_company['billing_address_3'], u'Stored billing_address_3 value mismatch')
        self.assertEqual(retrieved_company.billing_city, self.test_company['billing_city'], u'Stored billing_city value mismatch')
        self.assertEqual(retrieved_company.billing_county, self.test_company['billing_county'], u'Stored billing_county value mismatch')
        self.assertEqual(retrieved_company.billing_state, self.test_company['billing_state'], u'Stored billing_state value mismatch')
        self.assertEqual(retrieved_company.billing_post_code, self.test_company['billing_post_code'], u'Stored billing_post_code value mismatch')
        self.assertEqual(retrieved_company.billing_country, self.test_company['billing_country'], u'Stored billing_country value mismatch')

    def test_insert_company_strip_filter(self):
        company = koalacompanies.Companies.new(**self.test_company_with_spaces)
        company_uid = koalacompanies.Companies.insert(resource_object=company)

        retrieved_company = koalacompanies.Companies.get(resource_uid=company_uid)

        self.assertEqual(retrieved_company.company_name, self.test_company['company_name'], u'Stored company_name value mismatch')
        self.assertEqual(retrieved_company.contact_first_name, self.test_company['contact_first_name'], u'Stored contact_first_name value mismatch')
        self.assertEqual(retrieved_company.contact_last_name, self.test_company['contact_last_name'], u'Stored contact_last_name value mismatch')
        self.assertEqual(retrieved_company.contact_email, self.test_company['contact_email'], u'Stored contact_email value mismatch')
        self.assertEqual(retrieved_company.contact_phone, self.test_company['contact_phone'], u'Stored contact_phone value mismatch')
        self.assertEqual(retrieved_company.contact_mobile, self.test_company['contact_mobile'], u'Stored contact_mobile value mismatch')
        self.assertEqual(retrieved_company.delivery_address_1, self.test_company['delivery_address_1'], u'Stored delivery_address_1 value mismatch')
        self.assertEqual(retrieved_company.delivery_address_2, self.test_company['delivery_address_2'], u'Stored delivery_address_2 value mismatch')
        self.assertEqual(retrieved_company.delivery_address_3, self.test_company['delivery_address_3'], u'Stored delivery_address_3 value mismatch')
        self.assertEqual(retrieved_company.delivery_city, self.test_company['delivery_city'], u'Stored delivery_city value mismatch')
        self.assertEqual(retrieved_company.delivery_county, self.test_company['delivery_county'], u'Stored delivery_county value mismatch')
        self.assertEqual(retrieved_company.delivery_state, self.test_company['delivery_state'], u'Stored delivery_state value mismatch')
        self.assertEqual(retrieved_company.delivery_post_code, self.test_company['delivery_post_code'], u'Stored delivery_post_code value mismatch')
        self.assertEqual(retrieved_company.delivery_country, self.test_company['delivery_country'], u'Stored delivery_country value mismatch')
        self.assertEqual(retrieved_company.billing_address_1, self.test_company['billing_address_1'], u'Stored billing_address_1 value mismatch')
        self.assertEqual(retrieved_company.billing_address_2, self.test_company['billing_address_2'], u'Stored billing_address_2 value mismatch')
        self.assertEqual(retrieved_company.billing_address_3, self.test_company['billing_address_3'], u'Stored billing_address_3 value mismatch')
        self.assertEqual(retrieved_company.billing_city, self.test_company['billing_city'], u'Stored billing_city value mismatch')
        self.assertEqual(retrieved_company.billing_county, self.test_company['billing_county'], u'Stored billing_county value mismatch')
        self.assertEqual(retrieved_company.billing_state, self.test_company['billing_state'], u'Stored billing_state value mismatch')
        self.assertEqual(retrieved_company.billing_post_code, self.test_company['billing_post_code'], u'Stored billing_post_code value mismatch')
        self.assertEqual(retrieved_company.billing_country, self.test_company['billing_country'], u'Stored billing_country value mismatch')

    def test_update_company(self):
        company = koalacompanies.Companies.new(**self.test_company)
        company_uid = koalacompanies.Companies.insert(resource_object=company)
        retrieved_company = koalacompanies.Companies.get(resource_uid=company_uid)

        retrieved_company.company_name = 'updated_company_name'
        retrieved_company.contact_first_name = 'updated_contact_first_name'
        retrieved_company.contact_last_name = 'updated_contact_last_name'
        retrieved_company.contact_email = 'updated_contact_email'
        retrieved_company.contact_phone = 'updated_contact_phone'
        retrieved_company.contact_mobile = 'updated_contact_mobile'
        retrieved_company.delivery_address_1 = 'updated_delivery_address_1'
        retrieved_company.delivery_address_2 = 'updated_delivery_address_2'
        retrieved_company.delivery_address_3 = 'updated_delivery_address_3'
        retrieved_company.delivery_city = 'updated_delivery_city'
        retrieved_company.delivery_county = 'updated_delivery_county'
        retrieved_company.delivery_state = 'updated_delivery_state'
        retrieved_company.delivery_post_code = 'updated_delivery_post_code'
        retrieved_company.delivery_country = 'updated_delivery_country'
        retrieved_company.billing_address_1 = 'updated_billing_address_1'
        retrieved_company.billing_address_2 = 'updated_billing_address_2'
        retrieved_company.billing_address_3 = 'updated_billing_address_3'
        retrieved_company.billing_city = 'updated_billing_city'
        retrieved_company.billing_county = 'updated_billing_county'
        retrieved_company.billing_state = 'updated_billing_state'
        retrieved_company.billing_post_code = 'updated_billing_post_code'
        retrieved_company.billing_country = 'updated_billing_country'

        koalacompanies.Companies.update(resource_object=retrieved_company)
        updated_company = koalacompanies.Companies.get(resource_uid=company_uid)

        self.assertEqual(retrieved_company.uid, updated_company.uid, u'UID mismatch')
        self.assertEqual(retrieved_company.created, updated_company.created, u'Created date has changed')
        self.assertNotEqual(retrieved_company.updated, updated_company.updated, u'Updated date not changed')
        self.assertEqual(updated_company.company_name, 'updated_company_name', u'Stored company_name value mismatch')
        self.assertEqual(updated_company.contact_first_name, 'updated_contact_first_name', u'Stored contact_first_name value mismatch')
        self.assertEqual(updated_company.contact_last_name, 'updated_contact_last_name', u'Stored contact_last_name value mismatch')
        self.assertEqual(updated_company.contact_email, 'updated_contact_email', u'Stored contact_email value mismatch')
        self.assertEqual(updated_company.contact_phone, 'updated_contact_phone', u'Stored contact_phone value mismatch')
        self.assertEqual(updated_company.contact_mobile, 'updated_contact_mobile', u'Stored contact_mobile value mismatch')
        self.assertEqual(updated_company.delivery_address_1, 'updated_delivery_address_1', u'Stored delivery_address_1 value mismatch')
        self.assertEqual(updated_company.delivery_address_2, 'updated_delivery_address_2', u'Stored delivery_address_2 value mismatch')
        self.assertEqual(updated_company.delivery_address_3, 'updated_delivery_address_3', u'Stored delivery_address_3 value mismatch')
        self.assertEqual(updated_company.delivery_city, 'updated_delivery_city', u'Stored delivery_city value mismatch')
        self.assertEqual(updated_company.delivery_county, 'updated_delivery_county', u'Stored delivery_county value mismatch')
        self.assertEqual(updated_company.delivery_state, 'updated_delivery_state', u'Stored delivery_state value mismatch')
        self.assertEqual(updated_company.delivery_post_code, 'updated_delivery_post_code', u'Stored delivery_post_code value mismatch')
        self.assertEqual(updated_company.delivery_country, 'updated_delivery_country', u'Stored delivery_country value mismatch')
        self.assertEqual(updated_company.billing_address_1, 'updated_billing_address_1', u'Stored billing_address_1 value mismatch')
        self.assertEqual(updated_company.billing_address_2, 'updated_billing_address_2', u'Stored billing_address_2 value mismatch')
        self.assertEqual(updated_company.billing_address_3, 'updated_billing_address_3', u'Stored billing_address_3 value mismatch')
        self.assertEqual(updated_company.billing_city, 'updated_billing_city', u'Stored billing_city value mismatch')
        self.assertEqual(updated_company.billing_county, 'updated_billing_county', u'Stored billing_county value mismatch')
        self.assertEqual(updated_company.billing_state, 'updated_billing_state', u'Stored billing_state value mismatch')
        self.assertEqual(updated_company.billing_post_code, 'updated_billing_post_code', u'Stored billing_post_code value mismatch')
        self.assertEqual(updated_company.billing_country, 'updated_billing_country', u'Stored billing_country value mismatch')

    def test_delete_company(self):
        company = koalacompanies.Companies.new(**self.test_company)
        company_uid = koalacompanies.Companies.insert(resource_object=company)
        koalacompanies.Companies.delete(resource_uid=company_uid)
        retrieved_company = koalacompanies.Companies.get(resource_uid=company_uid)
        self.assertFalse(retrieved_company)

    def test_insert_search(self):
        company = koalacompanies.Companies.new(**self.test_company)
        koalacompanies.Companies.insert(resource_object=company)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Deferred task missing')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        search_result = koalacompanies.Companies.search(
            query_string='company_name: {}'.format(self.test_company['company_name']))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_update_search(self):
        company = koalacompanies.Companies.new(**self.test_company)
        company_uid = koalacompanies.Companies.insert(resource_object=company)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        retrieved_company = koalacompanies.Companies.get(resource_uid=company_uid)
        retrieved_company.company_name = 'updated_company_name'
        koalacompanies.Companies.update(resource_object=retrieved_company)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')

        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        search_result = koalacompanies.Companies.search(query_string='company_name: {}'.format('updated_company_name'))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_delete_search(self):
        company = koalacompanies.Companies.new(**self.test_company)
        company_uid = koalacompanies.Companies.insert(resource_object=company)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        koalacompanies.Companies.delete(resource_uid=company_uid)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')

        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        search_result = koalacompanies.Companies.search(
            query_string='company_name: {}'.format(self.test_company['company_name']))
        self.assertEqual(search_result.results_count, 0, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 0, u'Query returned incorrect number of results')
