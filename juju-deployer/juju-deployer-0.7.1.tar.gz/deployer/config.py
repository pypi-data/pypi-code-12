from os.path import abspath, isabs, join, dirname

import logging
import os
import tempfile
import shutil
import urllib2
import urlparse


from .deployment import Deployment
from .utils import ErrorExit, yaml_load, path_exists, dict_merge


class ConfigStack(object):

    log = logging.getLogger("deployer.config")

    def __init__(self, config_files, cli_series=None):
        self.config_files = config_files
        self.cli_series = cli_series
        self.version = 3
        self.data = {}
        self.yaml = {}
        self.include_dirs = []
        self.urlopen = urllib2.urlopen
        self.load()

    def _yaml_load(self, config_file):
        if config_file in self.yaml:
            return self.yaml[config_file]

        if urlparse.urlparse(config_file).scheme:
            response = self.urlopen(config_file)
            if response.getcode() == 200:
                temp = tempfile.NamedTemporaryFile(delete=True)
                shutil.copyfileobj(response, temp)
                temp.flush()
                config_file = temp.name
            else:
                self.log.warning("Could not retrieve %s", config_file)
                raise ErrorExit()

        with open(config_file) as fh:
            try:
                yaml_result = yaml_load(fh.read())
            except Exception, e:
                self.log.warning(
                    "Couldn't load config file @ %r, error: %s:%s",
                    config_file, type(e), e)
                raise

        # Check if this is a v4 bundle.
        services = yaml_result.get('services')
        if isinstance(services, dict) and 'services' not in services:
            self.version = 4
            yaml_result = {config_file: yaml_result}

        self.yaml[config_file] = yaml_result

        return self.yaml[config_file]

    def keys(self):
        return sorted(self.data)

    def get(self, key):
        if key not in self.data:
            self.log.warning("Deployment %r not found. Available %s",
                             key, ", ".join(self.keys()))
            raise ErrorExit()
        deploy_data = self.data[key]
        if self.version < 4:
            deploy_data = self._resolve_inherited(deploy_data)
        if self.cli_series:
            deploy_data['series'] = self.cli_series
        return Deployment(
            key, deploy_data, self.include_dirs,
            repo_path=os.environ.get("JUJU_REPOSITORY", ""),
            version=self.version)

    def load(self):
        data = {}
        include_dirs = []
        for fp in self._resolve_included():
            if path_exists(fp):
                include_dirs.append(dirname(abspath(fp)))
            d = self._yaml_load(fp)
            data = dict_merge(data, d)
        self.data = data
        for k in ['include-config', 'include-configs']:
            if k in self.data:
                self.data.pop(k)
        self.include_dirs = include_dirs

    def _inherits(self, d):
        parents = d.get('inherits', ())
        if isinstance(parents, basestring):
            parents = [parents]
        return parents

    def _resolve_inherited(self, deploy_data):
        if 'inherits' not in deploy_data:
            return deploy_data
        inherits = parents = self._inherits(deploy_data)
        for parent_name in parents:
            parent = self.get(parent_name)
            inherits.extend(self._inherits(parent.data))
            deploy_data = dict_merge(parent.data, deploy_data)

        deploy_data['inherits'] = inherits
        return deploy_data

    def _includes(self, config_file):
        files = [config_file]
        d = self._yaml_load(config_file)

        incs = d.get('include-configs') or d.get('include-config')
        if isinstance(incs, basestring):
            inc_fs = [incs]
        else:
            inc_fs = incs

        if inc_fs:
            for inc_f in inc_fs:
                if not isabs(inc_f):
                    inc_f = join(dirname(config_file), inc_f)
                files.extend(self._includes(inc_f))

        return files

    def _resolve_included(self):
        files = []
        [files.extend(self._includes(cf)) for cf in self.config_files]
        return files
