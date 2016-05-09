import time
import unittest
import mock

class TestCore(unittest.TestCase):

    @mock.patch('datadog.initialize')
    def test_metrics_initialized_with_known_backend(self, initialize_mock):
        from .core import Metrics

        _ = initialize_mock # For pylint.
        metrics_uri = 'metrics://abc@datadog?app_key=def&debug=true'

        Metrics(metrics_uri, host='i-12345')

        initialize_mock.assert_called_once_with(api_key='abc', app_key='def', host_name='i-12345', debug='true')

    @mock.patch('datadog.initialize')
    def test_metrics_initialized_with_unknown_backend_raise_error(self, initialize_mock):

        from .core import Metrics

        _ = initialize_mock # For pylint.
        metrics_uri = 'metrics://abc@unknown?app_key=def&debug=true'

        with self.assertRaises(NotImplementedError):
            Metrics(metrics_uri)

    @mock.patch('datadog.initialize')
    def test_metrics_initialized_bad_metrics_uri_scheme_raise_value_error(self, initialize_mock):

        from .core import Metrics

        _ = initialize_mock # For pylint.
        metrics_uri = 'http://abc@unknown?app_key=def&debug=true'

        with self.assertRaises(ValueError):
            Metrics(metrics_uri)

class TestDatadog(unittest.TestCase):

    def setUp(self):

        from .core import Metrics

        metrics_uri = 'metrics://abc@datadog?app_key=def&debug=true'

        self.datadog_metrics = Metrics(metrics_uri)

    @mock.patch('datadog.initialize')
    @mock.patch('datadog.api.metrics.Metric.send')
    def test_datadog_send_metrics_with_tags_tranformed(self, send_mock, initialize_mock):

        _ = initialize_mock # For pylint.
        self.datadog_metrics.send('test', 1, tags={'tag1': 'a'})

        send_mock.assert_called_once_with(
            metric='test',
            points=(int(time.time()), 1),
            tags=['tag1:a'],
            type='gauge'
        )

    @mock.patch('datadog.initialize')
    @mock.patch('datadog.api.metrics.Metric.send')
    def test_datadog_send_metrics_with_overrided_timestamp(self, send_mock, initialize_mock):

        _ = initialize_mock # For pylint.

        timestamp = int(time.time()) - 5000
        self.datadog_metrics.send('test', 1, tags={'tag1': 'a'}, timestamp=timestamp)

        send_mock.assert_called_once_with(
            metric='test',
            points=(timestamp, 1),
            tags=['tag1:a'],
            type='gauge'
        )
