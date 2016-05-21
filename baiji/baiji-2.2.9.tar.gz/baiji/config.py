import os
from baiji.exceptions import AWSCredentialsMissing

class Credentials(object):
    '''
    Amazon AWS credential object

    If created without an explicit path to the credential file, it will use the environment variable
    ``BODYLABS_CREDENTIAL_FILE``, or if that is not set, default to ``~/.bodylabs``.

    The file is to be a yaml file containing a dict with the keys ``AWS_ACCESS_KEY`` and ``AWS_SECRET``.

    If ``~/.bodylabs`` doesn't exist, we will try to read in the aws cli config file, ``~/.aws/credentials``.

    If the keys are set via environment variables, these will override anything set in a file.

    The credential object makes these availiable as ``o.key`` and ``o.secret``.
    '''
    environment_variable = 'BODYLABS_CREDENTIAL_FILE'
    default_path = '~/.bodylabs'
    aws_cli_path = '~/.aws/credentials'

    def __init__(self):
        self._raw_data = None

    def load(self):
        from baiji.util import yaml
        from baiji.util.environ import getenvpath

        if self._raw_data is not None:
            return self._raw_data

        raw_data = {}

        if os.path.isfile(os.path.expanduser(self.aws_cli_path)):
            import ConfigParser
            aws_cli_config = ConfigParser.ConfigParser()
            aws_cli_config.read([os.path.expanduser(self.aws_cli_path)])
            raw_data.update({
                'AWS_ACCESS_KEY': aws_cli_config.get('default', 'aws_access_key_id'),
                'AWS_SECRET': aws_cli_config.get('default', 'aws_secret_access_key'),
            })

        # If the two files have different keys, `.bodylabs` is used.
        path = getenvpath(self.environment_variable, self.default_path)
        if os.path.isfile(path):
            try:
                bodylabs_data = yaml.load(path)
            except IOError:
                raise AWSCredentialsMissing("Unable to read AWS configuration file: {}".format(path))
            # Don't crash on an empty ~/.bodylabs.
            if bodylabs_data is not None:
                raw_data.update(bodylabs_data)

        if not raw_data:
            raise AWSCredentialsMissing("Unable to read AWS configuration file: {}".format(path))

        self._raw_data = raw_data

        return self._raw_data

    def _try(self, var_list, key):
        for var in var_list:
            val = os.getenv(var, None)
            if val:
                return val
        try:
            return self.load()[key]
        except KeyError:
            raise AWSCredentialsMissing('AWS configuration is missing or ill formed.')

    @property
    def key(self):
        return self._try(['AWS_ACCESS_KEY_ID', 'AWS_ACCESS_KEY'], 'AWS_ACCESS_KEY')
    @property
    def secret(self):
        return self._try(['AWS_SECRET_ACCESS_KEY', 'AWS_SECRET'], 'AWS_SECRET')

credentials = Credentials()

def is_available():
    from baiji.util.reachability import internet_reachable
    try:
        credentials.load()
    except AWSCredentialsMissing:
        return False
    return internet_reachable()
