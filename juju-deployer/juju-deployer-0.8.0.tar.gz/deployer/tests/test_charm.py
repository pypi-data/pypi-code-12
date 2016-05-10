from __future__ import absolute_import
import os
import logging
import subprocess

from deployer.charm import Charm
from deployer.utils import ErrorExit, yaml_dump
from deployer.vcs import Bzr as BaseBzr
from deployer.vcs import Git as BaseGit
from .base import Base


class StoreCharmTest(Base):
    def setUp(self):
        self.charm = Charm(
            'cs:trusty/ubuntu', None, None, None, None)

    def test_is_absolute(self):
        self.assertFalse(self.charm.is_absolute())

    def test_repo_path(self):
        self.assertIsNone(self.charm.repo_path)


class AbsolutePathCharmTest(Base):
    def setUp(self):
        self.charm = Charm(
            '/tmp/trusty/ubuntu', '/tmp/trusty/ubuntu', None, None, None)

    def test_is_absolute(self):
        self.assertTrue(self.charm.is_absolute())

    def test_repo_path(self):
        self.assertEqual('/tmp', self.charm.repo_path)


class Bzr(BaseBzr):

    def __init__(self, path):
        super(Bzr, self).__init__(
            path, "", logging.getLogger("deployer.repo"))

    def init(self):
        self._call(
            ["bzr", "init", self.path],
            "Could not initialize repo at  %(path)s")
        try:
            subprocess.check_output(["bzr", "whoami"])
        except subprocess.CalledProcessError:
            subprocess.check_call([
                "bzr", "whoami", "TestRunner <test@example.com>"])

    def write(self, files):
        for f in files:
            with open(os.path.join(
                    self.path, f), 'w') as fh:
                fh.write(files[f])
            self._call(
                ["bzr", "add", f],
                "Could not add file %s" % f)

    def commit(self, msg):
        self._call(
            ["bzr", "commit", "-m", msg],
            "Could not commit at %(path)s")

    def revert(self):
        self._call(
            ["bzr", "revert"],
            "Could not revert at %(path)s")

    def tag(self, name):
        self._call(
            ["bzr", "tag", name],
            "Could not tag at %(path)s")

    branch = update = pull = None


class BzrCharmTest(Base):

    def setUp(self):
        self.repo_path = d = self.mkdir()
        self.series_path = os.path.join(d, "precise")
        os.mkdir(self.series_path)
        self.output = self.capture_logging(
            "deployer.charm", level=logging.DEBUG)

    def setup_vcs_charm(self):
        self.branch = Bzr(self.mkdir())
        self.branch.init()
        self.branch.write(
            {'metadata.yaml': yaml_dump({
                'name': 'couchdb',
                'summary': 'RESTful document oriented database',
                'provides': {
                    'db': {
                        'interface': 'couchdb'}}}),
             'revision': '3'})
        self.branch.commit('initial')
        self.branch.write({'revision': '4'})
        self.branch.commit('next')
        self.branch.tag('v2')
        self.branch.write({'revision': '5'})
        self.branch.commit('next')

        self.charm_data = {
            "charm": "couchdb",
            "build": None,
            "branch": self.branch.path,
            "rev": None,
            "charm_url": None,
        }

    def test_vcs_charm(self):
        self.setup_vcs_charm()
        params = dict(self.charm_data)
        charm = Charm.from_service(
            "scratch", self.repo_path, "precise", params)

        charm.fetch()
        self.assertEqual(charm.metadata['name'],  'couchdb')
        self.assertEqual(charm.vcs.get_cur_rev(), '3')

        charm.rev = '2'
        charm.update()
        self.assertEqual(charm.vcs.get_cur_rev(), '2')

        self.assertFalse(charm.is_modified())
        with open(os.path.join(charm.path, 'revision'), 'w') as fh:
            fh.write('0')
        self.assertTrue(charm.is_modified())
        Bzr(charm.path).revert()

        charm.rev = None
        # Update goes to latest with no revision specified
        charm.update()
        self.assertEqual(charm.vcs.get_cur_rev(), '3')

    def test_vcs_fetch_with_rev(self):
        self.setup_vcs_charm()
        params = dict(self.charm_data)
        params['branch'] = params['branch'] + '@2'
        charm = Charm.from_service(
            "scratch", self.repo_path, "precise", params)
        charm.fetch()
        self.assertEqual(charm.vcs.get_cur_rev(), '2')

    charms_vcs_series = [
        ({"charm": "local:precise/mongodb",
          "branch": "lp:charms/precise/couchdb"},
         'trusty', 'precise/mongodb'),
        ({"series": "trusty",
          "charm": "couchdb",
          "branch": "lp:charms/precise/couchdb"},
         'precise', 'trusty/couchdb')]

    def test_vcs_charm_with_series(self):
        for data, dseries, path in self.charms_vcs_series:
            charm = Charm.from_service(
                "db", "/tmp", dseries, data)
            self.assertEqual(
                charm.path,
                os.path.join('/tmp', path))
            self.assertEqual(
                charm.series_path, os.path.join('/tmp', path.split('/')[0]))

    def test_charm_error(self):
        branch = self.mkdir()
        params = {
            'charm': 'couchdb',
            'branch': "file://%s" % branch}
        charm = Charm.from_service(
            "scratch", self.repo_path, "precise", params)
        self.assertRaises(ErrorExit, charm.fetch)
        self.assertIn('bzr: ERROR: Not a branch: ', self.output.getvalue())


