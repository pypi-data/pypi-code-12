import json
import logging
import os


def _get_default_config_filename():
    """
    Returns the path of the default Kerb-STS configuration file.
    This is the path that Kerb will look for configuration and
    the location it will write configuration to when the --configure
    parameter is passed in.
    """
    return os.path.expanduser('~/.kerb-sts/config.json')


class Config:
    """
    The Config object stores connection configuration for
    the tool.
    """
    ADFS_URL_KEY = 'adfs_url'
    REGION_KEY = 'region'

    def __init__(self, adfs_url, region):
        self.adfs_url = adfs_url
        self.region = region

    def save(self, filename=_get_default_config_filename()):
        """
        Serializes the config object into the default config location.
        :param filename: where to save the Config to
        """
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        dictionary = {Config.ADFS_URL_KEY: self.adfs_url, Config.REGION_KEY: self.region}
        with open(filename, 'w') as f:
            json.dump(dictionary, f)
            logging.info("config file saved to {}".format(filename))

    def is_valid(self):
        """
        Validates that the Config object is valid (non-null non-empty values).
        :return: True if the Config is valid
        """
        return (self.adfs_url is not None and self.adfs_url is not '' and
                self.region is not None and self.region is not '')

    @staticmethod
    def load(filename=_get_default_config_filename()):
        """
        A factory method for returning a Config object
        that has been deserialized from the given filename.
        :param filename: the path to the config file
        :return: a Config object constructed from the filename's contents
        """
        config = Config(adfs_url='', region='')
        try:
            with open(filename) as f:
                config_json = json.loads(f.read())
                if config_json:
                    if Config.ADFS_URL_KEY in config_json:
                        config.adfs_url = str(config_json[Config.ADFS_URL_KEY])

                    if Config.REGION_KEY in config_json:
                        config.region = str(config_json[Config.REGION_KEY])
        except IOError:
            logging.warning("could not read config file {}".format(filename))
        return config
