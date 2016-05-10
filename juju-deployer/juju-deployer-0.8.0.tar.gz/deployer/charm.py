from __future__ import absolute_import
import logging
import os
import shutil

from six.moves.urllib.request import urlopen

from .vcs import Git, Bzr
from .utils import (
    _check_call,
    _get_juju_home,
    extract_zip,
    get_qualified_charm_url,
    path_join,
    path_exists,
    STORE_URL,
    temp_file,
    yaml_load,
    get_juju_major_version,
)


class Charm(object):

    log = logging.getLogger('deployer.charm')

    def __init__(
            self, name, path, branch, rev, build, charm_url="", data=None):
        self.name = name
        self._path = path
        self.branch = branch
        self.rev = rev
        self._charm_url = charm_url
        self._build = build
        self.vcs = self.get_vcs()
        self.data = data or {}

    def is_git_branch(self):
        return self.branch.startswith('git') or \
            self.branch.find("review.openstack.org") != -1 or \
            "github.com" in self.branch or \
            "git.launchpad.net" in self.branch or \
            os.path.exists(os.path.join(self.branch, '.git'))

    def get_vcs(self):
        if not self.branch:
            return None

        if self.is_git_branch():
            return Git(self.path, self.branch, self.log)
        elif self.branch.startswith("bzr") or self.branch.startswith('lp:') \
                or os.path.exists(os.path.join(self.branch, '.bzr')) \
                or self.branch.startswith('file:'):
            return Bzr(self.path, self.branch, self.log)
        raise ValueError(
            "Could not determine vcs backend for %s" % self.branch)

    @classmethod
    def from_service(cls, name, repo_path, deploy_series, data):
        """
        name: service name
        data['charm']: charm name or store charm url
        data['charm_url'] store charm url
        """
        branch, rev, series = None, None, None
        charm_branch = data.get('branch')
        if charm_branch is not None:
            branch, sep, rev = charm_branch.partition('@')

        charm_path, store_url, build = None, None, None
        name = data.get('charm', name)
        if name.startswith('cs:'):
            store_url = name
        elif name.startswith('local:'):
            # Support vcs charms specifying their
            parts = name[len('local:'):].split('/')
            if len(parts) == 2:
                series, name = parts
            elif data.get('series'):
                series = data['series']
                name = parts.pop()
            else:
                series = deploy_series
            charm_path = path_join(repo_path, series, name)
        elif os.path.isabs(name):
            # charm points to an absolute local path
            charm_path = name.rstrip(os.path.sep)
        elif 'series' in data:
            series = data['series']
            charm_path = path_join(repo_path, series, name)
        else:
            charm_path = path_join(repo_path, deploy_series, name)

        if not store_url:
            store_url = data.get('charm_url', None)

        if store_url and branch:
            cls.log.error(
                "Service: %s has both charm url: %s and branch: %s specified",
                name, store_url, branch)
        if not store_url:
            build = data.get('build', '')

        return cls(name, charm_path, branch, rev, build, store_url, data)

    def is_absolute(self):
        """Charm config points to an absolute path on disk.

        """
        return os.path.isabs(self.name)

    @property
    def repo_path(self):
        """The Juju repository path in which this charm resides.

        For most charms this returns None, leaving the repo path to be
        determined by the Deployment that deploys the charm.

        For charms at an absolute path, however, the repo path is by
        definition the directory two levels up from the charm. (And the
        series directory is one level up.) This allows us to deploy
        charms from anywhere on the filesystem without first gathering them
        under one repository path.

        """
        if self.is_absolute():
            d = os.path.dirname
            return d(d(self.path))
        return None

    def is_local(self):
        if self._charm_url:
            if self._charm_url.startswith('cs:'):
                return False
        return True

    def exists(self):
        return self.is_local() and path_exists(self.path)

    def is_subordinate(self):
        return self.metadata.get('subordinate', False)

    @property
    def charm_url(self):
        if self._charm_url:
            return self._charm_url
        if get_juju_major_version() > 1:
            return self.path
        series = os.path.basename(os.path.dirname(self.path))
        charm_name = self.metadata['name']
        return "local:%s/%s" % (series, charm_name)

    def build(self):
        if not self._build:
            return
        self.log.debug("Building charm %s with %s", self.path, self._build)
        _check_call([self._build], self.log,
                    "Charm build failed %s @ %s", self._build, self.path,
                    cwd=self.path, shell=True)

    def fetch(self):
        if self._charm_url:
            self._fetch_store_charm()
            return
        elif self.is_absolute():
            return
        elif not self.branch:
            self.log.warning("Invalid charm specification %s", self.name)
            return
        self.log.debug(" Branching charm %s @ %s", self.branch, self.path)
        self.vcs.branch()
        if self.rev:
            self.vcs.update(self.rev)
        self.build()

    @property
    def path(self):
        if not self.is_local() and not self._path:
            self._path = self._get_charm_store_cache()
        return self._path

    @property
    def series(self):
        if self.data.get('series'):
            return self.data.get('series')
        metadata_series = self.metadata.get('series')
        if metadata_series:
            return metadata_series[0]
        if self.series_path:
            return os.path.basename(self.series_path)
        return None

    @property
    def series_path(self):
        if not self.is_local():
            return None
        return os.path.dirname(self.path)

    def _fetch_store_charm(self, update=False):
        cache_dir = self._get_charm_store_cache()
        self.log.debug("Cache dir %s", cache_dir)

        if os.path.exists(cache_dir) and not update:
            return

        qualified_url = get_qualified_charm_url(self.charm_url)

        self.log.debug("Retrieving store charm %s" % qualified_url)

        if update and os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)

        store_url = "%s/charm/%s" % (STORE_URL, qualified_url[3:])
        with temp_file() as fh:
            ufh = urlopen(store_url)
            shutil.copyfileobj(ufh, fh)
            fh.flush()
            extract_zip(fh.name, self.path)
        self.config

    def _get_charm_store_cache(self):
        assert not self.is_local(), "Attempt to get store charm for local"
        # Cache
        jhome = _get_juju_home()
        cache_dir = os.path.join(jhome, ".deployer-store-cache")
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        return os.path.join(
            cache_dir,
            self.charm_url.replace(':', '_').replace("/", "_"))

    def update(self, build=False):
        if not self.branch:
            return
        assert self.exists()
        self.log.debug(" Updating charm %s from %s", self.path, self.branch)
        self.vcs.update(self.rev)
        if build:
            self.build()

    def is_modified(self):
        if not self.branch:
            return False
        return self.vcs.is_modified()

    @property
    def config(self):
        config_path = path_join(self.path, "config.yaml")
        if not path_exists(config_path):
            return {}

        with open(config_path) as fh:
            return yaml_load(fh.read()).get('options', {})

    @property
    def metadata(self):
        md_path = path_join(self.path, "metadata.yaml")
        if not path_exists(md_path):
            if not path_exists(self.path):
                raise RuntimeError("No charm metadata @ %s", md_path)
        with open(md_path) as fh:
            return yaml_load(fh.read())

    def get_provides(self):
        p = {'juju-info': [{'name': 'juju-info'}]}
        for key, value in self.metadata['provides'].items():
            value['name'] = key
            p.setdefault(value['interface'], []).append(value)
        return p

    def get_requires(self):
        r = {}
        for key, value in self.metadata['requires'].items():
            value['name'] = key
            r.setdefault(value['interface'], []).append(value)
        return r
