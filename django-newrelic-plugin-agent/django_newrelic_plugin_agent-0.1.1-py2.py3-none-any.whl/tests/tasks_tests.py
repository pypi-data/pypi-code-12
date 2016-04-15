from datetime import datetime

from mock import patch, call, Mock
from django_dynamic_fixture import G
from django.test import TestCase, override_settings
from freezegun import freeze_time
from db_mutex import DBMutexError

from newrelic_plugin_agent.tasks import PushMetricValueTask, PushMetricTimeslicesTask
from newrelic_plugin_agent.models import NewRelicComponent, NewRelicMetricTimeslice
from newrelic_plugin_agent.constants import AGENT_MUTEX_ID_NAMESPACE
from newrelic_plugin_agent.version import __version__


class TestException(Exception):
    pass


class PushMetricTimesliceTaskTest(TestCase):

    LICENSE_KEY = 'sup'

    @override_settings(NEWRELIC_LICENSE_KEY='sup')
    def setUp(self):
        self.component = G(NewRelicComponent)
        self.headers = {
            'X-License-Key': self.LICENSE_KEY,
            'Content-Type': 'application/json',
        }

    def build_push_json(self, hostname, component, metrics, duration):
        return {
            'agent': {
                'host': hostname,
                'version': __version__,
            },
            'components': [{
                'name': component.name,
                'guid': component.guid,
                'duration': duration,
                'metrics': metrics,
            }]
        }

    @freeze_time('2016-04-15 10:00:00')
    @patch('newrelic_plugin_agent.tasks.settings')
    @patch('newrelic_plugin_agent.tasks.db_mutex')
    @patch('newrelic_plugin_agent.tasks.post')
    @patch('newrelic_plugin_agent.tasks.gethostname')
    def test_run(self, gethostname, post, db_mutex, settings_mock):
        # setup
        settings_mock.NEWRELIC_LICENSE_KEY = self.LICENSE_KEY
        settings_mock.NEWRELIC_BASE_URL = 'quux'
        post.return_value = Mock()
        gethostname.return_value = 'ip-10-0-0-1'
        last_pushed_time = datetime(2016, 4, 15, 9, 59, 0)
        # make another component to test multi component push
        component = G(NewRelicComponent, guid='baz', last_pushed_time=last_pushed_time)
        self.component.last_pushed_time = last_pushed_time
        self.component.save()
        # add timeslices to self.component
        foo_values = {'foo': 'f'}
        bar_values = {'bar': 'b'}
        timeslices = [
            G(NewRelicMetricTimeslice, guid='foo', new_relic_component=self.component, values=foo_values),
            G(NewRelicMetricTimeslice, guid='bar', new_relic_component=self.component, values=bar_values),
        ]
        # run test
        PushMetricTimeslicesTask().run()
        # verify all the things
        db_mutex.assert_has_calls([
            call('{0}:{1}'.format(AGENT_MUTEX_ID_NAMESPACE, 'baz')),
            call().__enter__(),
            call().__exit__(None, None, None),
        ])
        self.assertFalse(NewRelicMetricTimeslice.objects.all().exists())
        metrics = {
            timeslice.guid: timeslice.values
            for timeslice in timeslices
        }
        expected_json_with_values = self.build_push_json('ip-10-0-0-1', self.component, metrics, 60)
        expected_json_without_values = self.build_push_json('ip-10-0-0-1', component, {}, 60)
        post.assert_has_calls([
            call('quux/platform/v1/metrics', json=expected_json_without_values, headers=self.headers),
            call('quux/platform/v1/metrics', json=expected_json_with_values, headers=self.headers),
        ])
        self.assertEqual(datetime(2016, 4, 15, 10, 0, 0), NewRelicComponent.objects.first().last_pushed_time)

    @freeze_time('2016-04-15 10:00:00')
    @patch('newrelic_plugin_agent.tasks.settings')
    @patch('newrelic_plugin_agent.tasks.db_mutex')
    @patch.object(PushMetricTimeslicesTask, 'retry')
    def test_run_retry(self, retry_mock, db_mutex, settings_mock):
        """
        Verifies that when the task can't obtain a lock, it retries
        """
        settings_mock.TIMESLICE_LOCK_RETRY_DELAY_MS = 30
        error = DBMutexError()
        db_mutex.side_effect = error
        retry_mock.return_value = TestException()
        with self.assertRaises(TestException):
            # run test
            PushMetricTimeslicesTask().run()
        retry_mock.assert_called_once_with(exc=error, countdown=30)


class PushMetricValueTaskTest(TestCase):

    def setUp(self):
        self.component = G(NewRelicComponent, guid='baz')

    @patch('newrelic_plugin_agent.tasks.db_mutex')
    @patch.object(NewRelicComponent, 'push')
    def test_run(self, push_mock, db_mutex):
        """
        Verifies that the task pushes a metric value to the given component without issue
        """
        PushMetricValueTask().run(self.component, 'foo', 3)
        db_mutex.assert_has_calls([
            call('{0}:{1}'.format(AGENT_MUTEX_ID_NAMESPACE, 'baz')),
            call().__enter__(),
            call().__exit__(None, None, None),
        ])
        push_mock.assert_called_once_with('foo', 3)

    @patch('newrelic_plugin_agent.tasks.db_mutex')
    @patch('newrelic_plugin_agent.tasks.settings')
    @patch.object(PushMetricValueTask, 'retry')
    def test_run_retry(self, retry_mock, settings_mock, db_mutex):
        """
        Verifies that the task retries if it can't obtain a lock
        """
        settings_mock.TIMESLICE_LOCK_RETRY_DELAY_MS = 40
        error = DBMutexError()
        db_mutex.side_effect = error
        retry_mock.return_value = TestException()
        with self.assertRaises(TestException):
            # run test
            PushMetricValueTask().run(self.component, 'foo', 3)
        retry_mock.assert_called_once_with(exc=error, countdown=40)
