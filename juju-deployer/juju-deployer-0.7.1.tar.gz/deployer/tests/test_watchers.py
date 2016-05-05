"""Tests juju-core environment watchers."""

import unittest

import mock

from deployer.env import watchers
from deployer.utils import ErrorExit


class TestWaitForUnits(unittest.TestCase):

    def make_watch(self, *changesets):
        """Create and return a mock watcher returning the given change sets."""
        watch = mock.MagicMock()
        watch.__iter__.return_value = changesets
        return watch

    def make_change(self, unit_name, status):
        """Create and return a juju-core mega-watcher unit change."""
        service = unit_name.split('/')[0]
        return {'Name': unit_name, 'Service': service, 'Status': status}

    def test_success(self):
        # It is possible to watch for units to be started.
        watch = self.make_watch(
            [('unit', 'change', self.make_change('django/0', 'pending')),
             ('unit', 'change', self.make_change('haproxy/1', 'pending'))],
            [('unit', 'change', self.make_change('django/0', 'started')),
             ('unit', 'change', self.make_change('haproxy/1', 'started'))],
        )
        watcher = watchers.WaitForUnits(watch)
        callback = mock.Mock()
        watcher.run(callback)
        # The callback has been called once for each change in the change sets,
        # excluding the initial state.
        self.assertEqual(2, callback.call_count)
        # The watcher has been properly stopped.
        watch.stop.assert_called_once_with()

    def test_watch_restart(self):
        # It is possible for a watch to be restarted.
        watch = self.make_watch(
            [('unit', 'change', self.make_change('django/0', 'pending')),
             ('unit', 'change', self.make_change('haproxy/1', 'pending'))],
            [('unit', 'change', self.make_change('django/0', 'started'))],
            # On a restart we get reinformed of things already current
            [('unit', 'change', self.make_change('django/0', 'started')),
             ('unit', 'change', self.make_change('haproxy/1', 'pending'))],
            [('unit', 'change', self.make_change('django/0', 'started')),
             ('unit', 'change', self.make_change('haproxy/1', 'started'))]
        )
        watcher = watchers.WaitForUnits(watch)
        callback = mock.Mock()
        watcher.run(callback)
        # The callback has been called once for each change in the change sets,
        # excluding the initial state.
        self.assertEqual(5, callback.call_count)
        # The watcher has been properly stopped.
        watch.stop.assert_called_once_with()

    def test_errors_handling(self):
        # Errors can be handled providing an on_errors callable.
        watch = self.make_watch(
            [('unit', 'change', self.make_change('django/0', 'pending')),
             ('unit', 'change', self.make_change('django/42', 'pending')),
             ('unit', 'change', self.make_change('haproxy/1', 'pending'))],
            [('unit', 'change', self.make_change('django/0', 'pending')),
             ('unit', 'change', self.make_change('django/42', 'error')),
             ('unit', 'change', self.make_change('haproxy/1', 'error'))],
            [('unit', 'change', self.make_change('django/0', 'error')),
             ('unit', 'change', self.make_change('django/42', 'error')),
             ('unit', 'change', self.make_change('haproxy/1', 'error'))],
        )
        on_errors = mock.Mock()
        watcher = watchers.WaitForUnits(watch, on_errors=on_errors)
        watcher.run()
        # The watcher has been properly stopped.
        watch.stop.assert_called_once_with()
        # The errors handler has been called once for each changeset containing
        # errors.
        self.assertEqual(2, on_errors.call_count)
        on_errors.assert_has_calls([
            mock.call([
                {'Status': 'error', 'Name': 'django/42', 'Service': 'django'},
                {'Status': 'error', 'Name': 'haproxy/1', 'Service': 'haproxy'}
            ]),
            mock.call([
                {'Status': 'error', 'Name': 'django/0', 'Service': 'django'}]),
        ])

    def test_specific_services(self):
        # It is possible to only watch units belonging to specific services.
        watch = self.make_watch(
            [('unit', 'change', self.make_change('django/0', 'pending')),
             ('unit', 'change', self.make_change('django/42', 'pending')),
             ('unit', 'change', self.make_change('haproxy/1', 'pending')),
             ('unit', 'change', self.make_change('haproxy/47', 'pending'))],
            [('unit', 'change', self.make_change('django/0', 'pending')),
             ('unit', 'change', self.make_change('django/42', 'started')),
             ('unit', 'change', self.make_change('haproxy/1', 'error')),
             ('unit', 'change', self.make_change('haproxy/47', 'pending'))],
            [('unit', 'change', self.make_change('django/0', 'error')),
             ('unit', 'change', self.make_change('django/42', 'started')),
             ('unit', 'change', self.make_change('haproxy/1', 'error')),
             ('unit', 'change', self.make_change('haproxy/47', 'pending'))],
        )
        on_errors = mock.Mock()
        watcher = watchers.WaitForUnits(
            watch, services=['django'], on_errors=on_errors)
        watcher.run()
        # The watcher has been properly stopped, even if haproxy/47 is pending.
        watch.stop.assert_called_once_with()
        # The errors handler has been called for the django error, not for the
        # haproxy one.
        on_errors.assert_called_once_with(
            [{'Status': 'error', 'Name': 'django/0', 'Service': 'django'}])

    def test_goal_states(self):
        # It is possible to watch for the given goal state
        watch = self.make_watch(
            [('unit', 'change', self.make_change('django/0', 'pending')),
             ('unit', 'change', self.make_change('haproxy/1', 'pending'))],
        )
        watcher = watchers.WaitForUnits(watch, goal_state='pending')
        callback = mock.Mock()
        watcher.run(callback)
        # Since all the units are already pending, the watcher has been
        # properly stopped.
        watch.stop.assert_called_once_with()


class TestLogOnErrors(unittest.TestCase):

    def setUp(self):
        # Set up a mock environment.
        self.env = mock.Mock()

    def test_returned_callable(self):
        # The returned function uses the env to log errors.
        callback = watchers.log_on_errors(self.env)
        self.assertEqual(self.env.log_errors, callback)


class TestExitOnErrors(unittest.TestCase):

    def setUp(self):
        # Set up a mock environment.
        self.env = mock.Mock()

    def test_returned_callable(self):
        # The returned function uses the env to log errors and then exits the
        # application.
        callback = watchers.exit_on_errors(self.env)
        with self.assertRaises(ErrorExit):
            callback('bad wolf')
        self.env.log_errors.assert_called_once_with('bad wolf')


class TestRaiseOnErrors(unittest.TestCase):

    def test_returned_callable(self):
        # The returned function raises the given exception passing the errors.
        callback = watchers.raise_on_errors(ValueError)
        with self.assertRaises(ValueError) as cm:
            callback('bad wolf')
        self.assertEqual('bad wolf', bytes(cm.exception))
