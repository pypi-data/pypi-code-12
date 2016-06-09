import mock
import unittest

from datarobot.utils import retry
import datarobot.errors as err


class TestDelayHelpers(unittest.TestCase):

    def test_no_delay(self):
        nd = retry.NoDelay()
        nd.delay()

    def test_constant_delay(self):
        cd = retry.ConstantDelay(10)
        with mock.patch('datarobot.utils.retry.time') as mock_time:
            cd.delay()
            mock_time.sleep.assert_called_once_with(10)

    def test_exponential_delay(self):
        ed = retry.ExponentialBackoffDelay(initial=1, growth=2)
        with mock.patch('datarobot.utils.retry.time') as mock_time:
            ed.delay()
            mock_time.sleep.assert_called_once_with(1)
            mock_time.reset_mock()
            ed.delay()
            mock_time.sleep.assert_called_once_with(2)
            mock_time.reset_mock()
            ed.delay()
            mock_time.sleep.assert_called_once_with(4)


class TestPredictionRetries(unittest.TestCase):

    def test_retries_eventually_run_out(self):
        requestor = mock.Mock()
        requestor.send_request.side_effect = [
            ValueError('Fail 1'),
            ValueError('Fail 2'),
            ValueError('Fail 3')
        ]
        manager = retry.RetryManager(requestor, n_retries=2,
                                     nonfatal_exceptions=(ValueError,),
                                     delay_manager=retry.NoDelay())
        with self.assertRaises(err.AllRetriesFailedError):
            manager.send_request()

    def test_retried_will_return_the_result(self):
        requestor = mock.Mock()
        great_success = 'Great success!'
        requestor.send_request.return_value = great_success

        manager = retry.RetryManager(requestor, n_retries=2)
        result = manager.send_request()
        self.assertEqual(result, great_success)
