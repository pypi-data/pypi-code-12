class SimpleFS:
    def exists(self, file_name):
        """
        Check whether a file exists in the file system
        :param file_name: the name of the file
        :return: true if the file exists, false otherwise
        """
        raise NotImplementedError

    def save(self, source_file, dest_name):
        """
        Save a file to the file system
        :param source_file: the source file
        :param dest_name: the destination name
¬        """
        raise NotImplementedError

    @staticmethod
    def from_config(config):
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
            return S3FS(bucket_name, credentials)

        try:
            method = config['method'].lower()
        except KeyError:
            raise Exception('Please specify the key "method" in the config')

        if method == 's3':
            return s3_from_config(config)
        elif method == 'local':
            return LocalFS()
        else:
            raise Exception('Method "{}" not known'.format(method))
