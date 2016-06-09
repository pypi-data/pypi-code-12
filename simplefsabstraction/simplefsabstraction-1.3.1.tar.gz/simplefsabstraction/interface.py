import uuid


class SimpleFS:
    class BadExtensionError(Exception):
        def __init__(self):
            super().__init__('Extension not allowed')

    def exists(self, file_name):
        """
        Check whether a file exists in the file system
        :param file_name: the name of the file
        :return: true if the file exists, false otherwise
        """
        raise NotImplementedError

    def save(self, source_file, dest_name, randomize=False):
        """
        Save a file to the file system
        :param source_file: the source file
        :param dest_name: the destination name
        :param randomize: use a random file name
        :return the generated filename
        """
        raise NotImplementedError

    @staticmethod
    def _check_extension(filename, extensions):
        """
        Check is a filename has an allowed extension
        :param filename: the filename
        :return: true if allowed extension, false otherwise
        """
        return any(filename.endswith(".{}".format(ext)) for ext in extensions)

    @staticmethod
    def _random_filename():
        """
        Generate a random filename
        """
        return str(uuid.uuid4())

    @staticmethod
    def from_config(config):
        """
        Instantiate a file system abstraction from a configuration dictionary.
        Example:
        {
            'method': 's3',
            'access_key': 'my_access_key',
            'secret_key': 'my_secret_key',
            'bucket_name': 'my_bucket_name'
        }

        or

        {
            'method': 'local',
            'base_path': '/tmp/',
            'allowed_extensions': ['jpg', 'png']
        }
        """
        from simplefsabstraction import S3FS, LocalFS

        def s3_from_config(config):
            """
            Create an instance of S3FS from the config
            """
            if 'access_key' in config and 'secret_key' in config:
                credentials = {'access_key': config['access_key'],
                               'secret_key': config['secret_key']}
            else:
                credentials = None
            try:
                bucket_name = config['bucket_name']
            except KeyError:
                raise Exception('Please specify the bucket name in the config')
            allowed_extensions = config['allowed_extensions'] if 'allowed_extensions' in config else None
            return S3FS(bucket_name, allowed_extensions=allowed_extensions, credentials=credentials)

        def local_from_config(config):
            """
            Create an instance of LocalFS from the config
            """
            allowed_extensions = config['allowed_extensions'] if 'allowed_extensions' in config else None
            if 'base_path' in config:
                return LocalFS(allowed_extensions=allowed_extensions, base_path=config['base_path'])
            else:
                return LocalFS(allowed_extensions=allowed_extensions)

        try:
            method = config['method'].lower()
        except KeyError:
            raise Exception('Please specify the key "method" in the config')

        if method == 's3':
            return s3_from_config(config)
        elif method == 'local':
            return local_from_config(config)
        else:
            raise Exception('Method "{}" not known'.format(method))
