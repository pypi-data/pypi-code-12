""" Unittest for juju-deployer diff action (--diff) """
# pylint: disable=C0103
import StringIO
import os
import shutil
import tempfile
import unittest

from deployer.config import ConfigStack
from deployer.env.mem import MemoryEnvironment
from deployer.utils import setup_logging

from .base import Base, skip_if_offline, TEST_OFFLINE, TEST_OFFLINE_REASON
from ..action.diff import Diff


@skip_if_offline
class DiffTest(Base):

    def setUp(self):
        self.output = setup_logging(
            debug=True, verbose=True, stream=StringIO.StringIO())

    # Because fetch_charms is expensive, do it once for all tests
    @classmethod
    def setUpClass(cls):
        super(DiffTest, cls).setUpClass()
        # setUpClass not being skipped, here, could have to do with
        # decorator on derived class.  So skip explicitly.
        if TEST_OFFLINE:
            raise unittest.SkipTest(TEST_OFFLINE_REASON)
        deployment = ConfigStack(
            [os.path.join(
                cls.test_data_dir, "blog.yaml")]).get('wordpress-prod')
        cls._dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(cls._dir, "precise"))
        deployment.repo_path = cls._dir
        deployment.fetch_charms()
        deployment.resolve()
        cls._deployment = deployment

    @classmethod
    def tearDownClass(cls):
        super(DiffTest, cls).tearDownClass()
        # TearDownClass not being skipped, here, could have to do with
        # decorator on derived class.  So skip explicitly.
        if TEST_OFFLINE:
            raise unittest.SkipTest(TEST_OFFLINE_REASON)
        shutil.rmtree(cls._dir)

    @classmethod
    def get_deployment(cls):
        """ Return saved deployment at class initialization
        """
        return cls._deployment

    def test_diff_nil(self):
        dpl = self.get_deployment()
        # No changes, assert nil diff
        env = MemoryEnvironment(dpl.name, dpl)
        diff = Diff(env, dpl, {}).do_diff()
        self.assertEqual(diff, {})

    def test_diff_num_units(self):
        # Removing 1 unit must show -1 'num_units'
        dpl = self.get_deployment()
        env = MemoryEnvironment(dpl.name, dpl)
        env.remove_unit(env.status()['services']['haproxy']['units'][0])
        diff = Diff(env, dpl, {}).do_diff()
        self.assertEqual(
            diff['services']['modified']['haproxy']['num_units'], -1)
        # re-adding a unit -> nil diff
        env.add_units('haproxy', 1)
        diff = Diff(env, dpl, {}).do_diff()
        self.assertEqual(diff, {})

    def test_diff_config(self):
        dpl = self.get_deployment()
        env = MemoryEnvironment(dpl.name, dpl)
        env.set_config('blog', {'tuning': 'bare'})
        diff = Diff(env, dpl, {}).do_diff()
        mod_blog = diff['services']['modified']['blog']
        self.assertTrue(mod_blog['env-config']['tuning'] !=
                        mod_blog['cfg-config']['tuning'])
        self.assertEquals(mod_blog['env-config']['tuning'], 'bare')

    def test_diff_config_many(self):
        dpl = self.get_deployment()
        env = MemoryEnvironment(dpl.name, dpl)
        env.set_config('blog', {'tuning': 'bare', 'engine': 'duck'})
        diff = Diff(env, dpl, {}).do_diff()
        mod_blog = diff['services']['modified']['blog']
        self.assertEqual(
            set(mod_blog['env-config'].keys()),
            set(['tuning', 'engine']))
        self.assertTrue(mod_blog['env-config']['tuning'] !=
                        mod_blog['cfg-config']['tuning'])
        self.assertTrue(mod_blog['env-config']['engine'] !=
                        mod_blog['cfg-config']['engine'])

    def test_diff_constraints(self):
        dpl = self.get_deployment()
        env = MemoryEnvironment(dpl.name, dpl)
        env.set_constraints('haproxy', 'foo=bar')
        diff = Diff(env, dpl, {}).do_diff()
        mod_haproxy = diff['services']['modified']['haproxy']
        self.assertTrue(
            mod_haproxy['env-constraints'] != mod_haproxy['cfg-constraints'])
        self.assertEqual(mod_haproxy['env-constraints'], {'foo': 'bar'})

    def test_diff_service_destroy(self):
        dpl = self.get_deployment()
        env = MemoryEnvironment(dpl.name, dpl)
        env.destroy_service('haproxy')
        diff = Diff(env, dpl, {}).do_diff()
        self.assertTrue(str(diff['relations']['missing'][0]).find('haproxy')
                        != -1)
        self.assertTrue(diff['services']['missing'].keys() == ['haproxy'])
