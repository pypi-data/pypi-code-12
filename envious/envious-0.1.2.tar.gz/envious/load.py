import os

__author__ = 'Matteo Danieli'


def load_env():
    """Load environment variables from a .env file, if present.

    If an .env file is found in the working directory, and the listed
    environment variables are not already set, they will be set according to
    the values listed in the file.
    """
    env_file = os.environ.get('ENV_FILE', '.env')
    try:
        variables = open(env_file).read().splitlines()
        for v in variables:
            if '=' in v:
                key, value = v.split('=', 1)
                if not key in os.environ:
                    os.environ[key] = value
    except IOError:
        pass
