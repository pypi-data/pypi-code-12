# -*- coding: utf-8 -*-
try:
    import configparser
except:
    from six.moves import configparser

class AdvertiserReport(object):
    def __init__(self, config_filename):
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(config_filename)
        self.api_key = self.config_parser.get('main', 'api_key')
