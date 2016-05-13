import os
import ast

__author__ = 'Matteo Danieli'


def load_env(print_vars=False):
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
                if key.startswith('#'):
                    continue
                if key not in os.environ:
                    if value.startswith('"') and value.endswith('"') or \
                                    value.startswith("'") and value.endswith("'"):
                        os.environ[key] = ast.literal_eval(value)
                    else:
                        os.environ[key] = value
                    if print_vars:
                        print key, os.environ[key]
    except IOError:
        pass
