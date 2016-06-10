import config
from exception import GitoException

def wunderlist_validation():
    cf = config.Config()
    if not cf.config_exists():
        raise GitoException("Config file missing")
    config_data = cf.get_config()
    if not 'wl_access_token' in config_data:
        raise GitoException("Wunderlist AccessToken not specified in config file")