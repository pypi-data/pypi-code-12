from __future__ import absolute_import
import logging
import os
import time
import sys
import unittest

from deployer.env.go import GoEnvironment

from .base import Base


# Takes roughly about 6m on core2 + ssd, mostly cloudinit time
@unittest.skipIf(
    (not bool(os.environ.get("TEST_ENDPOINT"))),
    "Test env must be defined: TEST_ENDPOINT")
class LiveEnvironmentTest(Base):

    @classmethod
    def setUpClass(cls):
        """Base class sets JUJU_HOME to a new tmp dir, but for these
        tests we need a real JUJU_HOME so that calls to
        ``juju api-endpoints`` work properly.

        """
        if not os.environ.get('JUJU_HOME'):
            raise RuntimeError('JUJU_HOME must be set')

    @classmethod
    def tearDownClass(cls):
        """Base class deletes the tmp JUJU_HOME dir it created.
        Override so we don't delete our real JUJU_HOME!

        """
        pass

    def setUp(self):
        self.endpoint = os.environ.get("TEST_ENDPOINT")
        self.output = self.capture_logging(
            "deployer", log_file=sys.stderr, level=logging.DEBUG)
        self.env = GoEnvironment(
            os.environ.get("JUJU_ENV"), endpoint=self.endpoint)
        self.env.connect()
        status = self.env.status()
        self.assertFalse(status.get('services'))
        # Destroy everything.. consistent baseline
        self.env.reset(
            terminate_machines=len(list(status['machines'].keys())) > 1,
            terminate_delay=240)

    def tearDown(self):
        self.env.reset(
            terminate_machines=True, terminate_delay=240,
            force_terminate=True)
        self.env.close()

    def test_env(self):
        status = self.env.status()
        self.env.deploy("test-blog", "cs:precise/wordpress")
        self.env.deploy("test-db", "cs:precise/mysql")
        self.env.add_relation("test-db", "test-blog")
        self.env.add_units('test-blog', 1)

        # Sleep because juju core watches are eventually consistent (5s window)
        # and status rpc is broken (http://pad.lv/1203105)
        time.sleep(6)
        self.env.wait_for_units(timeout=800)
        status = self.env.status()

        services = ["test-blog", "test-db"]
        self.assertEqual(
            sorted(status['services'].keys()),
            services)
        for s in services:
            for k, u in status['services'][s]['units'].items():
                try:
                    self.assertIn(u['agent-state'],
                                  ("allocating", "pending", "started"))
                except KeyError:
                    self.assertIn(u['jujustatus']['Current'],
                                  ("allocating", "idle"))

    def test_add_machine(self):
        machine_name = self.env.add_machine()

        # Sleep because juju core watches are eventually consistent (5s window)
        # and status rpc is broken (http://pad.lv/1203105)
        time.sleep(6)
        status = self.env.status()

        self.assertIn(machine_name, status['machines'])

    def test_set_annotation(self):
        machine_name = self.env.add_machine()
        self.env.set_annotation(
            machine_name, {'foo': 'bar'}, entity_type='machine')

        # Sleep because juju core watches are eventually consistent (5s window)
        # and status rpc is broken (http://pad.lv/1203105)
        time.sleep(6)
        self.env.status()

        self.assertIn('foo', self.env.client.get_annotation(
            machine_name, 'machine')['Annotations'])
