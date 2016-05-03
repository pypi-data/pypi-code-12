import paramiko
import os
import tempfile


class RepositoryFactory:
    def __init__(self):
        self.types = dict()

    def add_type(self, name, repository_cls):
        self.types[name] = repository_cls

    def create(self, config):
        repo_type = config['type']
        if repo_type not in self.types:
            raise KeyError("Not a valid repository type: `{type}`".format(type=repo_type))

        return self.types[repo_type](**config)


class RepositoryManager:
    def __init__(self, repo_config):
        self.repo_config = repo_config
        self.repositories = {}
        self.factory = RepositoryFactory()

    def get_repo(self, repo_name):
        if repo_name not in self.repositories:
            self.repositories[repo_name] = self.factory.create(self.repo_config[repo_name])

        return self.repositories[repo_name]


class SFTPRepository:
    def __init__(self, host=None, port=None, user=None, password=None, description=None, type=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.description = description
        self.type = type
        self.ssh_config_file = os.path.expanduser('~/.ssh/config')

    def get_file(self, remote_file, progress_callback=None):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_config = paramiko.SSHConfig()
        if os.path.exists(self.ssh_config_file):
            with open(self.ssh_config_file) as ssh_config_file:
                ssh_config.parse(ssh_config_file)

        connection_config = dict(
            hostname=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
        )

        # mapping between internal config and ssh config files
        user_config_mapping = dict(
            hostname='hostname',
            username='user',
            port='port',
            key_filename='identityfile'
        )

        user_config = ssh_config.lookup(self.host)

        for connection_name, user_name in user_config_mapping.items():
            if user_name in user_config:
                connection_config[connection_name] = user_config[user_name]

        # strip keys with None as value to fall back on defaults in paramiko
        empty_keys = [key for key, value in connection_config.items() if value is None]
        for key in empty_keys:
            del connection_config[key]

        try:
            ssh.connect(**connection_config)
        except Exception as e:
            raise RepositoryConnectionError(connection_config, e)
        sftp = ssh.open_sftp()
        temp_file = self.get_temp_file()
        sftp.get(remote_file, temp_file.name, progress_callback)

        # ensure contents are written to disk
        temp_file.flush()
        os.fsync(temp_file)

        return temp_file

    def get_temp_file(self):
        return tempfile.NamedTemporaryFile(delete=False)


class RepositoryConnectionError(Exception):
    def __init__(self, connection_info, original_exception):
        self.connection_info = connection_info
        self.original_exception = original_exception

    def __str__(self):
        return "Unable to connect to repository: " + self.original_exception.__str__()
