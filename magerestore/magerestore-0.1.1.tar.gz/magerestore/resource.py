import subprocess
import zipfile
import os

class ResourceManager:
    def __init__(self, resource_config, repo_manager):
        self.resource_config = resource_config
        self.repo_manager = repo_manager
        self.resources = dict()
        self.factory = ResourceFactory(self)

    def get_resource(self, name):
        if name not in self.resources:
            self.resources[name] = self.factory.create(self.resource_config[name])

        return self.resources[name]

    def get_repo(self, repo_name):
        return self.repo_manager.get_repo(repo_name)

    def names(self):
        """Get list of resource names"""
        return sorted([name for name in self.resource_config])


class ResourceFactory:
    def __init__(self, resource_manager):
        self.types = dict()
        self.manager = resource_manager

    def add_type(self, name, type_class):
        self.types[name] = type_class

    def create(self, node):
        node_type = node['type']

        if node_type not in self.types:
            raise KeyError('No resource class defined for node type `{type}`'.format(type=node_type))

        type_class = self.types[node_type]

        return type_class(node, self.manager)


class MagentoDatabaseResource:
    def __init__(self, config, resource_manager):
        self.manager = resource_manager
        self.repository = resource_manager.get_repo(config['repository'])
        self.temp_file = None

        self.compression = None
        self.path = None
        self.parse_config(config)

    def parse_config(self, config):
        if 'path' in config:
            self.path = config['path']

        if 'compression' in config:
            self.compression = config['compression']

    def pre_check(self):
        pass

    def get_file(self, progress_callback=None):
        self.temp_file = self.repository.get_file(self.path, progress_callback)

    def unpack(self):
        options = ['--drop']

        # determine if compression is used
        if self.compression:
            options.append('--compression=' + self.compression)

        cmd = ['n98-magerun.phar', 'db:import'] + options + ['--', self.temp_file.name]
        subprocess.call(cmd)  # use .call since this shows the progress bar output correctly
        """
        running the db:import with PV installed makes the terminal ignore newlines. Subject to further investigation.
        """
        subprocess.call(['stty', 'sane'])


class MagentoMediaResource:
    def __init__(self, config, resource_manager):
        self.manager = resource_manager
        self.repository = resource_manager.get_repo(config['repository'])
        self.temp_file = None
        self.path = None

        self.parse_config(config)

    def pre_check(self):
        if not os.path.isdir('media'):
            raise FileNotFoundError('Media folder does not exist in current directory (%s) ' % os.getcwd())

    def parse_config(self, config):
        if 'path' in config:
            self.path = config['path']

    def get_file(self, progress_callback=None):
        self.temp_file = self.repository.get_file(self.path, progress_callback)

    def unpack(self):
        with zipfile.ZipFile(self.temp_file) as media_zip:
            media_files = [file for file in media_zip.namelist() if file.startswith("media/")]
            media_zip.extractall(members=media_files)
