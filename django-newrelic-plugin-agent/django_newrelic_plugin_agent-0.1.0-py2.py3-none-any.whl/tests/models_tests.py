from django.test import TestCase
from django_dynamic_fixture import G
from mock import patch
from manager_utils import ManagerUtilsManager

from newrelic_plugin_agent.models import NewRelicMetricTimeslice, NewRelicComponent


class NewRelicComponentTest(TestCase):

    def setUp(self):
        self.component = G(NewRelicComponent)

    @patch('newrelic_plugin_agent.models.NewRelicComponent._extend_timeslice')
    @patch('newrelic_plugin_agent.models.ManagerUtilsManager.upsert')
    def test_push_existing(self, upsert_mock, extend_timeslice_mock):
        """
        Verifies that push recomputes existing timeslice and upserts
        """
        # wrong metric guid
        G(NewRelicMetricTimeslice, guid='bar', new_relic_component=self.component, values={})
        # wrong component
        G(NewRelicMetricTimeslice, guid='foo', new_relic_component=G(NewRelicComponent), values={})
        values = {
            'total': 12,
            'count': 2,
            'min': 2,
            'max': 10,
        }
        G(NewRelicMetricTimeslice, guid='foo', new_relic_component=self.component, values=values)
        extend_timeslice_mock.return_value = values
        upsert_mock.return_value = (None, None)
        self.component.push('foo', 3)
        extend_timeslice_mock.assert_called_once_with(values, 3)
        upsert_mock.assert_called_once_with(guid='foo', updates={'values': values}, new_relic_component=self.component)

    @patch('newrelic_plugin_agent.models.NewRelicComponent._extend_timeslice')
    @patch('newrelic_plugin_agent.models.ManagerUtilsManager.upsert')
    def test_push_new(self, upsert_mock, extend_timeslice_mock):
        """
        Verifies that push creates and computes timeslice if it doesn't exist
        """
        # wrong metric guid
        G(NewRelicMetricTimeslice, guid='bar', new_relic_component=self.component, values={})
        # wrong component
        G(NewRelicMetricTimeslice, guid='foo', new_relic_component=G(NewRelicComponent), values={})
        values = {
            'total': 12,
            'count': 2,
            'min': 2,
            'max': 10,
        }
        extend_timeslice_mock.return_value = values
        upsert_mock.return_value = (None, None)
        self.component.push('foo', 3)
        extend_timeslice_mock.assert_called_once_with({}, 3)
        upsert_mock.assert_called_once_with(guid='foo', updates={'values': values}, new_relic_component=self.component)

    def test_extend_timeslice_empty(self):
        """
        Verifies that extending an empty timeslice works as expected
        """
        current = {}
        value = 3
        timeslice = self.component._extend_timeslice(current, value)
        expected_timeslice = {
            'total': 3,
            'count': 1,
            'min': 3,
            'max': 3,
            'sum_of_squares': 9,
        }
        self.assertEqual(expected_timeslice, timeslice)

    def test_extend_timeslice_min(self):
        """
        Verifies that a value smaller than the current timeslice min will
        replace the current timeslice min value
        """
        current = {
            'total': 5,
            'count': 1,
            'min': 5,
            'max': 5,
            'sum_of_squares': 25,
        }
        value = 3
        timeslice = self.component._extend_timeslice(current, value)
        expected_timeslice = {
            'total': 8,
            'count': 2,
            'min': 3,
            'max': 5,
            'sum_of_squares': 34,
        }
        self.assertEqual(expected_timeslice, timeslice)

    def test_extend_timeslice_max(self):
        """
        Verifies that a value larger than the current timeslice max will replace
        the current timeslice max value
        """
        current = {
            'total': 5,
            'count': 1,
            'min': 5,
            'max': 5,
            'sum_of_squares': 25,
        }
        value = 8
        timeslice = self.component._extend_timeslice(current, value)
        expected_timeslice = {
            'total': 13,
            'count': 2,
            'min': 5,
            'max': 8,
            'sum_of_squares': 89,
        }
        self.assertEqual(expected_timeslice, timeslice)

    def test_merge(self):
        model_values = {
            'total': 13,
            'count': 2,
            'min': 5,
            'max': 8,
            'sum_of_squares': 89,
        }
        G(NewRelicMetricTimeslice, guid='foo', new_relic_component=self.component, values=model_values)
        timeslice = {
            'total': 5,
            'count': 1,
            'min': 5,
            'max': 5,
            'sum_of_squares': 25,
        }
        merged_timeslice = self.component.merge('foo', timeslice)
        expected = {
            'total': 18,
            'count': 3,
            'min': 5,
            'max': 8,
            'sum_of_squares': 114,
        }
        self.assertEqual(expected, merged_timeslice.values)


class NewRelicMetricTimesliceTest(TestCase):

    def test_manager(self):
        """
        Verifies that the custom manager is configured to work with model
        """
        self.assertIsInstance(NewRelicMetricTimeslice.objects, ManagerUtilsManager)