class Git(BaseGit):

    def __init__(self, path):
        super(Git, self).__init__(
            path, "", logging.getLogger("deployer.repo"))

    def init(self):
        self._call(
            ["git", "init", self.path],
            "Could not initialize repo at  %(path)s")

    def write(self, files):
        for f in files:
            with open(os.path.join(
                    self.path, f), 'w') as fh:
                fh.write(files[f])
            self._call(
                ["git", "add", f],
                "Could not add file %s" % f)

    def commit(self, msg):
        self._call(
            ["git", "commit", "-m", msg],
            "Could not commit at %(path)s")

    def revert(self):
        self._call(
            ["git", "reset", "--hard"],
            "Could not revert at %(path)s")

    def tag(self, name):
        self._call(
            ["git", "tag", name],
            "Could not tag at %(path)s")

    branch = update = pull = None


class GitCharmTest(Base):

    def setUp(self):
        self.repo_path = d = self.mkdir()
        self.series_path = os.path.join(d, "precise")
        os.mkdir(self.series_path)
        self.output = self.capture_logging(
            "deployer.charm", level=logging.DEBUG)

    def setup_vcs_charm(self):
        self.branch = Git(self.mkdir())
        self.branch.init()
        self.branch.write(
            {'metadata.yaml': yaml_dump({
                'name': 'couchdb',
                'summary': 'RESTful document oriented database',
                'provides': {
                    'db': {
                        'interface': 'couchdb'}}}),
             'revision': '3'})
        self.branch.commit('initial')
        self.branch.write({'revision': '4'})
        self.branch.commit('next')
        self.branch.tag('v2')
        self.tagged_revision = self.branch.get_cur_rev()
        self.branch.write({'revision': '5'})
        self.branch.commit('next')

        self.charm_data = {
            "charm": "couchdb",
            "build": None,
            "branch": self.branch.path,
            "rev": None,
            "charm_url": None,
        }

    def test_vcs_charm(self):
        self.setup_vcs_charm()
        params = dict(self.charm_data)
        charm = Charm.from_service(
            "scratch", self.repo_path, "precise", params)
        charm.fetch()
        self.assertEqual(charm.metadata['name'],  'couchdb')
        HEAD = charm.vcs.get_cur_rev()

        self.assertFalse(charm.is_modified())
        with open(os.path.join(charm.path, 'revision'), 'w') as fh:
            fh.write('0')
        self.assertTrue(charm.is_modified())
        Git(charm.path).revert()

        charm.rev = None
        # Update goes to latest with no revision specified
        charm.update()
        self.assertEqual(charm.vcs.get_cur_rev(), HEAD)

    def test_vcs_fetch_with_rev(self):
        self.setup_vcs_charm()
        params = dict(self.charm_data)
        rev2 = self.branch._call(
            "git rev-parse HEAD~1".split(),
            self.branch.err_cur_rev,
        )
        params['branch'] = '{}@{}'.format(params['branch'], rev2)
        charm = Charm.from_service(
            "scratch", self.repo_path, "precise", params)
        charm.fetch()
        self.assertEqual(charm.vcs.get_cur_rev(), rev2)

    def test_vcs_fetch_with_tag(self):
        self.setup_vcs_charm()
        params = dict(self.charm_data)
        params['branch'] = '{}@{}'.format(params['branch'], 'v2')
        charm = Charm.from_service(
            "scratch", self.repo_path, "precise", params)
        charm.fetch()
        self.assertEqual(charm.vcs.get_cur_rev(), self.tagged_revision)

    def test_vcs_with_extended_options(self):
        self.setup_vcs_charm()
        params = dict(self.charm_data)
        params['branch'] = \
            "https://review.openstack.org/openstack/charm-ceilometer" + \
            "#changeref=286669/1"

        charm = Charm.from_service(
            "scratch", self.repo_path, "trusty", params)

        self.assertEqual(charm.vcs.extended_options,
                         {'changeref': "286669/1"})

    def test_charm_vcs_unknown(self):
        branch = self.mkdir()
        params = {
            'charm': 'couchdb',
            'branch': "%s" % branch}
        try:
            Charm.from_service(
                "scratch", self.repo_path, "precise", params)
            self.fail("should have failed, vcs ambigious")
        except ValueError as e:
            self.assertIn("Could not determine vcs backend", str(e))
