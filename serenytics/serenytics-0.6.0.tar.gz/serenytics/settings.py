import os


def load_environment_variable(key, default=None):
    """
    Retrieves env vars and makes Python boolean replacements
    """
    val = os.getenv(key, default)
    if isinstance(val, str) and val.lower() == 'true':
        return True
    elif isinstance(val, str) and val.lower() == 'false':
        return False
    return val


SERENYTICS_API_DOMAIN = load_environment_variable('SERENYTICS_API_DOMAIN', 'https://api.serenytics.com')
