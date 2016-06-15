# Copyright 2016 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from testtools.testcase import TestCase

from daemonfixture.daemon import DaemonFixture


class DaemonFixtureTest(TestCase):

    def test_start_and_stop(self):
        """
        The daemon process is started and stopped at setup/cleanup time.
        """
        fixture = DaemonFixture(["/bin/cat"])
        fixture.setUp()
        self.assertTrue(fixture.is_running())
        fixture.cleanUp()
        self.assertFalse(fixture.is_running())

    def test_is_ready(self):
        """
        The setup doesn't complete until the is_ready() callable returns True,
        and the cleanup doesn't complete until the is_ready() callable returns
        False.
        """
        probes = [False, True, True, False]
        fixture = DaemonFixture(["/bin/cat"], is_ready=probes.pop)
        fixture.setUp()
        self.assertEqual([False, True], probes)
        fixture.cleanUp()
        self.assertEqual([], probes)

    def test_kill(self):
        """
        The kill() method terminates the daemon process immediately.
        """
        fixture = DaemonFixture(["/bin/cat"])
        fixture.setUp()
        fixture.kill()
        self.assertFalse(fixture.is_running())
        fixture.cleanUp()
        self.assertFalse(fixture.is_running())

    def test_timeout(self):
        """
        If is_ready() is passed and doesn't return True within the given
        timeout, the process is killed and an exception is raised.
        """
        fixture = DaemonFixture(
            ["/bin/cat"], is_ready=lambda: False, timeout=0.5)
        self.assertRaises(Exception, fixture.setUp)
        self.assertFalse(fixture.is_running())

    def test_wb_details(self):
        """
        If the fixture fails to stop, details about the standard output
        are added.
        """
        probes = [True, True, True, True, True, True, False]
        fixture = DaemonFixture(
            ["/usr/bin/yes"], is_ready=probes.pop, timeout=0.5)
        fixture.setUp()
        self.assertRaises(Exception, fixture._stop)
        details = fixture.getDetails()
        content = details["yes-out"]
        self.assertTrue(content.as_text().startswith("y\n"))
